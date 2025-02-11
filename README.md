# Income Stock Screener

### OTM Call Options Strategy
This is a simple proof-of-concept use of [yfinance](https://github.com/ranaroussi/yfinance) to scrape and analyze options data from Yahoo Finance in order to build a portfolio of dividend-bearing stocks. 

__This is not investment advice.__ The math present in the analysis here is arbitrary and not back-tested. 

The basic concept is to, for a given stock, compare the price of out of the money call options expiring in a year to the current price of the stock. Stocks which, in this metric, outperform others in their sector receive a higher score. High-scoring stocks are then compared to the current portfolio stored in a mySql database, and a recommendation is chosen with a regard to balancing sectors in the portfolio. 

The actual transaction is not handled, this program just provides a recommendation, and, if accepted, takes transaction data as input to update the portfolio in the database. 

### Install
In order to use this, you must have [yfinance](https://github.com/ranaroussi/yfinance) and the [Python mySql Connector](https://pypi.org/project/mysql-connector-python/). 

Change the schema name in create_schema.sql from 'my_schema' to whatever you like (my_schema is technically fine), and add the schema name, username and password variables to the top of main.py

Run the create_schema file in your mySql envirornment.

main.py has a STOCKS array variable. This is intentionally left empty; please populate with stocks you would like the program to analyze (along with the relevant sector). Selected stocks should pay dividends and have active options contracts. 

### Use
The intention is to use this program daily/weekly/etc for longer-term investing.

Once set up, just run main.py. Execution time varies, but it usually takes a minute or so for the web scraping to complete. 

The program will then prompt a stock, if you choose to buy it (manually from your chosen broker outside of this program), it will ask you for the cost (default is $5), the actual shares purchased, and any notes (eg, actual price of stock at time of purchase, which will depend on your broker).

The program will add that data to other data gathered from the web scraping and summarize a transaction for you. If you accept, the transaction will be inserted into your database, where it will be used for future analysis. 