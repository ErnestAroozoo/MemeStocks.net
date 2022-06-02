import datetime
from datetime import datetime, timedelta
import praw


# Scraping process
def stock_mentions(stock_ticker, subreddit, time_range):
    # Declare Reddit Information
    reddit = praw.Reddit(client_id='EXQz_JfwBsIDzxPleRVxUg', client_secret='wSRhPRaYmr-uN_htZhnfPwSVJPkTnQ',
                         redirect_uri='https://memestocks.net', user_agent='memestocks_net')
    # Initialize number of mentions
    mentions = 0
    # Initialize time range in unix time
    days_ago = (datetime.today() - timedelta(days=time_range)).timestamp()
    # Whitelisted words to scrape
    whitelist = [stock_ticker.upper(), "$" + stock_ticker.upper()]
    # Search every new post for the whitelisted words
    for submission in reddit.subreddit(subreddit).new(limit=1000):
        submission_title = submission.title.upper()
        submission_title_keywords = submission_title.split()
        submission_date = submission.created
        if submission_date >= days_ago:
            for word in whitelist:
                if word in submission_title_keywords:
                    mentions = mentions + 1
                    print(submission.title)
        else:
            print(submission.created)
            break
    return mentions
