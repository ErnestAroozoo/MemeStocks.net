# MemeStocks.net
------------
### What is MemeStocks.net?
MemeStocks.net is a web application that tracks the historical popularity of specific stocks by monitoring the number of mentions on Reddit. Users can search for a stock symbol and view information such as the stock's name, price, and historical popularity data. The data is gathered through web scraping and stored in a PostgreSQL database hosted on Heroku. The application generates multiple time-series graphs to display the historical popularity of the stock, allowing users to see trends in the stock's popularity over time and make more informed decisions about their investments.

![](https://github.com/ErnestAroozoo/MemeStocks.net/blob/main/tutorial.gif)

### How Does It Work?
The web application uses web scraping techniques to gather historical data on stock mentions from Reddit, utilizing the PMAW library to access the Pushshift.io API. The scraping process is automated on a daily basis using Heroku Scheduler, making sure that the data is always up-to-date. The collected data is then stored in a PostgreSQL database hosted on Heroku for easy access and analysis.
When a user enters a stock symbol, the application employs the Pandas library to retrieve and filter relevant data from the database. This data is then utilized to generate multiple time-series graphs that display the historical popularity of the stock. These graphs allow users to identify trends in the stock's popularity over time. The application also employs the Streamlit library to create an interactive user interface, which enables users to easily search for and view stock information.
The psycopg2 and SQLAlchemy libraries are utilized to connect to the PostgreSQL database, allowing for easy querying of the data. The Pandas library is employed to filter and process the data before it is displayed in the time-series graph.
