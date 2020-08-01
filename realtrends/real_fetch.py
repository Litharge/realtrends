from realtrends import TrendsFetcher

class RealTrendsFetcher:
    # todo find a low volume keyword automatically - scrape wikipedia list of villages?
    def __get_low_vol_keyword(self):
        self.__low_volume = "brierly"

    def __get_reference_index(self):
        relative_fetcher = TrendsFetcher()
        relative_fetcher.scrape_trend([self.__low_volume],
                geo=self.__geo, time_range=self.__time_range, tz=self.__tz)

        low_volume_profile = relative_fetcher.trends_data
        low_volume_profile.set_index("date_time", inplace=True) # TODO make this depend on resolution: Time vs Day vs Week

        print(low_volume_profile)

        ref_index = low_volume_profile.index[low_volume_profile["brierly"] == 100]

        print(int(low_volume_profile.loc[ref_index[0], "brierly"]))

    # todo use some form of means/clustering to infer absolute value?
    def __get_reference_abs(self):
        self.__low_volume_abs = 1

    def __get_low(self):
        self.__get_reference_index()
        self.__get_reference_abs()

    def scrape_real(self, keyword, geo="", time_range="1-H",
                    tz="0", save_file="", retry=True):
        self.__keyword = keyword
        self.__geo = geo
        self.__time_range = time_range
        self.__tz = tz

        self.__get_low_vol_keyword()

        self.__get_low()

    def __init__(self):
        self.__keyword = ""
        self.__geo = ""
        self.__time_range = ""
        self.__tz = ""

        # keyword to infer absolute values from and start bootstrapping
        self.__low_volume = ""
        # set of values increasing exponentially in popularity
        self.__ladder = []
        # index in low volume data to use as reference point
        self.__low_volume_reference_index = ""
        self.__low_volume_abs = 0