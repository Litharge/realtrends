import io
import re
import urllib.parse

import pandas
import pycurl
import pycountry

# "hl" = "host language", "tz" = "timezone"
# For an explanation of structure see CurlRequestPatternsAndNotes, particularly the 22072020 examples

class TrendsFetcher:
    cookie = ""
    keywords = []
    token = ""
    geo = ""
    trends_data = ""

    # Temporary headers taken from firefox on my machine
    default_cookie_header = [
        "User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0",
        "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language: en-GB,en;q=0.5",
        "Connection: keep-alive",
        "Upgrade-Insecure-Requests: 1",
        "Cache-Control: max-age=0"
    ]

    default_token_header = [
        'User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0',
        'Accept: application/json, text/plain, */*',
        'Accept-Language: en-GB,en;q=0.5',
        'Connection: keep-alive',
        'Referer: https://trends.google.com/trends/explore?q=snow&geo=US',
        # note that referer has a chance of being important, servers can block requests
        # without proper referer data. A member variable should be set to an initial
        # value and updated each time keyword is changed. TODO
        'TE: Trailers'
    ]

    default_csv_header = [
        'User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0',
       'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
       'Accept-Language: en-GB,en;q=0.5',
       'Connection: keep-alive',
       'Referer: https://trends.google.com/trends/explore?q=snow&geo=US',#note that this has a chance of being important, servers can block requests
        #without proper referer data. A member variable should be set to an initial value and updated each time keyword is changed. TODO
       'Upgrade-Insecure-Requests: 1',
       'TE: Trailers'
    ]

    # Fetch a cookie, this is needed to fetch a token
    def getCookie(self):
        cookieCurl = pycurl.Curl()

        cookieCurl.setopt(pycurl.URL, 'https://trends.google.com/trends/explore?geo=US&q=snow')
        cookieCurl.setopt(pycurl.HTTPHEADER, self.default_cookie_header)

        byteData = io.BytesIO()
        cookieCurl.setopt(pycurl.WRITEHEADER, byteData)

        cookieCurl.perform_rb()
        cookieCurl.close()
        # convert header into a string and perform regex to extract cookie
        headerStr = byteData.getvalue().decode("utf8")

        match_obj = re.search(r"Set-Cookie:.*?;", headerStr)
        match_obj = re.search(r"NID.*?;", match_obj.group(0))

        self.cookie = match_obj.group(0)


    def generate_token_query_request_comparison_item_list(self):
        comparison_item_list = ""
        for kw in self.keywords:
            comparison_item_list_element = """\"keyword":"%s",\"geo":"%s","time":"today 12-m\"""" % (kw, self.geo)
            comparison_item_list_element = "{" + comparison_item_list_element + "},"
            comparison_item_list += comparison_item_list_element
        # Return the list except the last character, which is an unneeded comma
        return comparison_item_list[:-1]

    def generate_token_query_request_comparisonItem(self):
        comparison_item =  self.generate_token_query_request_comparison_item_list()
        comparison_item = """\"comparisonItem":[""" + comparison_item + """],"""
        return comparison_item

    def generate_token_query_request(self):
        token_query_request = self.generate_token_query_request_comparisonItem() + """\"category":0,""" + """\"property":"\""""
        token_query_request = "{" + token_query_request + "}"
        return token_query_request
    # Fetch a token for a google trends query, this is needed to get csv data on the query
    def get_token(self):
        token_curl = pycurl.Curl()
        token_address = "https://trends.google.com/trends/api/explore?"
        token_query = urllib.parse.urlencode({"hl":"en-US", "tz":"60", "req":self.generate_token_query_request()})

        token_URL = token_address + token_query
        # set URL to request from, hard coded for now
        token_curl.setopt(pycurl.URL, token_URL)
        token_curl.setopt(pycurl.HTTPHEADER, self.default_token_header)
        # get body as string
        response = token_curl.perform_rs()
        token_curl.close()
        #search for first token in response
        token_match_obj = re.search(r"\"token\":.*?,", response)
        # remove starting "token":"
        self.token = re.sub(r"\"token\":.*?\"", '', token_match_obj.group(0))
        # remove trailing ",
        self.token = re.sub(r"\",", '', self.token)


    def generate_csv_query_request_time(self):
        return """
        "time":"2019-07-23 2020-07-23",
        "resolution":"WEEK"
        """

    def generate_csv_query_request_locale(self):
        return """
        "locale":"en-US"
        """

    # use pycountry to translate country to country code
    def generate_csv_query_request_comparison_item_list_geo(self):
        if self.geo != "":
            return """\"country":"%s\"""" % self.geo
        else:
            return ""

    def generate_csv_query_request_comparison_item_list(self):
        comparison_item_list = ""
        for kw in self.keywords:
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
            """ % (self.generate_csv_query_request_comparison_item_list_geo(), kw)
        # Return the list except the last character, which is an unneeded comma
        return comparison_item_list[:-1]

    def generate_csv_query_request_comparison_item(self):
        comparison_item = """
        "comparisonItem":[
        """
        comparison_item += self.generate_csv_query_request_comparison_item_list()
        comparison_item += "]"
        return comparison_item

    def generate_csv_query_request_request_options(self):
        return """\"requestOptions":{"property":"","backend":"IZG","category":0}"""

    def generate_csv_query_request(self):
        csv_query_request = "{%s,%s,%s,%s}" % (self.generate_csv_query_request_time()
        , self.generate_csv_query_request_locale()
        , self.generate_csv_query_request_comparison_item()
        , self.generate_csv_query_request_request_options())
        return csv_query_request

    def get_csv(self, save_file = ""):
        csv_address = """https://trends.google.com/trends/api/widgetdata/multiline/csv?"""
        csv_query = urllib.parse.urlencode({"req":self.generate_csv_query_request(), "token":self.token, "tz":"-60"})

        requestCurl = pycurl.Curl()
        requestCurl.setopt(pycurl.URL, csv_address + csv_query)
        requestCurl.setopt(pycurl.HTTPHEADER, self.default_csv_header)

        # If no save file is given, put the data into member trends_data DataFrame
        if save_file == "":
            response_string = requestCurl.perform_rs()
            requestCurl.close()
            # Delete top two lines of response, ready for conversion to DataFrame
            response_string = re.sub(".*?\n\n", "", response_string)
            # Produce StringIO object from response, put into DataFrame and return
            response_IO_string = io.StringIO(response_string)
            response_DF = pandas.read_csv(response_IO_string, sep=",")
            return response_DF
        else:
            pass
            file = open(save_file, "wb")
            requestCurl.setopt(pycurl.WRITEDATA, file)
            requestCurl.perform()
            requestCurl.close()


    def scrape_trend(self, keywords, geo = ""):
        self.keywords = keywords
        self.geo = geo

        self.get_token()
        self.trends_data = self.get_csv()
        print(self.trends_data)
        return self.trends_data

    def __init__(self):
        self.getCookie()
        self.default_token_header.append("Cookie: " + self.cookie)