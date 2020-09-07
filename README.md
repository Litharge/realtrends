# realtrends
A package to scrape google trends and estimate absolute (real) search volumes of given
terms.  Data is presented as a DataFrame.

## Install
```
pip install realtrends
```

## Example

### Get real search volumes

from realtrends import RealTrendsFetcher


### Relative

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

### *real_fetch* Module

```
def scrape_real(self, search_term, geo="", time_range="1-H",
                    tz="0", save_file="", retry=True,
                    ladder = ["englishcombe", "bathampton", "keynsham", "chippenham", "swindon", "bath", "london"]):
```

member function puts real search volumes into

```
self.real_trends_data
```

### *fetch* Module

If you only want relative search volumes

```
def scrape_trend(
            self, keywords, geo="", time_range = "12-m",
            tz="0", save_file="", retry=True)
```
member function puts csv data into
```
self.trends_data
```

#### Parameters
**keywords : list** \
Up to 5 search terms to compare

#### Keyword (Named) Parameters
**geo : string** \
A country code. eg "GB" for Great Britain. By default empty,
indicating global trends

**time\_range : string** \
A time range to get trends data across. 
"1-H" past 60 minutes, 
"4-H" past 240 minutes, 
"1-d" past 180 * 8 minute intervals, 
"7-d" past 7 days, 
"1-m" past 30 days, 
"3-m" past 90 days, 
"12-m" past 52 weeks

**tz : string** \
Timezone relative to UTC in minutes. Default = "0"

**save\_file : string** \
File to write CSV response to, if empty (default) no
file is written to

**retry : boolean** \
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
Get absolute search volumes (hence realtrends) \
Persistently store search volumes (needs absolute volume to be feasible)

## Caveats (and there are a few right now...)

### The default *ladder* only works for geo="" or geo="GB"

This package relies on inferring absolute (or *real*, the terms may be used 
interchangably, in the program "absolute" or "abs" is used everywhere except
function names, this is due to visual similarity with "rel") search term
volumes entered into Google Search over some time period.

In order to make this inference, a list called a *ladder* is needed. This is a list of
terms increasing in search magnitude, which the algorithm runs up until a term
of comparable, but less, search magnitude is found. 

The exact terms in the ladder is not important. But using population centres
gives a reliable estimate of relative magnitudes because we know their
populations and the number of searches is going to be in some way proportional
to this number.

The default ladder is
```
ladder = ["englishcombe", "bathampton", "keynsham", "chippenham", "swindon", "bath", "london"]
```
which works for worldwide (geo="") or UK (geo="GB" searches, as the number of 
searches for "englishcombe" in the world or UK is both small (>10) and nonzero. 

The default ladder will not work for other countries, eg Angola (geo="AO") as
"englishcombe", "bathampton" etc are never searched in Angola.

If you want to know about real search volumes in Angola, use google maps to
find a hamlet, village, town, smaller city, capital (or something else, this
is up to the user) and pass this list as the ladder keyword parameter

### Real volumes are only applicable for 1-H, 4-H or (potentially) 1-d

This is because the time increments increase as the interval increases: 1 min,
1 min, 8 min then hour. The problem here is that the first item in the ladder
will probably be searched many times within 1 hour.

If you really want longer intervals, for now you would need to store the
results

### The results wont be very accurate

todo: testing section

I am working on improving the accuracy of the results, how accurate they are
right now is difficult to determine, as Google only provides very limited real
search volmues to test with. These are on the "trending" section, though these 
figures are for *topics*, rather than search terms. I have done some testing and 
I feel the results are probably within +-20% of the true figure, I will be 
adding a testing section to demonstrate this soon.

Results are likely to be more accurate for smaller intervals: 1-H or 4-H


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
