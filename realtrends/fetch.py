import io
import re
import urllib.parse

import pandas
import pycurl
import pycountry

# "hl" = "host language", "tz" = "timezone"

class TrendsFetcher:
    cookie = ""
    keyword = ""
    token = ""
    geo = ""

    default_cookie_header = [
                              "User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0",
                              "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                              "Accept-Language: en-GB,en;q=0.5",
                              "Connection: keep-alive",
                              "Upgrade-Insecure-Requests: 1",
                              "Cache-Control: max-age=0"
                          ]

    default_token_header = ['User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0',
                            'Accept: application/json, text/plain, */*',
                            'Accept-Language: en-GB,en;q=0.5',
                            'Connection: keep-alive',
                            'Referer: https://trends.google.com/trends/explore?q=snow&geo=US',
                            # note that this has a chance of being important, servers can block requests
                            # without proper referer data. A member variable should be set to an initial value and updated each time keyword is changed. TODO
                            'TE: Trailers'
                            ]

    default_csv_header = ['User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0',
                               'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                               'Accept-Language: en-GB,en;q=0.5',
                               'Connection: keep-alive',
                               'Referer: https://trends.google.com/trends/explore?q=snow&geo=US',#note that this has a chance of being important, servers can block requests
                                #without proper referer data. A member variable should be set to an initial value and updated each time keyword is changed. TODO
                               'Upgrade-Insecure-Requests: 1',
                               'TE: Trailers']

    # return a string containing the cookie
    # for now use word = snow, geo = US
    def getCookie(self):
        # Create pycurl object with the purpose of getting cookies
        cookieCurl = pycurl.Curl()
        # Set url to request from, hard coded for now
        cookieCurl.setopt(pycurl.URL, 'https://trends.google.com/trends/explore?geo=US&q=snow')
        # Set header values, hard coded for now
        cookieCurl.setopt(pycurl.HTTPHEADER, self.default_cookie_header)

        byteData = io.BytesIO()

        # provide variable to write header data to, cookie is found in here, then perform the request and close
        cookieCurl.setopt(pycurl.WRITEHEADER, byteData)
        cookieCurl.perform_rb()
        cookieCurl.close()
        # convert header into a string and perform regex to extract cookie
        headerStr = byteData.getvalue().decode("utf8")

        match_obj = re.search(r"Set-Cookie:.*?;", headerStr)
        match_obj = re.search(r"NID.*?;", match_obj.group(0))
        print("\ncookie:")
        print(match_obj.group(0))
        return match_obj.group(0)

    # it is likely a loop will go in here, it looks like a list of locations and keywords are accepted
    # a list could be passed for this purpose
    def generate_token_query_request_comparisonItem_list(self):
        comparison_item_list = """\"keyword":"%s",\"geo":"%s","time":"today 12-m\"""" % (self.keyword, self.geo)
        comparison_item_list = "{" + comparison_item_list + "}"
        return comparison_item_list

    def generate_token_query_request_comparisonItem(self):
        comparison_item =  self.generate_token_query_request_comparisonItem_list()
        comparison_item = """\"comparisonItem":[""" + comparison_item + """],"""

        return comparison_item

    def generate_token_query_request(self):
        token_query_request = self.generate_token_query_request_comparisonItem() + """\"category":0,""" + """\"property":"\""""
        token_query_request = "{" + token_query_request + "}"
        return token_query_request

    def get_token(self):
        # create pycurl object with the purpose of getting token
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
        "time":"2019-07-22 2020-07-22",
        "resolution":"WEEK",
        """

    def generate_csv_query_request_locale(self):
        return """
        "locale":"en-US",
        """

    # use pycountry to translate country to country code
    def generate_csv_query_request_comparison_item_list_geo(self):
        #if self.geo
        return """
        "country":"US"
        """

    # it is likely a loop will go in here, it looks like a list of locations and keywords are accepted
    def generate_csv_query_request_comparison_item_list(self):
        comparison_item_list = """
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
        }
        """ % (self.generate_csv_query_request_comparison_item_list_geo(), self.keyword)

        return comparison_item_list

    def generate_csv_query_request_comparisonItem(self):
        comparison_item = """
        "comparisonItem":[
        """
        comparison_item += self.generate_csv_query_request_comparison_item_list()
        comparison_item += "],"
        return comparison_item

    def generate_csv_query_request_request_options(self):
        return """
            "requestOptions":{"property":"","backend":"IZG","category":0}
            """

    # change these to use urllib and put brace enclose on a single line at the end
    def generate_csv_query_request(self):
        csv_query_request = self.generate_csv_query_request_time()
        csv_query_request += self.generate_csv_query_request_locale()
        csv_query_request += self.generate_csv_query_request_comparisonItem()
        csv_query_request += self.generate_csv_query_request_request_options()
        csv_query_request = "{" + csv_query_request + "}"
        return csv_query_request

    def get_csv(self, save_file = ""):
        csv_address = """https://trends.google.com/trends/api/widgetdata/multiline/csv?"""

        csv_query = urllib.parse.urlencode({"req":self.generate_csv_query_request(), "token":self.token, "tz":"-60"})

        URL_string = csv_address + csv_query

        requestCurl = pycurl.Curl()

        requestCurl.setopt(pycurl.URL, URL_string)

        requestCurl.setopt(pycurl.HTTPHEADER, self.default_csv_header)

        # If no save file is given, put the data into a DataFrame
        if save_file == "":
            response_string = requestCurl.perform_rs()
            requestCurl.close()
            # Clean top two lines of response, ready for conversion to DataFrame
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

    def scrape_trend(self, keyword, geo = ""):
        self.keyword = keyword
        self.geo = geo
        # token is needed to make the CSV request
        self.get_token()
        trends_data = self.get_csv()
        print(trends_data)
        return trends_data

    def __init__(self):
        self.cookie = self.getCookie()
        self.default_token_header.append("Cookie: " + self.cookie)


