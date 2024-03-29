from datetime import datetime, timedelta, date
import datetime as dt
import psycopg2
import csv
from pmaw import PushshiftAPI
from psycopg2 import sql
import time
import os
from dotenv import load_dotenv

# Heroku PostgreSQL Database
load_dotenv()
con = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    database=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    port=os.getenv("DB_PORT")
)
cur = con.cursor()

# Stock Tickers CSV Database
with open('stock_tickers.csv', newline='') as f:
    reader = csv.reader(f)
    data = list(reader)

# Initialize today's date
    today_date = str(date.today())
    today_date_unix = int(time.mktime(dt.datetime.strptime(today_date, "%Y-%m-%d").timetuple()))


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
def scrape_daily_posts(subreddit_name):
    # Initialize PushShift API
    api = PushshiftAPI()
    # Date range for scraping
    yesterday_date_unix = today_date_unix - 86400
    tomorrow_date_unix = today_date_unix + 86400
    after_time = today_date_unix  # After Today's Date 12:00am
    before_time = tomorrow_date_unix  # Before Tomorrow's Date 12:00am

    print("Date to perform data scraping (YYYY-MM-DD): " + datetime.utcfromtimestamp(after_time).strftime("%Y-%m-%d"))

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
            submissions_data.append(submission['title'])
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
            comments_data.append(comment['body'])
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


# FUNCTION: Scrape yesterday data with Pushshift
def scrape_yesterday_posts(subreddit_name):
    # Initialize PushShift API
    api = PushshiftAPI()
    # Date range for scraping
    yesterday_date_unix = today_date_unix - 86400
    tomorrow_date_unix = today_date_unix + 86400
    after_time = yesterday_date_unix  # After Yesterday's Date 12:00am
    before_time = today_date_unix  # Before Today's Date 12:00am

    print("Date to perform data scraping (YYYY-MM-DD): " + datetime.utcfromtimestamp(after_time).strftime("%Y-%m-%d"))

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
            submissions_data.append(submission['title'])
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
            comments_data.append(comment['body'])
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


if __name__ == "__main__":
    scrape_daily_posts("wallstreetbets")
    scrape_yesterday_posts("wallstreetbets")
    # Close connection to database
    cur.close()
    con.close()
