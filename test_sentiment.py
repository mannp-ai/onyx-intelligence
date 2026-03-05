import yfinance as yf
import pprint
ticker = "AAPL"
stock = yf.Ticker(ticker)
news = stock.news
if news:
    pprint.pprint(news[0])
else:
    print("No news found.")
