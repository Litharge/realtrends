from realtrends import TrendsFetcher
import time
import pandas

test_fetcher = TrendsFetcher()

with pandas.option_context("display.max_rows", None, "display.max_columns", None):
    for tr in ["1-d"]:
        test_fetcher.scrape_trend(["snow", "ice", "sleet", "hail", "rain"], geo = "GB", time_range = tr, tz = "-60")
        print(test_fetcher.trends_data)





