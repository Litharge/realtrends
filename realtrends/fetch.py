import io
import re
import urllib.parse
from datetime import datetime, timezone

import pandas
import pycurl
from dateutil.relativedelta import relativedelta


class TrendsFetcher:
    __cookie = ""

    # Temporary headers taken from firefox on my machine
    __default_cookie_header = [
        "User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0",
        "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language: en-GB,en;q=0.5",
        "Connection: keep-alive",
        "Upgrade-Insecure-Requests: 1",
        "Cache-Control: max-age=0"
    ]

    __default_token_header = [
        "User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0",
        "Accept: application/json, text/plain, */*",
        "Accept-Language: en-GB,en;q=0.5",
        "Connection: keep-alive",
        "Referer: https://trends.google.com/trends/explore?q=snow&geo=US",
        "TE: Trailers"
    ]

    __default_csv_header = [
        "User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0",
        "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language: en-GB,en;q=0.5",
        "Connection: keep-alive",
        "Referer: https://trends.google.com/trends/explore?q=snow&geo=US",
        "Upgrade-Insecure-Requests: 1",
        "TE: Trailers"
    ]

    # Fetch a cookie, this is needed to fetch a token
    def __get_cookie(self):
        cookie_curl = pycurl.Curl()

        cookie_curl.setopt(pycurl.URL,
                           'https://trends.google.com/trends/explore?geo=US&q=snow')
        cookie_curl.setopt(pycurl.HTTPHEADER, self.__default_cookie_header)

        byte_data = io.BytesIO()
        cookie_curl.setopt(pycurl.WRITEHEADER, byte_data)

        cookie_curl.perform_rb()
        cookie_curl.close()
        # convert header into a string and extract cookie
        header = byte_data.getvalue().decode("utf8")

        header = header.split("Set-Cookie:")[1]
        cookie = header.split(";")[0] + ";"

        TrendsFetcher.__cookie = cookie

    def __generate_token_query_request_comparison_item_list(self):
        time_phrase = {
            "1-H": "now 1-H", "4-H": "now 4-H", "1-d": "now 1-d",
            "7-d": "now 7-d", "1-m": "today 1-m", "3-m": "today 3-m",
            "12-m": "today 12-m", "5-y": "today 5-y",
        }
        token_time = time_phrase.get(self.__time_range)
        comparison_item_list = ""
        for kw in self.__keywords:
            comparison_item_list_element = """
            "keyword":"%s","geo":"%s","time":"%s"
            """ % (kw, self.__geo, token_time)
            comparison_item_list_element = "{" + comparison_item_list_element + "},"
            comparison_item_list += comparison_item_list_element
        # Return the list except the last character, which is an unneeded comma
        return comparison_item_list[:-1]

    def __generate_token_query_request_comparisonItem(self):
        comparison_item = self.__generate_token_query_request_comparison_item_list()
        comparison_item = """\"comparisonItem":[""" + comparison_item + """],"""
        return comparison_item

    def __generate_token_query_request(self):
        token_query_request = \
            self.__generate_token_query_request_comparisonItem() + """\"category":0,"property":"\""""
        token_query_request = "{" + token_query_request + "}"
        return token_query_request

    # Fetch a token for a google trends query, this is needed to get csv data on the query
    def __get_token(self):
        token_curl = pycurl.Curl()
        token_address = "https://trends.google.com/trends/api/explore?"
        token_query = urllib.parse.urlencode(
            {"hl": "en-US", "tz": self.__tz,
             "req": self.__generate_token_query_request()})

        token_url = token_address + token_query
        token_curl.setopt(pycurl.URL, token_url)
        token_curl.setopt(pycurl.HTTPHEADER, self.__default_token_header)
        # get body as string
        response = token_curl.perform_rs()
        token_curl.close()
        # use first token in response
        self.__token = response.split("\"token\":\"")[1]
        self.__token = self.__token.split("\",")[0]

    # generates the csv query request string time component
    def __generate_csv_query_request_time(self):
        resolution = {
            "1-H": "MINUTE", "4-H": "MINUTE", "1-d": "EIGHT_MINUTE",
            "7-d": "HOUR", "1-m": "DAY", "3-m": "DAY",
            "12-m": "WEEK", "5-y": "WEEK"
        }
        interval_unit = {
            "H": "hours", "d": "days", "m": "months", "y": "years"
        }
        interval_keyword = interval_unit.get(self.__time_range.split("-")[1])
        interval_quantity = int(self.__time_range.split("-")[0])
        start_date_time = \
            datetime.now(timezone.utc) \
            - relativedelta(
                **{interval_keyword: interval_quantity}
                            )

        if resolution.get(self.__time_range) in {"MINUTE", "EIGHT_MINUTE", "HOUR"}:
            start_date_time = start_date_time.strftime("%Y-%m-%dT%H\\\\:%M\\\\:%S")
            end_date_time = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H\\\\:%M\\\\:%S")
        else:
            start_date_time = start_date_time.strftime("%Y-%m-%d")
            end_date_time = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        return """
        "time":"%s %s",
        "resolution":"%s"
        """ % (start_date_time, end_date_time, resolution.get(self.__time_range))

    def __generate_csv_query_request_comparison_item_list_geo(self):
        if self.__geo != "":
            return """\"country":"%s\"""" % self.__geo
        else:
            return ""

    def __generate_csv_query_request_comparison_item_list(self):
        comparison_item_list = ""
        for kw in self.__keywords:
            comparison_item_list += """
            {
                "geo":{%s},
                "complexKeywordsRestriction":{
                    "keyword":[
                        {
                            "type":"BROAD",
                            "value":"%s"
                        }
                    ]
                }
            },
            """ % (self.__generate_csv_query_request_comparison_item_list_geo(), kw)
        # Last character is unneeded comma, slice:
        return "[%s]" % comparison_item_list[:-1]

    def __generate_csv_query_request_request_options(self):
        backends = {"1-H": "CM", "4-H": "CM", "1-d": "CM",
                    "7-d": "CM", "1-m": "IZG", "3-m": "IZG",
                    "12-m": "IZG", "5-y": "IZG"}
        select_backend = backends.get(self.__time_range)
        return """{"property":"","backend":"%s","category":0}""" % select_backend

    def __generate_csv_query_request(self):
        csv_query_request = """
        {%s,"locale":"en-US","comparisonItem":%s,\"requestOptions":%s}
        """ % (self.__generate_csv_query_request_time(),
               self.__generate_csv_query_request_comparison_item_list(),
               self.__generate_csv_query_request_request_options())
        return csv_query_request

    def __get_csv(self):
        csv_address = """https://trends.google.com/trends/api/widgetdata/multiline/csv?"""
        csv_query = urllib.parse.urlencode(
            {"req": self.__generate_csv_query_request(),
             "token": self.__token, "tz": self.__tz})

        request_curl = pycurl.Curl()
        request_curl.setopt(pycurl.URL, csv_address + csv_query)
        request_curl.setopt(pycurl.HTTPHEADER, self.__default_csv_header)

        response_string = request_curl.perform_rs()
        request_curl.close()
        # Delete top two lines of response, ready for conversion to DataFrame
        response_string = re.sub(".*?\n\n", "", response_string)
        # Put response into buffer DataFrame
        response_io_string = io.StringIO(response_string)
        self.__trends_data_buffer = pandas.read_csv(response_io_string, sep=",")

    def scrape_trend(
            self, keywords, geo="", time_range="12-m",
            tz="0", save_file="", retry=True, simple_indexes=True):
        self.__keywords = keywords
        self.__geo = geo
        self.__time_range = time_range
        self.__tz = tz

        self.__get_token()

        fetch_fail = True
        retry_csv = 0
        retry_token = 0

        # First retry fetching CSV, if this fails again, retry fetching token:
        while fetch_fail:
            self.__get_csv()
            if retry == False:
                break
            if self.__trends_data_buffer.empty:
                fetch_fail = True
            else:
                fetch_fail = False
            if retry_csv >= 1:
                retry_csv = -1
                retry_token += 1
                # print("get_token retry %s" % retry_token)
                self.__get_token()
            retry_csv += 1
            # print("get_csv retry %s" % retry_csv)

        # make the first index "date_time" and the following columns simply
        # their keywords. Replace "<1" with "1", convert all entries to
        # integers
        if simple_indexes:
            # make first column name simply "date_time"
            self.__trends_data_buffer.rename(
                columns={self.__trends_data_buffer.columns[0]: "date_time"},
                inplace=True)
            # make column names just the keyword
            for n in self.__trends_data_buffer.columns:
                self.__trends_data_buffer.rename(columns={n: n.split(":")[0]},
                                                 inplace=True)
            # set "date_time" column as index
            self.__trends_data_buffer.set_index("date_time", inplace=True)

            # sanitise for "<1"
            for i in self.__trends_data_buffer.columns:
                self.__trends_data_buffer[i] = [str(x).split("<")[-1] if str(x).find("<") != -1 else str(x) for x in self.__trends_data_buffer[i]]
            #convert al values back to integers
            for i in self.__trends_data_buffer.columns:
                self.__trends_data_buffer[i] = [int(x) for x in self.__trends_data_buffer[i]]

        self.trends_data = self.__trends_data_buffer.copy()

        if save_file != "":
            self.trends_data.to_csv(save_file)

    def __init__(self):
        self.__keywords = ""
        self.__geo = ""
        self.__time_range = ""
        self.__tz = ""

        self.trends_data = pandas.DataFrame()

        if TrendsFetcher.__cookie == "":
            self.__get_cookie()
        self.__default_token_header.append("Cookie: " + self.__cookie)