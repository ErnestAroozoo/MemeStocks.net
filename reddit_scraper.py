from datetime import datetime, timedelta
import datetime as dt
import praw
import psycopg2
import csv
from psaw import PushshiftAPI
from psycopg2 import sql
import time

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

# # Reddit PRAW Client
# reddit = praw.Reddit(client_id='EXQz_JfwBsIDzxPleRVxUg', client_secret='wSRhPRaYmr-uN_htZhnfPwSVJPkTnQ',
#                      redirect_uri='https://memestocks.net', user_agent='memestocks_net')


# FUNCTION: Check if data already exists for a specific date
def date_exists(ticker_name, date_row):
    cur.execute(
        sql.SQL("""
        SELECT date FROM {table} where date = %s
        """).format(table=sql.Identifier(ticker_name.lower())),
        [str(date_row), ]
    )
    if cur.fetchone() is not None:
        return True
    elif cur.fetchone is None:
        return False


# FUNCTION: Scrape historical data using PushShift
def scrape_historical_posts(subreddit_name):
    # Initialize PushShift API
    api = PushshiftAPI()
    # Date to end scraping
    start_time = int(dt.datetime(2021, 12, 31).timestamp())
    # Date range for scraping (1 day = 86400 seconds)
    after_time = int(dt.datetime(2022, 8, 20).timestamp())  # Stop scraping when after_time = start_time
    before_time = after_time + 86400

    print("Date to end scraping (YYYY-MM-DD): " + datetime.utcfromtimestamp(start_time).strftime("%Y-%m-%d"))

    # While loop to retrieve data for every date interval until start_time
    while after_time > start_time:
        print("After " + datetime.utcfromtimestamp(after_time).strftime("%Y-%m-%d"))
        print("Before " + datetime.utcfromtimestamp(before_time).strftime("%Y-%m-%d"))
        submission_date = datetime.utcfromtimestamp(after_time).strftime("%Y-%m-%d")
        # For loop to go through every stock symbol
        for stock_info in data:
            stock_symbol = stock_info[0]
            comments_data = []
            submissions_data = []
            # Retrieve all comments object with the specified stock symbol
            comments = list(api.search_comments(after=after_time,
                                                before=before_time,
                                                q=str(stock_symbol),
                                                subreddit=subreddit_name,
                                                filter=['url', 'author', 'title', 'subreddit', 'body']))
            # Retrieve all submissions object with the specified stock symbol
            submissions = list(api.search_submissions(after=after_time,
                                                      before=before_time,
                                                      q=str(stock_symbol),
                                                      subreddit=subreddit_name,
                                                      filter=['url', 'author', 'title', 'subreddit']))

            # Collect all Submission Titles into a list for analysis
            for submission in submissions:
                submissions_data.append(submission.title)
            submission_numbers = len(submissions_data)
            # Case 1: If date exists in database then update existing row
            if date_exists(stock_symbol, submission_date):
                cur.execute(
                    sql.SQL("""
                    UPDATE {table}
                    SET wallstreetbets_posts = %s, wallstreetbets_posts_data = %s
                    WHERE date = %s
                    """).format(table=sql.Identifier(stock_symbol.lower())),
                    [submission_numbers, submissions_data, submission_date]
                )
            # Case 2: If date does not exist in database then insert new row
            else:
                cur.execute(
                    sql.SQL("""
                    INSERT INTO {table} (date, wallstreetbets_posts, wallstreetbets_posts_data)
                    VALUES (%s, %s, %s)
                    """).format(table=sql.Identifier(stock_symbol.lower())),
                    [submission_date, submission_numbers, submissions_data]
                )
            # Commit updates to database
            print(stock_symbol)
            print(submission_date)
            print(submission_numbers)
            print(submissions_data)
            con.commit()

            # Collect all Comment Bodies into a list for analysis
            for comment in comments:
                comments_data.append(comment.body)
            comment_numbers = len(comments_data)
            # Case 1: If date exists in database then update existing row
            if date_exists(stock_symbol, submission_date):
                cur.execute(
                    sql.SQL("""
                    UPDATE {table}
                    SET wallstreetbets_comments = %s, wallstreetbets_comments_data = %s
                    WHERE date = %s
                    """).format(table=sql.Identifier(stock_symbol.lower())),
                    [comment_numbers, comments_data, submission_date]
                )
            # Case 2: If date does not exist in database then insert new row
            else:
                cur.execute(
                    sql.SQL("""
                    INSERT INTO {table} (date, wallstreetbets_comments, wallstreetbets_comments_data)
                    VALUES (%s, %s, %s)
                    """).format(table=sql.Identifier(stock_symbol.lower())),
                    [submission_date, comment_numbers, comments_data]
                )

            # Commit updates to database
            print(stock_symbol)
            print(submission_date)
            print(comment_numbers)
            print(comments_data)
            con.commit()

        # Update date interval each loop until after_time = start_time
        after_time = after_time - 86400
        before_time = after_time + 86400

    # Close connection to database
    cur.close()
    con.close()


if __name__ == "__main__":
    scrape_historical_posts("wallstreetbets")
