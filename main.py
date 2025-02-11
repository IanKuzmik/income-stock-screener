from collections import Counter
from datetime    import date, datetime
from enum        import Enum

import mysql.connector
import random
import statistics
import yfinance as yf

DATABASE_HOST       = '127.0.0.1'
DATABASE_USER       = ''
DATABASE_PASSWORD   = ''
DATABASE_SCHEMA     = ''
TRANSACTION_TABLE   = 'transactions'
SECTOR_TABLE        = 'sectors'
TRANSACTION_FIELDS  = 'symbol,price,sector,dividend_yield,options_ratio,beta,date,cost,shares,notes'

class Sector(Enum):
    TECHNOLOGY      = 0
    UTILITIES       = 1 
    REALESTATE      = 2
    FINANCIALS      = 3
    CONSUMERGOODS   = 4
    HEALTHCARE      = 5
    ENERGY          = 6

STOCKS = [
    # Example: ('AAPL', Sector.TECHNOLOGY),
]

# DESC: Given a list of expiration dates, get the one closest to a specified value (default 1 year)
# INPUT: {} - A dictionary with 'yyyy-mm-dd' keys and unix miliseconds values, INT - amount of days from today to base selction on
# OUTPUT: INT - unix milliseconds 
def select_expiration(expiration_dates, expires_in = 365):
    deltas = []
    for exp_date in expiration_dates.keys():
        day_delta = int((datetime.strptime(exp_date, "%Y-%m-%d").date() - date.today()).total_seconds() / (60*60*24))
        deltas.append({'exp_date': exp_date, 'exp_delta': abs(day_delta - expires_in)})
    min_delta = min(list(map(lambda x: x['exp_delta'], deltas)))
    min_delta_date = list(filter( lambda x: x['exp_delta'] == min_delta, deltas))[0]['exp_date']
    return expiration_dates[min_delta_date]
    

# DESC: Given a list of options contracts, get a value for investor sentiment 
# INPUT: [] - An array of option contract obejects, FLOAT - current price of underlying stock
# OUTPUT: FLOAT - the higher the number, the more people are expecting the price to rise 
def get_option_ratio(option_contracts, current_price):
    if not option_contracts: return 0
    ratios = []
    for option in option_contracts:
        strike          = option['strike']
        ask             = option['ask']
        open_interest   = option['openInterest']

        strike_ratio            = abs(current_price - strike) / current_price
        ask_ratio               = ask / current_price
        ratio                   = strike_ratio * ask_ratio
        volume_weighted_ratio   = ratio * (1 + (open_interest / 1000000))

        ratios.append(volume_weighted_ratio)
    
    return statistics.mean(ratios)


# DESC: fill info for each stock
# INPUT: TUPLE - (STRING ticker, ENUM Sector)
# OUTPUT: Stock Object
def populate_stock_object(stock):
    symbol                  = stock[0]
    sector                  = stock[1]
    ticker                  = yf.Ticker(symbol)
    current_price           = ticker.info['open']
    beta                    = ticker.info['beta'] if 'beta' in ticker.info else None
    ticker_data             = ticker._download_options()['underlying'] # this also populates the internal dat._expirations attribute
    dividend_yield          = ticker_data['dividendYield'] if 'dividendYield' in ticker_data else None
    option_expiration_dates = ticker._expirations
    options_data            = ticker._download_options(date = select_expiration(option_expiration_dates))
    filtered_options_data   = list(filter(lambda x: not x['inTheMoney'] and 'ask' in x, options_data['calls']))
    ratio                   = get_option_ratio(filtered_options_data, current_price)

    stock_object = {
        'symbol'        : symbol,
        'price'         : current_price,
        'sector'        : sector,
        'dividend_yield': dividend_yield,
        'options_ratio' : ratio,
        'beta'          : beta,
    }

    return stock_object


# INPUT: Array of TUPLEs - (STRING ticker, ENUM Sector)
# OUTPUT: Stock Object Array
def get_stock_data(stocks):
    stock_data = []
    for stock in stocks:
        stock_data.append(populate_stock_object(stock))
    return stock_data

# INPUT: Stock Object Array
# OUTPUT: Stock Object Array
def get_best_ratio_stocks(stocks):
    sorted_by_ratio = sorted(stocks, key=lambda x: x['options_ratio'], reverse=True)
    return sorted_by_ratio[:10]

def connect_to_db():
    try:
        db = mysql.connector.connect(
            host=f'{DATABASE_HOST}',
            user=f'{DATABASE_USER}',       
            password=f'{DATABASE_PASSWORD}', 
            database=f'{DATABASE_SCHEMA}',
        )
    except:
        print('Error: Invalid DB')
        exit() 
    return db

def insert_transaction(db, transaction_object):
    sql = f'INSERT INTO {DATABASE_SCHEMA}.{TRANSACTION_TABLE} ({TRANSACTION_FIELDS}) VALUES ({','.join([str(val) for val in transaction_object.values()])})'
    cur = db.cursor()
    cur.execute(sql)
    db.commit()
    cur.close()

def get_transactions(db, logic = None):
    sql = f'SELECT * FROM {DATABASE_SCHEMA}.{TRANSACTION_TABLE}'

    if logic: sql = f'{sql} {logic}'

    cur = db.cursor()
    cur.execute(sql)
    data = cur.fetchall()
    cur.close()

    return data

# DESC: Find which sectors the portfolio is lacking in
# INPUT: ARRAY -  Transaction Objects
# OUTPUT: INT - sector from Sector enum
def get_rand_sector(portfolio_transactions):
    portfolio_sectors       = list(map(lambda x: x[3], portfolio_transactions))
    portfolio_sector_counts = Counter(portfolio_sectors)
    min_sectors             = [k for k, v in portfolio_sector_counts.items() if v == min(portfolio_sector_counts.values())]
    rand_sector             = random.choice(min_sectors)
    return rand_sector

# DESC: Prompt user to buy stock, and enter in specific transaction details
# INPUT: Database Connection, Stock Object
# OUTPUT: VOID - insert transaction record into database
def buy_stock(db, stock_pick):
    response = input(f'buy {stock_pick['symbol']}? (y/n) ')

    if response == 'y':
        cost    = input(f'enter final cost... ')        or 5.00
        shares  = input(f'enter shares bought...  ')    or 0.0
        notes   = input(f'notes? ')                     or ''
        transaction_object = {
            'symbol'        : f'"{stock_pick['symbol']}"',
            'price'         : stock_pick['price'],
            'sector'        : stock_pick['sector'].value,
            'dividend_yield': stock_pick['dividend_yield'],
            'options_ratio' : stock_pick['options_ratio'],
            'beta'          : stock_pick['beta'],
            'date'          : f'"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"',
            'cost'          : cost,
            'shares'        : shares,
            'notes'         : f'"{notes}"',
        }
        print(transaction_object) 
        finalize = input(f'finish? (y/n) ')
        if finalize != 'n':
            insert_transaction(db,transaction_object)

def init():

    # get best potential stocks
    stock_object_array = get_stock_data(STOCKS)
    best_stocks        = get_best_ratio_stocks(stock_object_array)
    
    DB = connect_to_db()

    # get current portfolio info
    transactions = get_transactions(DB)
    if not transactions: 
        rand_sector = random.choice([k.value for k in Sector])
    else:
        rand_sector = get_rand_sector(transactions)
    
    # pick stock based on best_stocks and portfolio balance
    possible_stocks = list(filter(lambda x: x['sector'].value == rand_sector, best_stocks))
    stock_pick      = random.choice(possible_stocks) if possible_stocks else random.choice(best_stocks)

    # go through manual buy stock process
    buy_stock(DB,stock_pick)  

init()