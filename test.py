from realtrends import TrendsFetcher, RealTrendsFetcher
import pandas

test_real_fetcher = RealTrendsFetcher()

test_real_fetcher.scrape_real("rain", geo="GB", time_range="1-d")

print(test_real_fetcher.real_trends_data)

# print estimated number of times search term was searched in the last day
print(int(test_real_fetcher.real_trends_data.sum()))
