# Data

**Author:** Diego A. Guerrero

**Last Edit:** 02/19/2018.

**NOTICE:** All datasets are original content, available for free. Please make good use of it and quote.
**Note:** Individual level data is not available anymore due to storage space limitations.


## Venezuelan Prices Tracker

File: price_index.csv

![CPI](https://raw.githubusercontent.com/guerreroda/data/master/price_index.png)

### Methodology.
#### Liquor prices
- An online Venezuelan liquor store is scraped daily for all its products and prices since July 2017. Week 2017-09-10 is missing for all values.
- The dataset comprises a panel with i=3,411 and t=135, by this date.
- There is attrition in products due scarcity and inventory. I track data for each item and am able to follow scarcity in alcohol.
- The data is resampled in weekly frequency.
- From all products, 574 items have less than 2 missing value. 11 of those are selected as a bundle.
- The following (arbitrary) weights were applied to construct a CPI:

| Low Price (80%)  | Mid. Price (15%) | High Price (5%) |
| ---------------- | ---------------- | --------------- |
| 'cerveza-tovar-pilsen'  | 'ron-cacique-500-anos'  | 'whisky-black-label-media-botella-media-botella' |
| 'vodka-bajo-cero' | 'ron-santa-teresa-1796'  | whisky-chivas-regal-12-anos' |
| 'ron-cacique' | 'vino-la-huerta-merlot'  | 'ron-cacique-antiguo' |
| 'ron-angostura' | 'vino-santa-carolina-cabernet'  | |

#### Restaurant prices
- Since February 2018, prices are scraped daily from an online store with a variety of restaurant menus available (including fast-food).
- Products were categorized from low, mid and high price according to their prices' percentile level in February and they were weighted (80% of bundle is comprised of 8 low-price products, 16% from 8 mid-price products, and 4% from highly priced 4 products.

Resulting data is uploaded as price_index.csv

| Date | Alcohol | Inf. | Restaurants | Inf. |
| ---- | ----- | ---- | ---- | ---- |
| Jul-17 | 2.19 | NaN | | |
| Aug-17 | 3.12 | 42% | | |
| Sep-17 | 4.89 |	57% | | |
| Oct-17 | 10.34 | 111% | | |
| Nov-17 | 21.89 |	112% | | |
| Dec-17 | 59.97 | 174% | | |
| Jan-18 | 67.08 | 12% | | |
| Feb-18 | 100 | 49% | 100 | NaN |
| Mar-18 | 118.89 | 19% | 143.37 | 43% |
| Apr-18 | 147.35 | 24% | 231.84 | 61% |
| May-18 | 277.64 | 88% | 430.13 | 86% |
| Jun-18 | 850.91 | 206% | 790.83 | 85% |
| Jul-18 | 1841.66 | 116% | 1610.48 | 102% |
| Aug-18 | 2480.60 |35% | 1908.67 | 19% |

(*) to date.
