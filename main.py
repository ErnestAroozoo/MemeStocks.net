import streamlit as st
import streamlit.components.v1 as components
import reddit_scraper
import yahoo_finance
import time

# Page config
st.set_page_config(
    page_title="MemeStocks.net - Stock sentiment analytical tool",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'http://memestocks.net',
        'Report a bug': "http://memestocks.net",
        'About': "MemeStocks.net is a tool that scrapes Reddit for the number of stock mentions"
    }
)

# Remove Streamlit hamburger menu
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: visible;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Change Streamlit footer
footer = """<style>
a:link , a:visited{
color: blue;
background-color: transparent;
text-decoration: underline;
}

a:hover,  a:active {
color: red;
background-color: transparent;
text-decoration: underline;
}

.footer {
position: fixed;
left: 0;
bottom: 0;
width: 100%;
background-color: #212121;
color: white;
text-align: center;
}
</style>
<div class="footer">
<p>Made by Ernest Aroozoo</p>
</div>
"""
st.markdown(footer, unsafe_allow_html=True)

# Remove Streamlit top margin
hide_streamlit_style = """
<style>
    #root > div:nth-child(1) > div > div > div > div > section > div {padding-top: 0rem;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Remove Streamlit top decoration bar
hide_decoration_bar_style = '''
    <style>
        header {visibility: hidden;}
    </style>
'''
st.markdown(hide_decoration_bar_style, unsafe_allow_html=True)

# Hide anchor link
st.markdown("""
    <style>
    .css-15zrgzn {display: none}
    </style>
    """, unsafe_allow_html=True)

# Title of the web app
st.title("MemeStocks.net")


# Function to display stock information
def stock_info():
    col1, col2 = st.columns(2)

    progress_bar = st.progress(0)
    progress_bar.progress(0)

    stock_data = yahoo_finance.get_info(search_input)  # Retrieves dictionary object with info

    with col1:
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

    with col2:
        stock_currency = stock_data['currency']
        stock_price = "$" + str(stock_data['regularMarketPrice'])
        st.metric(label="Stock Price", value=stock_price)
        progress_bar.progress(80)

        stock_mentions = reddit_scraper.stock_mentions(search_input, subreddit_input, 1)
        st.metric(label="Number of Posts (Today)", value=stock_mentions)

        progress_bar.progress(100)
        time.sleep(1)
        progress_bar.empty()


# Function to display TradingView chart
def stock_chart():
    with st.container():
        components.html(
            """
    <!-- TradingView Widget BEGIN -->
    <div class="tradingview-widget-container">
      <div id="tradingview_c45b8"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">
      new TradingView.widget(
      {
      "width": 1000,
      "height": 500,
      "symbol":""" "\"" + str(search_input) + "\"" + """,
          "interval": "D",
          "timezone": "exchange",
          "theme": "dark",
          "style": "1",
          "locale": "en",
          "toolbar_bg": "#f1f3f6",
          "enable_publishing": false,
          "hide_top_toolbar": true,
          "save_image": false,
          "container_id": "tradingview_c45b8"
        }
          );
          </script>
        </div>
        <!-- TradingView Widget END -->
                """, height=500, scrolling=False
        )


# Search input
search_input = st.text_input('Stock Ticker', '', max_chars=10, key=str, placeholder='Type a stock ticker (e.g. "AAPL")')
subreddit_input = st.selectbox('Subreddit', ('WallStreetBets', 'Stocks', 'Investing'))

# Display information if stock exists
with st.spinner("Please wait... Retrieving data from" + " " + "r/" + subreddit_input):
    if search_input != '' and yahoo_finance.stock_exists(search_input) is True:
        stock_info()
        stock_chart()

    # Return error message if stock does not exist
    elif search_input != '' and yahoo_finance.stock_exists(search_input) is False:
        st.error('Error: Invalid stock symbol. Try a valid stock symbol such as "AAPL".')
