import datetime
import praw


# Scraping process //
def stock_mentions(stock_ticker, subreddit):
    # Declare Reddit Information
    reddit = praw.Reddit(client_id='EXQz_JfwBsIDzxPleRVxUg', client_secret='wSRhPRaYmr-uN_htZhnfPwSVJPkTnQ',
                         redirect_uri='https://memestocks.net', user_agent='memestocks_net')
    # Initialize number of mentions
    mentions = 0
    # Initialize today's date
    today_date = datetime.datetime.now().strftime("%x")
    # Whitelisted words to scrape
    whitelist = [stock_ticker.upper(), "$" + stock_ticker.upper()]
    # Search every new post for the whitelisted words
    for submission in reddit.subreddit(subreddit).new(limit=100):
        submission_title = submission.title.upper()
        submission_title_keywords = submission_title.split()
        submission_date = datetime.datetime.fromtimestamp(submission.created).strftime("%x")
        for word in whitelist:
            if word in submission_title_keywords and submission_date == today_date:
                mentions = mentions + 1
    return mentions
