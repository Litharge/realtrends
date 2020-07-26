from realtrends import TrendsFetcher
import time
import pandas

test_fetcher = TrendsFetcher()

with pandas.option_context("display.max_rows", None, "display.max_columns", None):
    for tr in ["1-H","4-H","1-d","7-d","1-m","3-m","12-m"]:
        for i in range(1):
            test_fetcher.scrape_trend(["snow", "ice", "sleet", "hail", "rain"], geo = "", time_range = tr, tz = "-60", save_file="testSave")
            print(test_fetcher.trends_data)





