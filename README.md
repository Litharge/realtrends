# realtrends
A package to scrape google trends for relative (v1) and absolute (v2) search
volumes of given terms. Data is put into a DataFrame.

## Install
```
pip install realtrends
```

## Example
get relative search popularities for "sunhats" vs "snow" amongst US searchers 
over the past day, where the user's time zone is central = UTC-0600 = -360 in 
minutes. Print the result.
```
from realtrends import TrendsFetcher
my_test_fetcher = TrendsFetcher()
my_test_fetcher.scrape_trend(["sunhats","snow"], geo="US", time_range="1-d", tz="-360")
print(my_test_fetcher.trends_data)
```

## Usage

### *fetch* Module

```
def scrape_trend(
            self, keywords, geo="", time_range = "12-m",
            tz="0", save_file="", retry=True)
```
member function puts csv data into
```
trends_data
```
member DataFrame

#### Parameters:
keywords : list 
Up to 5 search terms to compare

#### Keyword (Named) Parameters
geo : string 
A country code. eg "GB" for Great Britain. By default empty,
indicating global trends

time\_range : string 
A time range to get trends data across. 
"1-H" past 60 minutes, 
"4-H" past 240 minutes, 
"1-d" past 180 * 8 minute intervals, 
"7-d" past 7 days, 
"1-m" past 30 days, 
"3-m" past 90 days, 
"12-m" past 52 weeks

tz : string 
Timezone relative to UTC in minutes. Default = "0"

save\_file : string 
File to write CSV response to, if empty (default) no
file is written to

retry : boolean 
Decide whether to automatically retry if the server fails
to send CSV data. Default is True

## Features
v1.0 (current) 
Scrape trends directly from google trends:
* Supports up to 5 search terms
* Any country code may be used
* Optional save file
* Optional automatic retry if request fails

## Planned Features
Get absolute search volumes (hence realtrends)
Persistently store search volumes (needs absolute volume to be feasible)

MIT License

Copyright (c) [2020] [Robert Chambers]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
