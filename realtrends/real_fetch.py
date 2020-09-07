from realtrends import TrendsFetcher

import pandas

# Module to fetch approximate real/absolute search volumes for a specified term

class RealTrendsFetcher:
    def __get_reference_index(self, low_volume_profile):
        # search for the highest index, this will always be 100 as we are looking at this term alone
        reference_index = low_volume_profile.index[low_volume_profile[self.__ladder[0]] == 100]

        return reference_index

    # calculate what the maximum volume index represents as an absolute value
    # we assume that the lowest nonzero index represents a single search
    # so to get the absolute value at max, we divide the relative volume at max (100) by the relative search volume
    # at the nonzero minimum
    def __get_reference_abs(self, low_volume_profile):
        lowest_nonzero = low_volume_profile[low_volume_profile.gt(0)].min(0)
        return 100.0 / lowest_nonzero

    def __get_low_reference(self):
        relative_fetcher = TrendsFetcher()
        relative_fetcher.scrape_trend([self.__ladder[0]], geo=self.__geo, time_range=self.__time_range, tz=self.__tz)

        low_volume_profile = relative_fetcher.trends_data

        low_ref_index = self.__get_reference_index(low_volume_profile)
        low_abs_vol = self.__get_reference_abs(low_volume_profile)
        return low_ref_index, low_abs_vol

    # function to "climb" the ladder one step
    # gets a DataFrame with relative volumes for low_term and high_term
    # from this DataFrame, finds low_rel_vol at low_ref_index
    # high_ref_index is then selected to be where high_term is highest (always 100)
    # high_abs_vol is the absolute volume at this index, given by low_abs_vol * (high_rel_vol / low_rel_vol)
    # high_ref_index, high_abs_vol are then returned (these may then be passed to __step_absolute() again later to
    # generate the next index and volume
    def __step_absolute(self, low_term, high_term, low_ref_index, low_abs_vol):
        step_fetcher = TrendsFetcher()
        step_fetcher.scrape_trend([low_term, high_term],
                                  geo=self.__geo,
                                  time_range=self.__time_range,
                                  tz=self.__tz)
        step_data = step_fetcher.trends_data

        #print(step_data)

        # get relative value where low term popularity is highest
        low_rel_vol = int(step_data.loc[low_ref_index, low_term])

        # todo
        # for now just use index where value is 100 as reference point
        # in the future change this to not use very early data points (could
        # go out of range by the time the next request is made) or very
        # late points (where values are likely to change)
        high_ref_index = step_data.index[step_data[high_term] == 100]
        high_rel_vol = 100

        high_abs_vol = low_abs_vol * (high_rel_vol / low_rel_vol)
        # print(high_abs_vol)

        return high_ref_index, high_abs_vol

    def __transform_keyword_data(self, ladder_term, ladder_ref_index, ladder_abs_vol):
        # get relative data between ladder item and keyword
        keyword_fetcher = TrendsFetcher()
        keyword_fetcher.scrape_trend([ladder_term, self.__search_term],
                                     geo=self.__geo,
                                     time_range=self.__time_range,
                                     tz=self.__tz)

        search_term_data = keyword_fetcher.trends_data

        #print(search_term_data)

        # if ladder_term maximum relative volume is low this means it is not comparable to search_term, so we return
        # false, this then leads to the next ladder term having its reference index and absolute volume calculated
        # and passed, this is repeated until a comparable ladder term is found
        if search_term_data[ladder_term].max() < 10:
            return False

        # transform 2 column dataframe containing relative data into 1 column
        # dataframe containing absolute data for keyword

        ladder_rel_vol = int(search_term_data.loc[ladder_ref_index, ladder_term])

        scale_factor = ladder_abs_vol / ladder_rel_vol
        search_term_data[self.__search_term] = search_term_data[self.__search_term].apply(lambda x: round(x * scale_factor))
        search_term_data.drop(labels=[ladder_term], axis="columns", inplace=True)

        self.real_trends_data = search_term_data
        return True

    # member function to get real trends volume data
    def scrape_real(self, search_term, geo="", time_range="1-H",
                    tz="0", save_file="", retry=True,
                    ladder = ["englishcombe", "bathampton", "keynsham", "chippenham", "swindon", "bath", "london"]):
        self.__search_term = search_term
        self.__geo = geo
        self.__time_range = time_range
        self.__tz = tz

        self.__ladder = ladder

        # find a time and the absolute volume at this time using the first ladder item (default "englishcombe")
        low_ref_index, low_abs_vol = self.__get_low_reference()

        # check keyword against ladder base item (default "englishcombe")
        # if similar then no need to go up the ladder
        if self.__transform_keyword_data(self.__ladder[0], low_ref_index, low_abs_vol):
            return

        # Check keyword against ladder item 2, 3...
        i = 0
        while i < len(self.__ladder) - 1:
            comp1 = self.__ladder[i]
            comp2 = self.__ladder[i+1]

            # find
            high_ref_index, high_abs_vol = self.__step_absolute(comp1, comp2, low_ref_index, low_abs_vol)

            if self.__transform_keyword_data(comp2, high_ref_index, high_abs_vol):
                break

            low_ref_index = high_ref_index
            low_abs_vol = high_abs_vol
            i += 1

    def __init__(self):
        self.__search_term = ""
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