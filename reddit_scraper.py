import datetime
from datetime import datetime
from datetime import timedelta
import praw
import psycopg2
import csv
from psycopg2 import sql

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

    # Reddit PRAW Client
    reddit = praw.Reddit(client_id='EXQz_JfwBsIDzxPleRVxUg', client_secret='wSRhPRaYmr-uN_htZhnfPwSVJPkTnQ',
                         redirect_uri='https://memestocks.net', user_agent='memestocks_net')

# Initialize today's date in YYYY-MM-DD format
today = datetime.today().utcnow().strftime('%Y-%m-%d')  # Retrieve today's date in UTC


# FUNCTION: Store Reddit posts as a list locally for more optimal scraping
def scrape_posts(subreddit_name):
    # Initialize variables
    posts_list = []  # List used to store the title of all posts within the time range
    for posts in reddit.subreddit(subreddit_name).new(limit=100000):
        post_date = datetime.utcfromtimestamp(posts.created).strftime('%Y-%m-%d')  # Retrieve post's date in UTC
        # Case 1: If the post date is today then add it to the list
        if post_date == today:
            posts_list.append(posts.title)
            print(post_date)
        # Case 2: If post date is not today meaning we can end loop early
        else:
            break
    return posts_list


# FUNCTION: Parse the list of titles for specified keywords and commit to database
def parse_posts(posts_list):
    for tickers in data:
        # Initialize variables
        ticker = tickers[0]
        whitelist_keyword1 = ticker.upper()
        whitelist_keyword2 = '$' + ticker.upper()
        mentions_posts = 0
        content = []
        for titles in posts_list:
            post_title_keywords = titles.upper().split()
            # Case 1: Post date is today and keywords are in the title
            if whitelist_keyword1 in post_title_keywords or whitelist_keyword2 in post_title_keywords:
                mentions_posts = mentions_posts + 1  # Count number of mentions from posts
                content.append(titles)  # Append post title into a list

        print("Symbol: " + ticker + " | Mentions: " + str(mentions_posts))
        print(content)
        # Insert data into PostgreSQL
        cur.execute("""
        INSERT INTO mentions_posts (date, stock_symbol, subreddit, mentions_posts, content)
        VALUES (%s, %s, %s, %s, %s)
        """, (today, ticker, 'wallstreetbets', mentions_posts, content))
    con.commit()


# # FUNCTION: Only need to run once to initialize databases for all stocks
# def create_database_stocks():
#     for tickers in data:
#         sql_code = """
#             CREATE TABLE public.%s
#             (
#                 date date NOT NULL,
#                 wallstreetbets_posts integer,
#                 wallstreetbets_posts_data text[],
#                 wallstreetbets_comments integer,
#                 wallstreetbets_comments_data text[],
#                 PRIMARY KEY (date)
#             );
#         """
#         ticker = str(tickers[0])
#         database_name = ticker
#         sql_code = sql_code % database_name
#         print(sql_code)
#         cur.execute(sql_code)
#         con.commit()


if __name__ == "__main__":
    wallstreetbets_posts_list = scrape_posts('wallstreetbets')  # Retrieve a list of posts from r/wallstreetbets
    parse_posts(wallstreetbets_posts_list)  # Parse title from r/wallstreetbets for keywords

    cur.close()
    con.close()
