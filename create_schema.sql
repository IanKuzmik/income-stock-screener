CREATE DATABASE  IF NOT EXISTS `my_schema`;
USE `my_schema`;
-- MySQL dump 10.13  Distrib 8.0.33
--
-- ------------------------------------------------------
-- Server version	8.0.33

--
-- Table structure for table `sectors`
--

DROP TABLE IF EXISTS `sectors`;

CREATE TABLE `sectors` (
  `id` int NOT NULL,
  `sector` varchar(45) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `sectors` VALUES 
  (0,'TECHNOLOGY'),
  (1,'UTILITIES'),
  (2,'REALESTATE'),
  (3,'FINANCIALS'),
  (4,'CONSUMERGOODS'),
  (5,'HEALTHCARE'),
  (6,'ENERGY')
;

--
-- Table structure for table `transactions`
--

DROP TABLE IF EXISTS `transactions`;

CREATE TABLE `transactions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `symbol` varchar(10) NOT NULL,
  `price` decimal(10,2) NOT NULL,
  `sector` int DEFAULT NULL,
  `dividend_yield` decimal(20,4) DEFAULT NULL,
  `options_ratio` decimal(25,20) DEFAULT NULL,
  `beta` decimal(10,4) DEFAULT NULL,
  `date` datetime NOT NULL,
  `cost` decimal(10,2) NOT NULL,
  `shares` decimal(12,6) DEFAULT NULL,
  `notes` varchar(450) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

