import psycopg2
import streamlit as st
import streamlit.components.v1 as components
import reddit_scraper
import yahoo_finance
import time
import csv
import pandas as pd

# Heroku PostgreSQL Database
con = psycopg2.connect(
    host="ec2-52-207-15-147.compute-1.amazonaws.com",
    database="db02648v92l1c3",
    user="vyodltuwdpfjsh",
    password="c4edb887115a1cf4a665e02aba475d16b115154bff6b49615936a38b416bac47"
)
cur = con.cursor()

# Stock Tickers CSV Database
with open('stock_tickers.csv', newline='') as f:
    reader = csv.reader(f)
    data = list(reader)
whitelist = []
for stock_info in data:
    whitelist.append(stock_info[0])

# CUSTOMIZATION: Page config
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

# CUSTOMIZATION: Change Streamlit footer
add_footer_style = """<style>
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
st.markdown(add_footer_style, unsafe_allow_html=True)

# CUSTOMIZATION: Remove Streamlit components
hide_menu_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_menu_style, unsafe_allow_html=True)

# CUSTOMIZATION: Remove Streamlit top margin
hide_margin_style = """
<style>
    #root > div:nth-child(1) > div > div > div > div > section > div {padding-top: 0rem;}
</style>
"""
st.markdown(hide_margin_style, unsafe_allow_html=True)

# CUSTOMIZATION: Hide anchor link
hide_anchor_style = """
<style>
    .css-15zrgzn {display: none}
</style>
"""
st.markdown(hide_anchor_style, unsafe_allow_html=True)


# FUNCTION: Display stock information
def stock_info():
    progress_bar.progress(0)

    stock_data = yahoo_finance.get_info(search_input.upper())  # Retrieves dictionary object with info

    st.subheader('Information')

    # Initialize variables to retrieve information on stocks from Yahoo Finance
    try:
        stock_name = stock_data['shortName']
    except:
        stock_name = "N/A"

    try:
        stock_sector = stock_data['sector']
    except:
        stock_sector = "N/A"

    try:
        stock_country = stock_data['country']
    except:
        stock_country = "N/A"

    try:
        stock_price = "$" + str(stock_data['regularMarketPrice'])
    except:
        stock_price = "N/A"

    # Create columns for section 1
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(label="Name", value=stock_name)
        progress_bar.progress(30)

    with col2:
        st.metric(label="Sector", value=stock_sector)
        progress_bar.progress(50)

    with col3:
        st.metric(label="Country", value=stock_country)
        progress_bar.progress(70)

    with col4:
        st.metric(label="Price", value=stock_price)
        progress_bar.progress(80)

    st.markdown("""---""")

    # Create columns for section 2
    with st.container():
        col5, col6 = st.columns([8, 3])

        with col5:
            st.subheader('Price Chart')
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
          "symbol":""" "\"" + str(search_input.upper()) + "\"" + """,
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
                     """, width=1000, height=500, scrolling=False
            )

        with col6:
            st.subheader('Mentions Data')
            cur.execute("SELECT * FROM mentions_posts")
            rows = cur.fetchall()
            data_panda = pd.DataFrame(rows,
                                      columns=['Date', 'Stock Symbol', 'Subreddit', 'Number of Mentions',
                                               'Submission Titles'])
            st.dataframe(data_panda)

        progress_bar.progress(100)
        progress_bar.empty()


# Title of the web app
st.title("📈 MemeStocks.net")

# Search input
search_input = st.text_input('Stock Symbol', '', max_chars=5, key=str,
                             placeholder="Type a valid stock symbol (e.g. 'GME')")
subreddit_input = st.selectbox('Subreddit', ['WallStreetBets'])

# Display information if stock exists
with st.spinner("Please wait... Retrieving data from" + " " + "r/" + subreddit_input + "."):
    if search_input.upper() != '' and search_input.upper() in whitelist:
        progress_bar = st.progress(0)
        stock_info()

    # Return error message if stock does not exist
    elif search_input.upper() != '' and search_input.upper() not in whitelist:
        print(search_input)
        print(whitelist)
        st.error("Error: Invalid stock symbol. Please type a valid stock symbol such as 'AAPL'.")

# CUSTOMIZATION: Change Streamlit footer again to prevent clipping
add_footer_style2 = """<style>
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
st.markdown(add_footer_style2, unsafe_allow_html=True)
