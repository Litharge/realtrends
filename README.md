# realtrends
A package to scrape Google Trends and estimate absolute (real) search volumes
of given terms.  Data is presented as a DataFrame.

## Install
```
pip install realtrends
```

## Examples

### Get real search volumes

Get real search volumes for "rain" amongst UK searchers over past day. Print
the results and cumulative searches.
```
from realtrends import RealTrendsFetcher
test_real_fetcher = RealTrendsFetcher()
test_real_fetcher.scrape_real("rain", geo="GB", time_range="1-d")
print(test_real_fetcher.real_trends_data)
print(int(test_real_fetcher.real_trends_data.sum()))
```

### Relative

Get relative search volumes for "sunhats" vs "snow" amongst US searchers 
over the past day, where the user's time zone is central = UTC-0600 = -360 in 
minutes. Print the result.
```
from realtrends import TrendsFetcher
my_test_fetcher = TrendsFetcher()
my_test_fetcher.scrape_trend(
			    ["sunhats","snow"], geo="US",
			    time_range="1-d", tz="-360")
print(my_test_fetcher.trends_data)
```

## Usage

### *real_fetch* Module

```
def scrape_real(self, search_term, geo="", time_range="1-H",
                tz="0", save_file="", retry=True,
                ladder = ["englishcombe", "bathampton", "keynsham", 
		"chippenham", "swindon", "bath", "london"]):
```

member function puts real search volumes into

```
self.real_trends_data
```

#### Parameters
**search\_term : string** \
Search term to fetch real volume data for

#### Keyword (Named) Parameters
**geo : string** \
A country code. eg "GB" for United Kingdom. By default empty,
indicating global trends

**time\_range : string** \
A time range to get trends data across.   
"1-H" past 60 minutes,   
"4-H" past 240 minutes,   
"1-d" past 180 * 8 minute intervals,   
Note: real volumes past this point are likely to be unreliable, see Caveats 
below  
"7-d" past 7 days,   
"1-m" past 30 days,   
"3-m" past 90 days,   
"12-m" past 52 weeks  

**tz : string** \
Timezone relative to UTC in minutes. Default = "0"


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
A country code. eg "GB" for United Kingdom. By default empty,
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

## Features v1.1 (current) 
* real\_fetch module supports finding real search volumes for a given search
  term
* fetch module supports up to 5 search terms
* Any country code may be used (in the case of real\_fetch, see Caveats below)
* fetch module supports optional save file
* Optional automatic retry if request fails (mandatory for real\_fetch module)

## Planned Features
Persistently store search volumes   
Automatically fetch ladder   
Allow search topics to be compared  

## Caveats (and there are a few right now...)

### The default *ladder* only works for geo="" or geo="GB"

This package relies on inferring absolute (or *real*, the terms may be used
interchangably, in the program "absolute" or "abs" is used everywhere except
function names, this is due to visual similarity with "rel") search term
volumes entered into Google Search over some time period

In order to make this inference, a list called a *ladder* is needed. This is a
list of terms increasing in search magnitude, which the algorithm runs up until
a term of comparable, but less, search magnitude is found 

The exact terms in the ladder is not important. But using population centres
gives a reliable estimate of relative magnitudes because we know their
populations and the number of searches is going to be in some way proportional
to this number

The default ladder is
```
ladder = ["englishcombe", "bathampton", "keynsham", "chippenham", "swindon", "bath", "london"]
```
which works for worldwide (geo="") or UK (geo="GB" searches, as the number of
searches for "englishcombe" in the world or UK is both small (>10) and nonzero 

The default ladder will not work for other countries, eg Angola (geo="AO") as
"englishcombe", "bathampton" etc are never searched in Angola

If you want to know about real search volumes in Angola, use Google Maps to
find a hamlet, village, town, smaller city, capital (or something else, this is
up to the user) and pass this list as the ladder keyword parameter

### Real volumes are only applicable for 1-H, 4-H and 1-d

This is because the time increments increase as the interval increases: 1 min,
1 min, 8 min then hour. The problem here is that the first item in the ladder
will probably be searched many times within 1 hour (or even 8 minutes depending
on what you select as your first ladder item)

If you really want longer intervals, either store the results and update the
volumes by calling scrape\_real() every day. 

However, longer intervals can be passed to scrape\_real() if the user so
chooses

### The results wont be very accurate

todo: testing section

I am working on improving the accuracy of the results, how accurate they are
right now is difficult to determine, as Google only provides very limited real
search volmues to test with. These are on the "Trending Searches" section,
though these figures are for *topics*, rather than search terms. I have done
some testing and I feel the results are probably better than +-20% of the true
figure, I will be adding a testing section to demonstrate this soon as well as
a mathematical determination of accuracy

Results are likely to be more accurate for smaller intervals: 1-H or 4-H



