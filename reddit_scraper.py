# PRAW for Reddit API web scraping

import praw
import datetime
import main

# Declare Reddit information
reddit = praw.Reddit(client_id='EXQz_JfwBsIDzxPleRVxUg', client_secret='wSRhPRaYmr-uN_htZhnfPwSVJPkTnQ',
                     redirect_uri='https://memestocks.net', user_agent='memestocks_net')

# Declare subreddits to scrape
reddit_wallstreetbets = reddit.subreddit("wallstreetbets")

# Declare the type of content to scrape
new_submission = reddit_wallstreetbets.new(limit=500)

today_date = datetime.datetime.now().strftime("%x")


# Scraping process // TODO: Change subreddit and date range
def stock_mentions(stock_ticker):
    mentions = 0
    whitelist = [stock_ticker.upper(), "$" + stock_ticker.upper()]
    for submission in new_submission:
        submission_title = submission.title.upper()
        submission_title_keywords = submission_title.split()
        submission_date = datetime.datetime.fromtimestamp(submission.created).strftime("%x")
        for word in whitelist:
            if word in submission_title_keywords and submission_date == today_date:
                mentions = mentions + 1
    return mentions

