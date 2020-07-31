from realtrends import TrendsFetcher, RealTrendsFetcher
import pandas

test_fetcher = TrendsFetcher()
"""
with pandas.option_context("display.max_rows", None, "display.max_columns", None):
    for tr in ["1-H","4-H","1-d","7-d","1-m","3-m","12-m","5-y"]:
        test_fetcher.scrape_trend(["snow", "ice", "sleet", "hail", "rain"], geo="GB", time_range=tr, tz="-60")
        print(test_fetcher.trends_data)
"""

test_real_fetcher = RealTrendsFetcher()

test_real_fetcher.scrape_real("Cinderford", geo="GB", time_range="1-H")




