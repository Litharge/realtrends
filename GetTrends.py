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


def getToken(cookie):
    # create pycurl object with the purpose of getting token
    tokenCurl = pycurl.Curl()
    # set URL to request from, hard coded for now
    tokenCurl.setopt(pycurl.URL,
                     'https://trends.google.com/trends/api/explore?hl=en-US&tz=-60&req=%7B%22comparisonItem%22:%5B%7B%22keyword%22:%22snow%22,%22geo%22:%22US%22,%22time%22:%22today+12-m%22%7D%5D,%22category%22:0,%22property%22:%22%22%7D&tz=-60')
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
    # remove starting: "token":"
    token = re.sub(r"\"token\":.*?\"", '', token_match_obj.group(0))
    # remove trailing: ",
    token = re.sub(r"\",", '', token)

    #print(token)
    return token

def getCSV(token):
    #start and end components are not percent encoded
    URL_string_start = """https://trends.google.com/trends/api/widgetdata/multiline/csv?req="""
    URL_string_end = "&token="
    URL_string_end = URL_string_end + token
    URL_string_end = URL_string_end + "&tz=-60"
    # URL_string_mid contains request data
    # Notes for infering dynamic structure
    #
    URL_string_mid = """
    {
    "time":"2019-07-18 2020-07-18",
    "resolution":"WEEK",
    "locale":"en-US",
    "comparisonItem":[
        {"geo":{"country":"US"},
        "complexKeywordsRestriction":{"keyword":[{"type":"BROAD","value":"snow"}]}}
    ],
    "requestOptions":{"property":"","backend":"IZG","category":0}
    }
    """
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

    response_string = requestCurl.perform_rs()
    print(response_string)
    requestCurl.close()
    # Clean top two lines of response, ready for conversion to datafram
    response_string = re.sub(".*?\n\n", "", response_string)
    response_IO_string = io.StringIO(response_string)
    response_DF = pandas.read_csv(response_IO_string, sep=",")

    return response_DF

# main

# get cookie
cookie = getCookie()
for i in range(1):
    #use cookie to get token
    token = getToken(cookie)
    # use token to get data
    trendsData = getCSV(token)
    print(trendsData)
