import psycopg2
import streamlit as st
import streamlit.components.v1 as components
import csv
import pandas as pd
import os
from sqlalchemy import create_engine
from dotenv import load_dotenv
from datetime import datetime
from pytz import timezone
import duckdb

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

# CUSTOMIZATION: Hide unnecessary UI elements
hide_streamlit_style = """
                <style>
                div[data-testid="stToolbar"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
                }
                div[data-testid="stDecoration"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
                }
                div[data-testid="stStatusWidget"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
                }
                #MainMenu {
                visibility: hidden;
                height: 0%;
                }
                header {
                visibility: hidden;
                height: 0%;
                }
                footer {
                visibility: hidden;
                height: 0%;
                }
                .css-15zrgzn {display: none}
                #root > div:nth-child(1) > div > div > div > div > section > div {padding-top: 0rem;}
                </style>
                """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# CONNECTION: PostgreSQL Database
load_dotenv()
con = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    database=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    port=os.getenv("DB_PORT")
)
cur = con.cursor()
db_string = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
connection = create_engine(db_string, pool_size=20, max_overflow=0).connect()

# CONNECTION: Stock Tickers CSV Dataset
with open('stock_tickers.csv', newline='') as f:
    reader = csv.reader(f)
    data = list(reader)
whitelist = []
stock_name_list = []
for stock_info in data:
    whitelist.append(stock_info[0])
    stock_name_list.append(stock_info[1])


# FUNCTION: Display stock information
def stock_info():
    st.warning(
        "DISCLAIMER: The data provided should be used for informational purposes only and in no way should be relied upon for financial advice.",
        icon="⚠️")
    # Create columns for section 1

    st.subheader('Information', anchor=False)
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

    st.subheader('Mentions Data', anchor=False)
    
    # Create Pandas object using data from PostgreSQL
    database_name = search_input.lower()
    df = pd.read_sql_table(database_name, connection)
    df = duckdb.query(f"""
                      SELECT date AS "Date", wallstreetbets_posts AS "Number of Posts", wallstreetbets_posts_data AS "Posts", 
                      wallstreetbets_comments AS "Number of Comments", wallstreetbets_comments_data AS "Comments"
                      FROM df
                      ORDER BY "Date" DESC
                      """).to_df()
    # Change date format to YY-MM-DD
    df["Date"] = pd.to_datetime(df["Date"]).dt.date
  
    # Display Pandas table
    st.dataframe(data=df, height=140, width=3000, hide_index=True)

    # Create columns for section 2
    with st.container():
        col3, col4, col5 = st.columns(3)
        with col3:
            st.line_chart(data=df, x='Date', y='Number of Posts', width=1000, height=250, use_container_width=True)
        with col4:
            st.line_chart(data=df, x='Date', y='Number of Comments', width=1000, height=250, use_container_width=True)
        with col5:
            df["Number of Posts & Comments"] = df["Number of Posts"] + df["Number of Comments"]
            st.line_chart(data=df, x='Date', y='Number of Posts & Comments', width=1000, height=250,
                          use_container_width=True)

    con.close()


# Title of the web app
st.title("📈 MemeStocks.net", anchor=False)

# Search input
search_input = (st.text_input('Stock Symbol', '', max_chars=5, key=str,
                              placeholder="Type a stock symbol and then press enter (e.g. GME)")).strip().upper()
subreddit_input = st.selectbox('Subreddit', ['WallStreetBets'])

# Intro tutorial
intro = st.empty()
with intro.container():
    # Info dialogue
    st.info('Welcome to MemeStocks.net! To get started, please type a valid stock symbol in the search bar above and then press enter.', icon="ℹ️")
    st.warning(
        "We regret to inform you that due to recent changes in the terms of service of the Reddit API, we are no longer able to obtain new data. As of May 1, 2023, new data ingestion is no longer possible.",
        icon="⚠️")
    # Text body
    st.markdown("""
    ------------
    ### What is MemeStocks.net?
    MemeStocks.net is a web application that tracks the historical popularity of specific stocks by monitoring Reddit mentions. Users can search for a stock symbol to access detailed information, including the stock's name, price, and historical popularity data. The data is collected using the Pushshift API and stored in a PostgreSQL database. The application generates time-series graphs to visually display the stock's popularity trends over time, helping users make more informed investment decisions.
    """)
    # Add gif
    col1, col2, col3 = st.columns([20, 45, 20])
    with col2:
        st.image("tutorial.gif")

# Case 1: Display information if stock exists
if search_input.upper() != '' and search_input.upper() in whitelist:
    intro.empty()
    stock_info()
    # Logs
    if search_input != "" and subreddit_input != "":
        print(f"[{datetime.now(timezone('EST'))}] Stock Symbol: {search_input}, Subreddit: {subreddit_input}")

# Case 2: Return error message if stock does not exist
elif search_input.upper() != '' and search_input.upper() not in whitelist:
    intro.empty()
    st.error("Error: Invalid stock symbol. Please type a valid stock symbol (e.g. AAPL).", icon="🚨")
    # Logs
    if search_input != "" and subreddit_input != "":
        print(f"[{datetime.now(timezone('EST'))}] Stock Symbol: {search_input}, Subreddit: {subreddit_input}, Error: Invalid stock symbol")

# CUSTOMIZATION: Change footer again to prevent clipping
add_footer_style2 = """<style>
.footer {
position: fixed;
left: 0;
bottom: 0;
width: 100%;
background-color: #212121;
color: #f1f1f1;
text-align: center;
padding: 2px;
font-size: 12px;
}
a {
color: #f1f1f1;
text-decoration: none;
}
</style>
<div class="footer">
<p>Made by <a href='https://github.com/ErnestAroozoo' target='_blank'>Ernest Aroozoo</a> | <a href='https://github.com/ErnestAroozoo/MemeStocks.net' target='_blank'>View on GitHub</a></p>
</div>
"""
st.markdown(add_footer_style2, unsafe_allow_html=True)
