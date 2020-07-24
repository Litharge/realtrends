from realtrends import TrendsFetcher

import pandas

test_fetcher = TrendsFetcher()

with pandas.option_context("display.max_rows", None, "display.max_columns", None):
    test_fetcher.scrape_trend(["snow", "ice", "sleet", "hail", "rain"], geo = "US", time_range = "1-H", timezone = "")
    test_fetcher.scrape_trend(["snow", "ice", "sleet", "hail", "rain"], geo="US", time_range="1-d", timezone="")
    test_fetcher.scrape_trend(["snow", "ice", "sleet", "hail", "rain"], geo="US", time_range="7-d", timezone="")
    test_fetcher.scrape_trend(["snow", "ice", "sleet", "hail", "rain"], geo="", time_range="1-m", timezone="")
    test_fetcher.scrape_trend(["snow", "ice", "sleet", "hail", "rain"], geo="", time_range="3-m", timezone="")
    test_fetcher.scrape_trend(["snow", "ice", "sleet", "hail", "rain"], geo="", time_range="12-m", timezone="")





