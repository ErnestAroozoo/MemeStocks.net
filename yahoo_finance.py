# PostgreSQL to store data for stock mentions

import yfinance as yf


# Checks if user inputted a valid stock ticker symbol
def stock_exists(stock_ticker):
    ticker = yf.Ticker(str(stock_ticker))
    if ticker.info['regularMarketPrice'] is None:
        return False
    return True


# Returns the price of the stock
def get_price(stock_ticker):
    ticker = yf.Ticker(str(stock_ticker))
    price = ticker.info['regularMarketPrice']
    return price


# Returns the name of the stock
def get_name(stock_ticker):
    ticker = yf.Ticker(str(stock_ticker))
    name = ticker.info['shortName']
    return name
