from realtrends import TrendsFetcher

class RealTrendsFetcher:
    # todo find a low volume keyword automatically - scrape wikipedia list of villages?
    def __get_ladder(self):
        self.__ladder = ["brierly", "cinderford", "gloucester"]
        #self.__low_volume = "brierly"

    def __get_reference_index(self):
        relative_fetcher = TrendsFetcher()
        relative_fetcher.scrape_trend([self.__ladder[0]],
                geo=self.__geo, time_range=self.__time_range, tz=self.__tz)

        low_volume_profile = relative_fetcher.trends_data
        low_volume_profile.set_index("date_time", inplace=True) # TODO make this depend on resolution: Time vs Day vs Week

        print(low_volume_profile)

        self.__ref_index_low = low_volume_profile.index[low_volume_profile[self.__ladder[0]] == 100]

        #print(int(low_volume_profile.loc[ref_index[0], "brierly"]))

    # todo use some form of means/clustering to infer absolute value?
    def __get_reference_abs(self):
        self.__low_volume_abs = 1

    def __get_low_reference(self):
        self.__get_reference_index()
        self.__get_reference_abs()

    def __similar_vol(self, term1, term2):
        return False

    def __step_absolute(self, low, high):
        step_data = TrendsFetcher()

        step_data.scrape_trend([low, high],
                geo=self.__geo, time_range=self.__time_range, tz=self.__tz)
        print(step_data.trends_data)

    def scrape_real(self, keyword, geo="", time_range="1-H",
                    tz="0", save_file="", retry=True):
        self.__keyword = keyword
        self.__geo = geo
        self.__time_range = time_range
        self.__tz = tz

        self.__get_ladder()

        self.__get_low_reference()

        # work up the ladder until the lowest term is similar in magnitude
        i = 0
        comp1 = self.__ladder[i]
        while self.__similar_vol(self.__keyword, comp1) == False and i < len(self.__ladder)-1:
            i += 1
            comp1 = self.__ladder[i-1]
            comp2 = self.__ladder[i]
            print("here:")
            print(comp1)
            print(comp2)
            self.__step_absolute(comp1, comp2)

    def __init__(self):
        self.__keyword = ""
        self.__geo = ""
        self.__time_range = ""
        self.__tz = ""

        # set of values increasing exponentially in popularity
        # ladder[0] has absolute values inferred
        self.__ladder = []
        # index in low volume data to use as reference point
        self.__ref_index_low = ""
        self.__abs_vol_low = 0