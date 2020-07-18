import pycurl
import io
import re
import urllib.parse
import pandas


# return a string containing the cookie
# for now use word = snow, geo = US
def getCookie():
    """
    curl 'https://trends.google.com/trends/explore?geo=US&q=snow,ice'
    -H 'User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0'
    -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
    -H 'Accept-Language: en-GB,en;q=0.5'
    --compressed
    -H 'Connection: keep-alive'
    -H 'Upgrade-Insecure-Requests: 1'
    -H 'Cache-Control: max-age=0'
    """
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
    # remove : ",
    token = re.sub(r"\",", '', token)

    print(token)

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
    #print(URL_string_mid)
    URL_string_mid = urllib.parse.quote(URL_string_mid)


    URL_string = URL_string_start + URL_string_mid + URL_string_end

    print(URL_string)

    requestCurl = pycurl.Curl()

    requestCurl.setopt(pycurl.URL, URL_string)#"""https://trends.google.com/trends/api/widgetdata/multiline/csv?req=%7B%22time%22%3A%222019-07-18%202020-07-18%22%2C%22resolution%22%3A%22WEEK%22%2C%22locale%22%3A%22en-US%22%2C%22comparisonItem%22%3A%5B%7B%22geo%22%3A%7B%22country%22%3A%22US%22%7D%2C%22complexKeywordsRestriction%22%3A%7B%22keyword%22%3A%5B%7B%22type%22%3A%22BROAD%22%2C%22value%22%3A%22snow%22%7D%5D%7D%7D%5D%2C%22requestOptions%22%3A%7B%22property%22%3A%22%22%2C%22backend%22%3A%22IZG%22%2C%22category%22%3A0%7D%7D&token=APP6_UEAAAAAXxR9t6qP61XMfH3dvF1L_3H7jXzPqPHw&tz=-60""")

    requestCurl.setopt(pycurl.HTTPHEADER,
                       [
                           'User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0',
                           'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                           'Accept-Language: en-GB,en;q=0.5',
                           'Connection: keep-alive',
                           'Referer: https://trends.google.com/trends/explore?q=snow&geo=US',
                           #'Cookie: 1P_JAR=2020-7-18-17; NID=204=XsOVdqWxmhMpR7hWFNMMegW95loBh6DqxjnXDi-HEAV0oVF8MOZjh-3kMB4XBIWL7RjKUzszfSNV15y2_OyU0ii35eu0WBQ0Fdzf-xmSGR2uhHrd6cn6Fetf38_WnSjEF5-tv3fNWdI009rv8ORY1WQWbYOkB06Wi2vkhKbk0oNf-i1gmCKwpm6YWbykIvCdQj1cT0KPOjJkl8jjaWRMDViuHqqn7k16NMNerzE; CONSENT=YES+GB.en+20150628-20-0; SID=zQdxhWZXVAG4ztSsKQkNnAKTz8jSihV0Mv8ovjJuyPaVFymp1zCqncEyVhlY-ocb8Y2EwA.; __Secure-3PSID=zQdxhWZXVAG4ztSsKQkNnAKTz8jSihV0Mv8ovjJuyPaVFympIb44UNy6Ht3DYwe9CNPU2A.; HSID=ARQPoRWzpPDn7fzrL; SSID=Al4mTEuoHnYHBXHKM; APISID=xtGNEU-toLmxwouh/A1qE8BSejCJPmebN5; SAPISID=oXMtIf1QHaJbrP7m/AZDt9yzMXYHsuP6j8; __Secure-HSID=ARQPoRWzpPDn7fzrL; __Secure-SSID=Al4mTEuoHnYHBXHKM; __Secure-APISID=xtGNEU-toLmxwouh/A1qE8BSejCJPmebN5; __Secure-3PAPISID=oXMtIf1QHaJbrP7m/AZDt9yzMXYHsuP6j8; SIDCC=AJi4QfG5ff-SCoOOJY69p_vngOAG2fSASfCLXHZaLJMQi64c3uv-DkYMqnrb8lSPhWSuy6kqXCc'
                           'Upgrade-Insecure-Requests: 1',
                           'TE: Trailers'
                       ]
                       )
    requestCurl.perform()
    requestCurl.close()

# main

# get cookie
cookie = getCookie()
for i in range(3):
    # use cookie to get token
    token = getToken(cookie)
    # use token to get data
    getCSV(token)
