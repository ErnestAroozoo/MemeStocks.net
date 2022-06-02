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


# Returns the sector of the stock
def get_sector(stock_ticker):
    ticker = yf.Ticker(str(stock_ticker))
    sector = ticker.info['sector']
    return sector


# Returns the country of the stock
def get_country(dictionary):
    country = dictionary['country']
    return country


# Returns dictionary of stock info
def get_info(stock_ticker):
    ticker = yf.Ticker(str(stock_ticker))
    dictionary = ticker.info
    return dictionary


test_ticker = yf.Ticker("AAaPL")
print(test_ticker.info)
if test_ticker.info['regularMarketPrice'] is None:
    print("Does not exist")
else:
    print("Exists")
