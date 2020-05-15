# Lys event fetcher

![Deploy lambda](https://github.com/corentindautreme/lys-event-fetcher/workflows/Deploy%20lambda/badge.svg)

An Amazon Lambda script tasked with searching events (= national final show dates) for Lys.

Language:
* Python 3

Dependencies:
* [requests](https://pypi.org/project/requests/) 2.22
* [dateparser](https://pypi.org/project/dateparser/) 0.7

## Date extraction process

Dates are retrieved by parsing [Eurovoix](https://eurovoix.com) articles through the website's RSS feed and, after filtering and normalizing, saved as suggestions for manual processing (that is, deciding or not to use the extracted dates to create events that will be tweeted by Lys).

The date extraction process is as follows:

* Retrieving all articles from Eurovoix's RSS feed
* Keeping only the articles that refer to Eurovision national finals, which are found by:
  * Searching for the "National Selection" tag in the article's categories
  * Searching for a national final name (Melodifestivalen, Melodi Grand Prix...) or short name (MGP, UMK...) in the article's title
  * Excluding articles referring to the sister Eurovision events (Junior Eurovision, EYD, EYM, Choir), again by looking at the article's categories
* Searching for dates in the body of the article and filtering out the "false positives", mainly:
  * Numerical values wrongly extracted by the date parser ("25% of the vote", "finished 6th in the final"...)
  * Dates that are not in the usual national final season range (September to March)
* Saving the dates with their context (= the string that the date parser interpreted as a date) and a link to the source article as a "suggestion" in a DynamoDB table

## Suggestions processing

I have made a basic Android app for my smartphone to help me manage Lys, and developped a dedicated section for the suggestion management.

![Lys Manager - Suggestion display dialog](https://raw.githubusercontent.com/corentindautreme/lys-event-fetcher/master/img/lys_manager_suggestion.jpg)

Date context can be displayed for review purposes by simply tapping on a date:

![Lys Manager - Suggested date context display](https://raw.githubusercontent.com/corentindautreme/lys-event-fetcher/master/img/lys_manager_date_context.jpg)