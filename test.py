from realtrends import TrendsFetcher

#cookie = realtrends.getCookie()

#print(realtrends.get_trend("snow", cookie))

test_fetcher = TrendsFetcher()

test_fetcher.scrape_trend(["snow","ice"], geo="US")





