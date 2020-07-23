from realtrends import TrendsFetcher

import pandas

test_fetcher = TrendsFetcher()

with pandas.option_context("display.max_rows", None, "display.max_columns", None):
    test_fetcher.scrape_trend(["snow", "ice", "sleet", "hail", "rain"], geo= "" , time_range = "12M", timezone = "")
    test_fetcher.scrape_trend(["snow", "ice", "sleet", "hail", "rain"], geo = "US", time_range = "1H", timezone = "")





