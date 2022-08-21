import psycopg2
import streamlit as st
import streamlit.components.v1 as components
import reddit_scraper
import yahoo_finance
import time
import csv
import pandas as pd
from sqlalchemy import create_engine

# Heroku PostgreSQL Database
con = psycopg2.connect(
    host="ec2-52-207-15-147.compute-1.amazonaws.com",
    database="db02648v92l1c3",
    user="vyodltuwdpfjsh",
    password="c4edb887115a1cf4a665e02aba475d16b115154bff6b49615936a38b416bac47"
)
cur = con.cursor()
db_string = "postgresql://vyodltuwdpfjsh:c4edb887115a1cf4a665e02aba475d16b115154bff6b49615936a38b416bac47@ec2-52-207-15-147.compute-1.amazonaws.com:5432/db02648v92l1c3"
connection = create_engine(db_string, pool_size=20, max_overflow=0).connect()

# Stock Tickers CSV Database
with open('stock_tickers.csv', newline='') as f:
    reader = csv.reader(f)
    data = list(reader)
whitelist = []
stock_name_list = []
for stock_info in data:
    whitelist.append(stock_info[0])
    stock_name_list.append(stock_info[1])

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
    # Create columns for section 1
    col1, col2 = st.columns(2)

    with col1:
        st.subheader('Information')
        st.metric(label="Stock Symbol", value="$" + search_input.upper())
        st.metric(label="Name", value=stock_name_list[whitelist.index(search_input)])

    with col2:
        st.subheader('Mentions Data')
        database_name = search_input.lower()
        # Create Pandas object using data from PostgreSQL
        df = pd.read_sql_table(database_name, connection)
        # Filter columns based on user selection (e.g. subreddit)
        df_filter = df[["date", subreddit_input.lower() + "_posts", subreddit_input.lower() + "_posts_data",
                        subreddit_input.lower() + "_comments", subreddit_input.lower() + "_comments_data"]]
        # Create new table with renamed column titles
        df2 = df_filter.set_axis(['Date', '# of Posts', 'Posts', '# of Comments', 'Comments'], axis=1, inplace=False)
        # Sort data by date
        df2 = df2.sort_values(by='Date', ascending=False)
        # Change date format to YY-MM-DD
        df2["Date"] = pd.to_datetime(df2["Date"]).dt.date
        # Display Pandas table
        st.dataframe(data=df2, height=160, width=1000)

    st.markdown("""---""")

    # Create columns for section 2
    with st.container():
        col3, col4 = st.columns(2)

        with col3:
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
          "width": 700,
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
               "hide_legend": true,
               "save_image": false,
               "container_id": "tradingview_c45b8"
             }
               );
               </script>
             </div>
             <!-- TradingView Widget END -->
                     """, width=700, height=500, scrolling=False
            )

        with col4:
            st.subheader('Sentiment Chart')
            st.caption("Data Unavailable")

    con.close()


# Title of the web app
st.title("📈 MemeStocks.net")

# Search input
search_input = (st.text_input('Stock Symbol', '', max_chars=5, key=str,
                              placeholder="Type a stock symbol and then press enter (e.g. GME)")).strip().upper()
subreddit_input = st.selectbox('Subreddit', ['WallStreetBets'])

# Case 1: Display information if stock exists
if search_input.upper() != '' and search_input.upper() in whitelist:
    stock_info()

# Case 2: Return error message if stock does not exist
elif search_input.upper() != '' and search_input.upper() not in whitelist:
    st.error("Error: Invalid stock symbol. Please type a valid stock symbol (e.g. AAPL).")

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
