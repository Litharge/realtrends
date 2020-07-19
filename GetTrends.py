import pycurl
import io
import re
import urllib.parse
import pandas


# return a string containing the cookie
# for now use word = snow, geo = US
def getCookie():
    # Create pycurl object with the purpose of getting cookies
    cookieCurl = pycurl.Curl()
    # Set url to request from, hard coded for now
    cookieCurl.setopt(pycurl.URL, 'https://trends.google.com/trends/explore?geo=US&q=snow')
    # Set header values, hard coded for now
    cookieCurl.setopt(pycurl.HTTPHEADER,
                      [
                          "User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0",
                          "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                          "Accept-Language: en-GB,en;q=0.5",
                          "Connection: keep-alive",
                          "Upgrade-Insecure-Requests: 1",
                          "Cache-Control: max-age=0"
                      ]
                      )

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
def generate_token_URL_string_mid_comparisonItem_list(keyword):
    comparison_items = "{"
    comparison_items += "\"keyword\":\""
    comparison_items += keyword
    comparison_items += "\","
    comparison_items += "\"geo\":\"US\",\"time\":\"today 12-m\""
    comparison_items += """}"""
    return comparison_items

def generate_token_URL_string_mid_comparisonItem(keyword):
    comparison_item = """
    "comparisonItem":[
    """
    comparison_item +=  generate_token_URL_string_mid_comparisonItem_list(keyword)
    comparison_item += """],"""

    return comparison_item


def generate_token_URL_string_mid_category():
    return """"category":0,"""

def generate_token_URL_string_mid_property():
    return """
    "property":""
    """

def generate_token_URL_string_mid(keyword):
    token_URL_string_mid = """{"""
    token_URL_string_mid += generate_token_URL_string_mid_comparisonItem(keyword)
    token_URL_string_mid += generate_token_URL_string_mid_category()
    token_URL_string_mid += generate_token_URL_string_mid_property()
    token_URL_string_mid += """}"""
    return token_URL_string_mid

def getToken(keyword, cookie):
    # create pycurl object with the purpose of getting token
    tokenCurl = pycurl.Curl()
    token_URL_string_start = "https://trends.google.com/trends/api/explore?hl=en-US&tz=-60&req="
    token_URL_string_end = "&tz=-60"
    token_URL_string_mid = generate_token_URL_string_mid(keyword)

    token_URL_string_mid = urllib.parse.quote(token_URL_string_mid)

    token_URL_string = token_URL_string_start + token_URL_string_mid + token_URL_string_end
    # set URL to request from, hard coded for now
    tokenCurl.setopt(pycurl.URL, token_URL_string)
    # set header values, hard coded for now. Including cookie passed to function
    cookieHeaderString = "Cookie: " + cookie
    tokenCurl.setopt(pycurl.HTTPHEADER,
                     [
                         'User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0',
                         'Accept: application/json, text/plain, */*',
                         'Accept-Language: en-GB,en;q=0.5',
                         'Connection: keep-alive',
                         'Referer: https://trends.google.com/trends/explore?q=snow&geo=US',
                         cookieHeaderString,
                         'TE: Trailers'
                     ]
    )

    # get body
    response = tokenCurl.perform_rs()
    tokenCurl.close()
    #search for first token in response
    token_match_obj = re.search(r"\"token\":.*?,", response)
    # remove starting "token":"
    token = re.sub(r"\"token\":.*?\"", '', token_match_obj.group(0))
    # remove trailing ",
    token = re.sub(r"\",", '', token)

    #print(token)
    return token

def generate_CSV_URL_string_mid_time():
    return """"time":"2019-07-19 2020-07-19",
    "resolution":"WEEK","""

def generate_CSV_URL_string_mid_locale():
    return """"locale":"en-US","""

# it is likely a loop will go in here, it looks like a list of locations and keywords are accepted
def generate_CSV_URL_string_mid_comparisonItem_list(keyword):
    comparison_item_list = """{"geo":{"country":"US"},"complexKeywordsRestriction":{"keyword":[{"type":"BROAD","value":\""""
    comparison_item_list += keyword
    comparison_item_list += """\"}]}}"""
    return comparison_item_list
    return """
    {
        "geo":{"country":"US"},
        "complexKeywordsRestriction":{"keyword":[{"type":"BROAD","value":"snow"}]}
        }
    """

def generate_CSV_URL_string_mid_comparisonItem(keyword):
    comparison_item = """
    "comparisonItem":[
    """
    comparison_item += generate_CSV_URL_string_mid_comparisonItem_list(keyword)
    comparison_item += "],"
    return comparison_item;


def generate_CSV_URL_string_mid_requestOptions():
    return """
        "requestOptions":{"property":"","backend":"IZG","category":0}
        """

def generate_URL_string_mid(keyword):
    URL_string_mid = """{"""
    URL_string_mid += generate_CSV_URL_string_mid_time()
    URL_string_mid += generate_CSV_URL_string_mid_locale()
    URL_string_mid += generate_CSV_URL_string_mid_comparisonItem(keyword)
    URL_string_mid += generate_CSV_URL_string_mid_requestOptions()
    URL_string_mid += """}"""
    return URL_string_mid


def getCSV(keyword, token, save_file = ""):
    #start and end components are not percent encoded
    URL_string_start = """https://trends.google.com/trends/api/widgetdata/multiline/csv?req="""
    URL_string_end = "&token="
    URL_string_end = URL_string_end + token
    URL_string_end = URL_string_end + "&tz=-60"
    # URL_string_mid contains request data
    URL_string_mid = generate_URL_string_mid(keyword)
    # Mid section of URL must use percent encoding
    URL_string_mid = urllib.parse.quote(URL_string_mid)
    # Assemble full URL
    URL_string = URL_string_start + URL_string_mid + URL_string_end

    #print(URL_string)

    requestCurl = pycurl.Curl()

    requestCurl.setopt(pycurl.URL, URL_string)

    requestCurl.setopt(pycurl.HTTPHEADER,
                       [
                           'User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0',
                           'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                           'Accept-Language: en-GB,en;q=0.5',
                           'Connection: keep-alive',
                           'Referer: https://trends.google.com/trends/explore?q=snow&geo=US',
                           'Upgrade-Insecure-Requests: 1',
                           'TE: Trailers'
                       ]
                       )
    #file = open("test.csv", "wb")
    #requestCurl.setopt(pycurl.WRITEDATA, file)
    #DF = pandas.read_csv(requestCurl.perform())
    # If no save file is given, put the data into a dataframe
    if save_file == "":
        response_string = requestCurl.perform_rs()
        requestCurl.close()
        # Clean top two lines of response, ready for conversion to datafram
        response_string = re.sub(".*?\n\n", "", response_string)
        # Produce StringIO object, insert data and return
        response_IO_string = io.StringIO(response_string)
        response_DF = pandas.read_csv(response_IO_string, sep=",")
        return response_DF
    else:
        pass

def get_trend(keyword, cookie):
    token = getToken(keyword, cookie)
    # use token to get data
    trendsData = getCSV(keyword, token)
    return trendsData

# get cookie
cookie = getCookie()

trendsData = get_trend("sunscreen", cookie)
print(trendsData)
