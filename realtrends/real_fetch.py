from realtrends import TrendsFetcher

class RealTrendsFetcher:
    __keyword = ""
    __geo = ""
    __time_range = ""
    __tz = ""

    # keyword to get absolute values from
    __low_volume = ""
    # index in data to use as reference point
    __low_volume_reference_index = ""

    # TODO find a low volume keyword automatically - scrape wikipedia list of villages?
    def get_low_vol_keyword(self):
        self.__low_volume = "brierly"

    def get_reference_index(self):
        relative_fetcher = TrendsFetcher()
        relative_fetcher.scrape_trend([self.__low_volume],
                geo=self.__geo, time_range=self.__time_range, tz=self.__tz)

        low_volume_profile = relative_fetcher.trends_data
        low_volume_profile.set_index("Time", inplace=True) # TODO make this depend on resolution: Time vs Day vs Week

        print(low_volume_profile)

        #print(low_volume_profile.loc(low_volume_profile[low_volume_profile.columns[0]] == "100"))

    def scrape_real(self, keyword, geo="", time_range="12-m",
            tz="0", save_file="", retry=True):
        self.__keyword = keyword
        self.__geo = geo
        self.__time_range = time_range
        self.__tz = tz

        self.get_low_vol_keyword()

        self.get_reference_index()

