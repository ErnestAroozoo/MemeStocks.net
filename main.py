import streamlit as st
import streamlit.components.v1 as components
import reddit_scraper
import yahoo_finance
import time

# Page config
st.set_page_config(
    page_title="MemeStocks.net",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'http://memestocks.net',
        'Report a bug': "http://memestocks.net",
        'About': "MemeStocks.net is a tool that scrapes Reddit for the number of stock mentions"
    }
)

# Title of the web app
st.title("MemeStocks.net")


# Function to display stock information
def stock_info():
    progress_bar = st.progress(0)
    progress_bar.progress(0)

    stock_data = yahoo_finance.get_info(search_input)  # Retrieves dictionary object with info

    stock_name = stock_data['shortName']
    st.metric(label="Stock Name", value=stock_name)
    progress_bar.progress(20)

    try:
        stock_sector = stock_data['sector']
        st.metric(label="Sector", value=stock_sector)
    except:
        pass

    progress_bar.progress(40)

    try:
        stock_country = stock_data['country']
        st.metric(label="Country", value=stock_country)
    except:
        pass

    progress_bar.progress(60)

    stock_currency = stock_data['currency']
    stock_price = "$" + str(stock_data['regularMarketPrice']) + " " + stock_currency
    st.metric(label="Stock Price", value=stock_price)
    progress_bar.progress(80)

    stock_mentions = reddit_scraper.stock_mentions(search_input, subreddit_input)
    st.metric(label="Today's Number of Mentions", value=stock_mentions)

    progress_bar.progress(100)

    time.sleep(3)

    progress_bar.empty()


# Search input
st.header('')
search_input = st.text_input('Stock Ticker', '', max_chars=10, key=str, placeholder='Type a stock ticker (e.g. "AAPL")')
subreddit_input = st.selectbox('Subreddit', ('WallStreetBets', 'Stocks', 'Investing'))

# Display information if stock exists
with st.spinner("Please wait... Retrieving information from" + " " + "r/" + subreddit_input):
    if search_input != '' and yahoo_finance.stock_exists(search_input) is True:
        stock_info()

    # Return error message if stock does not exist
    elif search_input != '' and yahoo_finance.stock_exists(search_input) is False:
        st.error('Error: Invalid stock symbol. Try a valid stock symbol such as "AAPL".')

# Remove Streamlit watermark
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)
