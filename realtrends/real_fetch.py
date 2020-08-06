from realtrends import TrendsFetcher

import pandas
import numpy

# Module to fetch approximate real search volumes for a specified term

class RealTrendsFetcher:
    def __get_reference_index(self):
        relative_fetcher = TrendsFetcher()
        relative_fetcher.scrape_trend([self.__ladder[0]],
                geo=self.__geo, time_range=self.__time_range, tz=self.__tz)

        low_volume_profile = relative_fetcher.trends_data

        #print(low_volume_profile)

        return low_volume_profile.index[low_volume_profile[self.__ladder[0]] == 100]

    # todo use some form of means/clustering to infer absolute value?
    # todo more viable initial method: 100/(lowest value)
    def __get_reference_abs(self):
        return 1

    def __get_low_reference(self):
        low_ref_index = self.__get_reference_index()
        low_abs_vol = self.__get_reference_abs()
        return low_ref_index, low_abs_vol

    # function to climb the ladder one step
    def __step_absolute(self, low, high, low_ref_index, low_abs_vol):
        step_fetcher = TrendsFetcher()
        step_fetcher.scrape_trend([low, high],
                                  geo=self.__geo,
                                  time_range=self.__time_range,
                                  tz=self.__tz)
        step_data = step_fetcher.trends_data

        #print(step_data)

        # get relative value where low term popularity is highest
        low_rel_vol = int(step_data.loc[low_ref_index[0], low])

        # todo
        # for now just use index where value is 100 as reference point
        # in the future change this to not use very early data points (could
        # go out of range by the time the next request is made) or very
        # late points (where values are likely to change)
        high_ref_index = step_data.index[step_data[high] == 100]
        high_rel_vol = 100

        high_abs_vol = low_abs_vol * (high_rel_vol / low_rel_vol)
        print(high_abs_vol)

        return high_ref_index, high_abs_vol

    def __transform_keyword_data(self, ladder_term, ladder_ref_index, ladder_abs_vol):
        # get relative data between ladder item and keyword
        keyword_fetcher = TrendsFetcher()
        keyword_fetcher.scrape_trend([ladder_term, self.__keyword],
                                     geo=self.__geo,
                                     time_range=self.__time_range,
                                     tz=self.__tz)

        keyword_data = keyword_fetcher.trends_data

        #print(keyword_data)

        # todo some better measure of whether the comparison is high enough
        # precision
        if keyword_data[ladder_term].max() < 10:
            return False

        # transform 2 column dataframe containing relative data into 1 column
        # dataframe containing absolute data for keyword
        ladder_rel_vol = int(keyword_data.loc[ladder_ref_index[0], ladder_term])

        scale_factor = ladder_abs_vol / ladder_rel_vol
        keyword_data[self.__keyword] = \
            [round(x * scale_factor) for x in keyword_data[self.__keyword]]
        keyword_data.drop(labels=[ladder_term], axis="columns", inplace=True)

        self.real_trends_data = keyword_data
        return True

    # member function to get real trends volume data
    def scrape_real(self, keyword, geo="", time_range="1-H",
                    tz="0", save_file="", retry=True,
                    ladder = ["brierly", "cinderford", "gloucester", "london"]):
        self.__keyword = keyword
        self.__geo = geo
        self.__time_range = time_range
        self.__tz = tz

        # todo find a low volume keyword automatically -
        #  scrape wikipedia list of villages?
        self.__ladder = ladder

        low_ref_index, low_abs_vol = self.__get_low_reference()

        # check against ladder base item, if similar then no need to go up the
        # ladder
        if self.__transform_keyword_data(self.__ladder[0],
                                         low_ref_index, low_abs_vol):
            return

        # Work up the ladder until the highest term magnitude is similar to
        # keyword magnitude:
        i = 0
        comp1 = self.__ladder[i]
        comp2 = self.__ladder[i+1]
        while i < len(self.__ladder) - 1:
            comp1 = self.__ladder[i]
            comp2 = self.__ladder[i+1]
            #print(comp1)
            #print(comp2)
            high_ref_index, high_abs_vol = self.__step_absolute(comp1, comp2, low_ref_index, low_abs_vol)
            if self.__transform_keyword_data(comp2, high_ref_index, high_abs_vol):
                break

            low_ref_index = high_ref_index
            low_abs_vol = high_abs_vol
            i += 1

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

        # real volume data for external use
        self.real_trends_data = pandas.DataFrame()