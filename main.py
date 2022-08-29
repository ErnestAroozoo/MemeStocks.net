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
    host="containers-us-west-69.railway.app",
    database="railway",
    user="postgres",
    password="A3ZyGuamiu2AZ2z7H1vI",
    port=6898
)
cur = con.cursor()
db_string = "postgresql://postgres:A3ZyGuamiu2AZ2z7H1vI@containers-us-west-69.railway.app:6898/railway"
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
    st.warning(
        "Disclaimer: The data provided should be used for informational purposes only and in no way should be relied upon for financial advice.",
        icon="⚠️")
    # Create columns for section 1

    st.subheader('Information')
    col1, col2 = st.columns(2)

    with col1:
        st.metric(label="Stock Symbol", value="$" + search_input.upper())
        st.metric(label="Name", value=stock_name_list[whitelist.index(search_input)])

    with col2:
        components.html(
            """
        <!-- TradingView Widget BEGIN -->
        <div class="tradingview-widget-container">
          <div id="tradingview_c45b8"></div>
          <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
          <script type="text/javascript">
          new TradingView.widget(
          {
          "autosize": true,
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
                                     """, scrolling=False
        )

    st.markdown("""---""")

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
    st.dataframe(data=df2, height=140, width=3000)

    # Create columns for section 2
    with st.container():
        col3, col4, col5 = st.columns(3)
        with col3:
            st.line_chart(data=df2, x='Date', y='# of Posts', width=1000, height=250, use_container_width=True)
        with col4:
            st.line_chart(data=df2, x='Date', y='# of Comments', width=1000, height=250, use_container_width=True)
        with col5:
            df2["# of Posts & Comments"] = df2["# of Posts"] + df2["# of Comments"]
            st.line_chart(data=df2, x='Date', y='# of Posts & Comments', width=1000, height=250,
                          use_container_width=True)

    con.close()


# Title of the web app
st.title("📈 MemeStocks.net")

# Search input
search_input = (st.text_input('Stock Symbol', '', max_chars=5, key=str,
                              placeholder="Type a stock symbol and then press enter (e.g. GME)")).strip().upper()
subreddit_input = st.selectbox('Subreddit', ['WallStreetBets'])

# Intro tutorial
intro = st.empty()
with intro.container():
    # Info dialogue
    st.info('Welcome to MemeStocks.net! To get started, please type a valid stock symbol in the search bar above and then press enter.', icon="ℹ️")
    # Text body
    st.markdown("""
    ------------
    ### What is MemeStocks.net?
    MemeStocks.net is a web app that keeps track of the number of times a specific stock has been mentioned. After searching for a valid stock symbol above, multiple time series graphs will be generated to display the historical popularity of that stock.
    
    ### How Does It Work?
    Data scraping is performed on a daily basis in order to keep track of the number of times a stock has been mentioned.
    """)
    # Add gif
    col1, col2, col3 = st.columns([20, 45, 20])
    with col2:
        st.image("tutorial.gif")

# Case 1: Display information if stock exists
if search_input.upper() != '' and search_input.upper() in whitelist:
    intro.empty()
    stock_info()

# Case 2: Return error message if stock does not exist
elif search_input.upper() != '' and search_input.upper() not in whitelist:
    intro.empty()
    st.error("Error: Invalid stock symbol. Please type a valid stock symbol (e.g. AAPL).", icon="🚨")

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
