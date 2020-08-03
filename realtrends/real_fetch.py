from realtrends import TrendsFetcher

# Module to fetch approximate real search volumes for a specified term

class RealTrendsFetcher:
    # todo find a low volume keyword automatically - scrape wikipedia list of villages?
    def __get_ladder(self):
        self.__ladder = ["brierly", "cinderford", "gloucester", "london"]

    def __get_reference_index(self):
        relative_fetcher = TrendsFetcher()
        relative_fetcher.scrape_trend([self.__ladder[0]],
                geo=self.__geo, time_range=self.__time_range, tz=self.__tz)

        low_volume_profile = relative_fetcher.trends_data

        print(low_volume_profile)

        self.__low_ref_index = low_volume_profile.index[low_volume_profile[self.__ladder[0]] == 100]

    # todo use some form of means/clustering to infer absolute value?
    # todo more viable initial method: 100/(lowest value)
    def __get_reference_abs(self):
        self.__low_abs_vol = 1

    def __get_low_reference(self):
        self.__get_reference_index()
        self.__get_reference_abs()

    def __similar_vol(self, term1, term2):
        #similar_fetcher = TrendsFetcher()
        #similar_fetcher.scrape_trend([term1, term2],
        #        geo=self.__geo, time_range=self.__time_range, tz=self.__tz)
        #if similar_fetcher.trends_data[term1].max
        return False

    def __step_absolute(self, low, high):
        step_fetcher = TrendsFetcher()

        step_fetcher.scrape_trend([low, high],
                geo=self.__geo, time_range=self.__time_range, tz=self.__tz)

        step_data = step_fetcher.trends_data

        print(step_data)
        # get relative value where low term popularity is highest
        low_rel_vol = int(step_data.loc[self.__low_ref_index[0], low])

        self.__high_ref_index = step_data.index[step_data[high] == 100]
        high_rel_vol = 100

        self.__high_abs_vol = self.__low_abs_vol * (high_rel_vol / low_rel_vol)
        print(self.__high_abs_vol)

    def scrape_real(self, keyword, geo="", time_range="1-H",
                    tz="0", save_file="", retry=True):
        self.__keyword = keyword
        self.__geo = geo
        self.__time_range = time_range
        self.__tz = tz

        self.__get_ladder()

        self.__get_low_reference()

        # Work up the ladder until the lowest term magnitude is similar to
        # keyword magnitude:
        i = 0
        comp1 = self.__ladder[i]
        comp2 = self.__ladder[i+1]
        while self.__similar_vol(self.__keyword, comp1) == False and i < len(self.__ladder) - 1:
            comp1 = self.__ladder[i]
            comp2 = self.__ladder[i+1]
            print("here:")
            print(comp1)
            print(comp2)
            self.__step_absolute(comp1, comp2)
            self.__low_ref_index = self.__high_ref_index
            self.__low_abs_vol = self.__high_abs_vol
            i += 1

        # The values in self.__low_ref_index and self.__low_abs_vol can then
        # be used to find self.__kw_ref_index and self.__kw_abs_vol. Note that
        # the loop above terminates when low and keyword are similar, so __low
        # is used here rather than __high:

        #

    def __init__(self):
        self.__keyword = ""
        self.__geo = ""
        self.__time_range = ""
        self.__tz = ""

        # set of values increasing ~exponentially in popularity
        self.__ladder = []
        # index in low volume data to use as reference point
        self.__low_ref_index = ""
        self.__low_abs_vol = 0