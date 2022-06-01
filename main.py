# Streamlit for frontend
import streamlit as st
import yahoo_finance
import reddit_scraper

st.set_page_config(
    page_title="MemeStocks.net",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://memestocks.net',
        'Report a bug': "https://memestocks.net",
        'About': "MemeStocks.net is a tool that scrapes Reddit for the number of stock mentions"
    }
)


# Display metrics for the chosen stock
def stock_info():
    st.metric(label="Stock Name", value=yahoo_finance.get_name(search_input))
    stock_price = yahoo_finance.get_price(search_input)
    st.metric(label="Stock Price", value=stock_price)
    st.metric(label="Today's Number of Mentions", value=reddit_scraper.stock_mentions(str(search_input)))


# Title of the web app
st.title("MemeStocks.net")

# Search input
st.header('')
search_input = st.text_input('Stock Ticker', '', max_chars=10, placeholder='Type a stock ticker (e.g. "AAPL")')

# Check if inputted stock ticker exists
if search_input != '' and yahoo_finance.stock_exists(search_input) is True:
    stock_info()
elif search_input != '' and yahoo_finance.stock_exists(search_input) is False:
    st.error('Error: Invalid stock symbol. Try a valid stock symbol such as "AAPL".')

