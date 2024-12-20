import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import os
from sqlalchemy import create_engine
from dotenv import load_dotenv
import duckdb
import plotly.express as px
from PIL import Image
import base64
import io
import yfinance as yf

# ==========================================================
# Section: Page Config
# ==========================================================
st.set_page_config(
    page_title="MemeStocks.net - Stock sentiment analytical tool",
    page_icon="./assets/favicon.ico",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'http://memestocks.net',
        'Report a bug': "http://memestocks.net",
        'About': "MemeStocks.net is a tool that scrapes Reddit for the number of stock mentions"
    }
)

# ==========================================================
# Section: CSS Styling
# ==========================================================
# Layout
st.markdown("""
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

                /* Remove blank space at top and bottom */ 
                .block-container {
                    padding-top: 0rem;
                    padding-bottom: 0rem;
                    }
                
                /* Remove blank space at the center canvas */ 
                .st-emotion-cache-z5fcl4 {
                    position: relative;
                    top: -62px;
                    }
                
                /* Make the toolbar transparent and the content below it clickable */ 
                .st-emotion-cache-18ni7ap {
                    pointer-events: none;
                    background: rgb(255 255 255 / 0%)
                    }
                .st-emotion-cache-zq5wmm {
                    pointer-events: auto;
                    background: rgb(255 255 255);
                    border-radius: 5px;
                    }
            </style>
                """, unsafe_allow_html=True)

# Footer
st.markdown("""
            <style>
            .footer {
                position: fixed;
                left: 0;
                bottom: 0;
                width: 100%;
                background-color: #232323;
                color: #FFFFFF;
                text-align: center;
                padding: 0px 0;
                font-size: 15px;
                height: 35px;
                line-height: 30px;
            }
            .footer a {
                color: #6464ef;
                text-decoration: none;
            }
            </style>
            <div class="footer">
            <p>Made by <a href='https://github.com/ErnestAroozoo' target='_blank'>Ernest Aroozoo</a> | <a href='https://github.com/ErnestAroozoo/MemeStocks.net' target='_blank'>View on GitHub</a></p>
            </div>
            """, unsafe_allow_html=True)

# Metric Cards
def metric_card(icon_name, value, description, fontsize=18, blink=False, icon_color="#F9B500"):
    """
    Helper function to create custom style for Streamlit metric cards
    """
    # Define colors and styles
    background_color = (33, 33, 33)  # Dark background
    font_color = (255, 255, 255)     # White text
    border_radius = 10               # Rounded corners

    icon_style = f"color: {icon_color}; font-size: 24px; position: absolute; top: 8px; right: 8px;"

    # Create the HTML string for the custom metric
    html_str = f"""
    <link href="https://fonts.googleapis.com/icon?family=Material+Icons+Outlined" rel="stylesheet">
    <div style='background-color: rgb({background_color[0]}, {background_color[1]}, {background_color[2]}); 
                padding: 18px; border-radius: {border_radius}px; position: relative;'>
        <i class='material-icons-outlined' style='{icon_style}'>{icon_name}</i>
        <div style='display: flex; flex-direction: column; align-items: flex-start;'>
            <span style='color: rgb({font_color[0]}, {font_color[1]}, {font_color[2]}); 
                         font-size: 14px;'>{description}</span>
            <strong style='color: rgb({font_color[0]}, {font_color[1]}, {font_color[2]}); 
                           font-size: {fontsize}px;'>{value}</strong>
        </div>
    </div>
    """
    # Display the custom metric
    st.markdown(html_str, unsafe_allow_html=True)

# Title
def image_to_base64(img_path):
    img = Image.open(img_path)
    img_data = io.BytesIO()
    img.save(img_data, format='PNG')
    img_base64 = base64.b64encode(img_data.getvalue()).decode('utf-8')
    return img_base64
custom_title = """
                <style>
                    .custom-title {{
                        display: flex;
                        align-items: center;
                        font-family: Arial, sans-serif;
                        color: #FFFFFF;
                    }}
                    .custom-title img {{
                        height: 55px;
                        margin-right: 3px;
                        position: relative;
                        top: -8px;
                    }}
                    .custom-title h1 {{
                        font-size: 2.5rem;
                        margin: 0;
                    }}
                </style>
                <div class="custom-title">
                    <img src="data:image/png;base64,{logo}" alt="Logo">
                    <h2>MemeStocks.net</h2>
                </div>
                """
logo_base64 = image_to_base64('./assets/logo.png')
custom_title = custom_title.format(logo=logo_base64)
st.markdown(custom_title, unsafe_allow_html=True)
st.html("<style>[data-testid='stHeaderActionElements'] {display: none;}</style>")

# ==========================================================
# Section: Streamlit UI and Logic
# ==========================================================
# CSV Dataset
if 'stock_tickers_df' not in st.session_state:
    st.session_state['stock_tickers_df'] = pd.read_csv('stock_tickers.csv', names=['Symbol', 'Name', 'MarketCap'])

# Search Bar (Default to "GME")
search_input = (st.text_input('Stock Symbol', 'GME', max_chars=5, key=str, placeholder="Type a stock symbol and then press enter (e.g. GME)")).strip().upper()
subreddit_input = st.selectbox('Subreddit', ['WallStreetBets'])

# Notifications
st.info('Welcome to MemeStocks.net! To get started, please type a valid stock symbol in the search bar above and then press enter.', icon=":material/info:")
st.warning("Due to recent changes in Reddit's API terms of service, we are unable to retrieve new data. Data ingestion has been halted as of May 1, 2023.", icon=":material/warning:")

@st.fragment()
def stock_info_fragment():
    """
    Display relevant stock info
    """
    # Information
    st.subheader('Overview')

    # Fetch stock data using yfinance
    ticker = yf.Ticker(search_input)
    stock_info = ticker.info

    # Overview Metric Cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        metric_card("list_alt", search_input, "Stock Symbol", icon_color="#6464ef")
        st.write("") # Empty padding
    with col2:
        stock_name = stock_info.get('longName', 'N/A')
        metric_card("article", stock_name, "Name", icon_color="#6464ef")
        st.write("") # Empty padding
    with col3:
        # Use totalAssets as a proxy for market cap if marketCap is not provided
        market_cap = stock_info.get('marketCap', stock_info.get('totalAssets', 'N/A'))
        if isinstance(market_cap, (int, float)):
            market_cap = f"${market_cap:,.0f}"
        else:
            market_cap = "N/A"
        metric_card("account_balance", market_cap, "Market Cap", icon_color="#6464ef")
        st.write("") # Empty padding
    with col4:
        # Try to use currentPrice, if not available fallback to navPrice or regularMarketOpen
        current_price = stock_info.get('currentPrice',
                        stock_info.get('navPrice',
                        stock_info.get('regularMarketOpen', 'N/A')))
        
        if isinstance(current_price, (int, float)):
            current_price = f"${current_price:,.2f}"
        else:
            current_price = "N/A"
        metric_card("attach_money", current_price, "Current Price", icon_color="#6464ef")
        st.write("") # Empty padding

    # TradingView Chart
    components.html(
        f"""
        <!-- TradingView Widget BEGIN -->
        <div class="tradingview-widget-container" style="height:100%;width:100%">
        <div class="tradingview-widget-container__widget" style="height:calc(100% - 32px);width:100%"></div>
        <div class="tradingview-widget-copyright">
            <a href="https://www.tradingview.com/" rel="noopener nofollow" target="_blank">
            </a>
        </div>
        <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-advanced-chart.js" async>
        {{
        "height": 450,
        "symbol": "{search_input.upper()}",
        "interval": "D",
        "timezone": "Etc/UTC",
        "theme": "dark",
        "style": "2",
        "locale": "en",
        "backgroundColor": "rgba(0, 0, 0, 1)",
        "gridColor": "rgba(240, 243, 250, 0.02)",
        "hide_top_toolbar": true,
        "hide_legend": true,
        "allow_symbol_change": false,
        "save_image": false,
        "calendar": false,
        "hide_volume": true,
        "support_host": "https://www.tradingview.com"
        }}
        </script>
        </div>
        <!-- TradingView Widget END -->
        """,
        height=430,
        scrolling=False
    )

    # Social Analytics
    st.subheader('Social Analytics')

    # PostgreSQL Database
    load_dotenv()
    db_string = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    if 'connection' not in st.session_state:
        with st.spinner("Connecting..."):
            st.session_state['connection'] = create_engine(db_string, pool_size=20, max_overflow=0).connect()

    # Create Pandas object using data from PostgreSQL
    database_name = search_input.lower()
    with st.spinner("Loading..."):
        df = pd.read_sql_table(database_name, st.session_state['connection'])
    df = duckdb.query(f"""
                      SELECT date AS "Date", wallstreetbets_posts AS "Number of Posts", wallstreetbets_posts_data AS "Posts", 
                      wallstreetbets_comments AS "Number of Comments", wallstreetbets_comments_data AS "Comments"
                      FROM df
                      ORDER BY "Date" DESC
                      """).to_df()
    # Change date format to YY-MM-DD
    df["Date"] = pd.to_datetime(df["Date"]).dt.date

    # Social Analytics Metric Cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        # Calculate total posts using df and display in metric card
        total_posts = df["Number of Posts"].sum()
        metric_card("post_add", f"{total_posts:,}", "Total Reddit Posts", icon_color="#6464ef")
        st.write("") # Empty padding

    with col2:
        # Calculate total comments using df and display in metric card
        total_comments = df["Number of Comments"].sum()
        metric_card("comment", f"{total_comments:,}", "Total Reddit Comments", icon_color="#6464ef")
        st.write("") # Empty padding

    with col3:
        # Calculate 7-day average posts using df and display in metric card
        if len(df) >= 7:
            # Calculate the average over the last 7 days
            avg_posts_7_days = df["Number of Posts"].head(7).mean()
        else:
            # If less than 7 days of data, take average of available data
            avg_posts_7_days = df["Number of Posts"].mean()
        metric_card("show_chart", f"{avg_posts_7_days:,.2f}", "Weekly Average Posts", icon_color="#6464ef")
        st.write("") # Empty padding

    with col4:
        # Calculate 7-day average comments using df and display in metric card
        if len(df) >= 7:
            # Calculate the average over the last 7 days
            avg_comments_7_days = df["Number of Comments"].head(7).mean()
        else:
            # If less than 7 days of data, take average of available data
            avg_comments_7_days = df["Number of Comments"].mean()
        metric_card("stacked_line_chart", f"{avg_comments_7_days:,.2f}", "Weekly Average Comments", icon_color="#6464ef")
        st.write("") # Empty padding
  
    # Data Visualizations
    with st.container(height=430, border=True):
        # Add the 'Number of Posts & Comments' column to the DataFrame
        df["Number of Posts & Comments"] = df["Number of Posts"] + df["Number of Comments"]
        
        # Prepare the data for Plotly
        df_melted = df.melt(id_vars='Date', value_vars=['Number of Posts', 'Number of Comments', 'Number of Posts & Comments'],
                            var_name='Type', value_name='Count')

        # Define custom colors
        colors = {
            'Number of Posts': '#1d94d7',
            'Number of Comments': '#6464ef',
            'Number of Posts & Comments': '#9c32f3'
        }

        # Create a Plotly line chart
        fig = px.line(
            df_melted,
            x='Date',
            y='Count',
            color='Type',
            labels={'Count': 'Number'},
            template='plotly_dark',
            color_discrete_map=colors
        )

        # Update layout to hide titles, grid lines, and adjust legend
        fig.update_layout(
            autosize=True,
            width=1000,
            height=400,
            margin=dict(l=0, r=0, t=50, b=0),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.05,
                xanchor="center",
                x=0.5,
                title_text=''
            ),
            xaxis_title=None,
            yaxis_title=None,
            showlegend=True,
            xaxis=dict(
                showgrid=False,
                rangeslider=dict(visible=False),  # Disable range slider
                type="date",
                automargin=True  # Auto adjust the x-axis
            ),
            yaxis=dict(
                showgrid=False,
                automargin=True  # Auto adjust the y-axis
            ),
            hovermode='x unified',
            dragmode='pan'  # Set default mode to 'pan'
        )

        # Display the Plotly chart
        st.plotly_chart(fig, use_container_width=True, config={
            'scrollZoom': True,  # Enable scroll to zoom
            'displayModeBar': True,  # Show the mode bar
            'displaylogo': False,  # Hide the Plotly logo
            'modeBarButtonsToRemove': ['toImage']  # Remove the full screen button
        })

    # Display dataframe table
    with st.container(height=500, border=False):
        st.dataframe(data=df, height=450, width=10000, hide_index=True)

# Case 1: Display information if stock exists
if not st.session_state['stock_tickers_df'][st.session_state['stock_tickers_df']['Symbol'] == search_input].empty:
    stock_info_fragment()

# Case 2: Return error message if stock does not exist
elif search_input:
    st.error("Invalid stock symbol. Please type a valid stock symbol (e.g. AAPL).", icon=":material/error:")

# ==========================================================
# Section: CSS Footer
# ==========================================================
# Footer
st.markdown("""
            <style>
            .footer {
                position: fixed;
                left: 0;
                bottom: 0;
                width: 100%;
                background-color: #232323;
                color: #FFFFFF;
                text-align: center;
                padding: 0px 0;
                font-size: 15px;
                height: 35px;
                line-height: 30px;
            }
            .footer a {
                color: #6464ef;
                text-decoration: none;
            }
            </style>
            <div class="footer">
            <p>Made by <a href='https://github.com/ErnestAroozoo' target='_blank'>Ernest Aroozoo</a> | <a href='https://github.com/ErnestAroozoo/MemeStocks.net' target='_blank'>View on GitHub</a></p>
            </div>
            """, unsafe_allow_html=True)
