from realtrends import TrendsFetcher, RealTrendsFetcher
import pandas

# test fetch module
animals_fetcher = TrendsFetcher()
animals_fetcher.scrape_trend(["fallow deer", "red deer"], geo="US", time_range="12-m")
print(animals_fetcher.trends_data)

animals_fetcher.scrape_trend(["zebra", "gazelle"], geo="US", time_range="1-m")
print(animals_fetcher.trends_data)


# test real_fetch module
weather_real_fetcher = RealTrendsFetcher()
weather_real_fetcher.scrape_real("rain", geo="GB", time_range="1-d")

print(weather_real_fetcher.real_trends_data)
# print estimated number of times search term was searched in the last day
print(int(weather_real_fetcher.real_trends_data.sum()))
