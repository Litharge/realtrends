import io
import re
import urllib.parse
from datetime import datetime, timezone

import pandas
import pycurl
from dateutil.relativedelta import relativedelta


# "hl" = "host language", "tz" = "timezone"
# For an explanation of structure see CurlRequestPatternsAndNotes, particularly the 22072020 examples

class TrendsFetcher:
    __keywords = []
    __geo = ""
    __time_range = ""
    __tz = ""

    __cookie = ""
    __token = ""

    trends_data = ""

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
        # convert header into a string and perform regex to extract cookie
        header = byte_data.getvalue().decode("utf8")

        match_obj = re.search(r"Set-Cookie:.*?;", header)
        match_obj = re.search(r"NID.*?;", match_obj.group(0))

        self.__cookie = match_obj.group(0)

    def __generate_token_query_request_comparison_item_list(self):
        time_phrase = {
            "1-H": "now 1-H", "4-H": "now 4-H", "1-d": "now 1-d",
            "7-d": "now 7-d", "1-m": "today 1-m", "3-m": "today 3-m",
            "12-m": "today 12-m", "5-y": "today 1-y",
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
        comparison_item =  self.__generate_token_query_request_comparison_item_list()
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
        token_query = urllib.parse.urlencode({"hl":"en-US", "tz":self.__tz, "req":self.__generate_token_query_request()})

        token_URL = token_address + token_query
        # set URL to request from, hard coded for now
        token_curl.setopt(pycurl.URL, token_URL)
        token_curl.setopt(pycurl.HTTPHEADER, self.__default_token_header)
        # get body as string
        response = token_curl.perform_rs()
        token_curl.close()
        # search for first token in response
        token_match_obj = re.search(r"\"token\":.*?,", response)
        # remove starting "token":"
        self.__token = re.sub(r"\"token\":.*?\"", '', token_match_obj.group(0))
        # remove trailing ",
        self.__token = re.sub(r"\",", '', self.__token)


    def __generate_csv_query_request_time(self):
        resolution = {
            "1-H": "MINUTE", "4-H": "MINUTE", "1-d": "EIGHT_MINUTE",
            "7-d": "HOUR", "1-m": "DAY", "3-m": "DAY",
            "12-m": "WEEK", "5-y": "WEEK"
        }
        # For high resolutions, hours, minutes and seconds must be passed in the query
        if resolution.get(self.__time_range) in {"MINUTE", "EIGHT_MINUTE", "HOUR"}:
            # Use number from time_range to give delta
            if self.__time_range[-1] == "H":
                start_date_time = datetime.now(timezone.utc) \
                                  - relativedelta(hours=int(self.__time_range[:self.__time_range.index("-")]))
            if self.__time_range[-1] == "d":
                start_date_time = datetime.now(timezone.utc) \
                                  - relativedelta(days=int(self.__time_range[:self.__time_range.index("-")]))

            start_date_time = start_date_time.strftime("%Y-%m-%dT%H\\\\:%M\\\\:%S")
            end_date_time = datetime.now(timezone.utc)
            end_date_time = end_date_time.strftime("%Y-%m-%dT%H\\\\:%M\\\\:%S")
        else:
            # Use number from time_range to give delta
            if self.__time_range[-1] == "m":
                start_date_time = datetime.now(timezone.utc) \
                                  - relativedelta(months=int(self.__time_range[:self.__time_range.index("-")]))
            if self.__time_range[-1] == "y":
                start_date_time = datetime.now(timezone.utc) - relativedelta(years=5)

            start_date_time = start_date_time.strftime("%Y-%m-%d")
            end_date_time = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        return """
        "time":"%s %s",
        "resolution":"%s"
        """ % (start_date_time, end_date_time, resolution.get(self.__time_range))

    # use pycountry to translate country to country code
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
        # Return crotchet enclosed list except the last character, an unneeded comma
        return "[" + comparison_item_list[:-1] + "]"

    def __generate_csv_query_request_request_options(self):
        backends = {"1-H":"CM","4-H":"CM","1-d":"CM",
                    "7-d":"CM","1-m":"IZG","3-m":"IZG",
                    "12-m":"IZG","5-y":"IZG"}
        select_backend = backends.get(self.__time_range)
        return """{"property":"","backend":"%s","category":0}""" % select_backend

    # TODO: put context back in here, only values should be returned by functions for uniformity and clarity
    def __generate_csv_query_request(self):
        csv_query_request = """
        {%s,"locale":"en-US","comparisonItem":%s,\"requestOptions":%s}
        """ % (self.__generate_csv_query_request_time()
        #, self.__generate_csv_query_request_locale()
        , self.__generate_csv_query_request_comparison_item_list()
        , self.__generate_csv_query_request_request_options())
        return csv_query_request

    def __get_csv(self, save_file = ""):
        csv_address = """https://trends.google.com/trends/api/widgetdata/multiline/csv?"""
        csv_query = urllib.parse.urlencode({"req":self.__generate_csv_query_request(), "token":self.__token, "tz":self.__tz})

        requestCurl = pycurl.Curl()
        requestCurl.setopt(pycurl.URL, csv_address + csv_query)
        requestCurl.setopt(pycurl.HTTPHEADER, self.__default_csv_header)

        # If no save file is given, put the data into self.trends_data DataFrame and return it
        if save_file == "":
            response_string = requestCurl.perform_rs()
            requestCurl.close()
            # Delete top two lines of response, ready for conversion to DataFrame
            response_string = re.sub(".*?\n\n", "", response_string)
            # Produce StringIO object from response, put into DataFrame and return
            response_IO_string = io.StringIO(response_string)
            self.trends_data = pandas.read_csv(response_IO_string, sep=",")
            return self.trends_data
        else:
            file = open(save_file, "wb")
            requestCurl.setopt(pycurl.WRITEDATA, file)
            requestCurl.perform()
            requestCurl.close()

    # Primary member function. Takes up to 5 keywords as a list in (keywords)
    # and optional arguments: country code as a string in [geo], time range
    # as a string in [time_range], country to take timezone of in [timezone]
    # OR if timezone_override == True takes timezone of form (+/-)(hours) in
    # timezone. If timezone_override == False, timezone is calculated
    # automatically from the country, including daylight savings.
    # Defaults to worldwide trend over the past 12 months, with UTC timezone:
    # +0
    # 1-H = past hour, 4-h = past 4 hours, 1-d = past day, 5-d = past 5 days
    # 1-m = past month, 3-m = past 3 months, 12-m = 12 months
    def scrape_trend(self, keywords, geo = "", time_range = "12-m", tz = "0"):
        self.__keywords = keywords
        self.__geo = geo
        self.__time_range = time_range
        self.__tz = tz

        self.__get_token()
        self.trends_data = self.__get_csv()
        print(self.trends_data)
        return self.trends_data

    def __init__(self):
        self.__get_cookie()
        self.__default_token_header.append("Cookie: " + self.__cookie)