import pycurl
import io
import re


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
    cookieCurl.perform()
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

    byteData = io.BytesIO()

    tokenCurl.setopt(pycurl.WRITEHEADER, byteData)
    response = tokenCurl.perform()
    tokenCurl.close()






# main

# byteData = io.BytesIO()

cookie = getCookie()

getToken(cookie)
