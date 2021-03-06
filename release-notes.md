## v0.16

* Feature: create table to be able to join journals from downloads with journals from E data

## v0.15

* Feature: add bash script to parse nlm data, and transform usefull data to csv
* Feature: keep "ar" suffixes in article ids, to make match with E. data easier
* Feature: quote all values when exporing minimal fields

## v0.14

* Feature: add region in geolocalization data
* Feature: add flag to parsing script to avoid exporting some columns to csv

## v0.13

* Feature: add city in geolocalization data
* Feature: filter html downloads depending on journal referential data

## v0.11

* Feature: user can now specify source and output directories
* Feature: parsing can be stopped, and relaunched

## v0.10

* Feature: package parsing script in docker container

## v0.9

* Feature: added device type in download table. "p" -> pc, "m" -> mobile and "t" -> tablet
* Feature: journals have only 1 (standard) classification now

## v0.8

* Feature: indexes are all anonymous now, to make renaming easier

## v0.7

* Bug fix: parsing can now be stopped using ctrl-c
* Feature: Sampling script works by sampling all years at once

## v0.6

* Bug fix in parasble log line counts, that affected robot detection also
* Update robot detection to use number of requests instead of number of download as threshold

## v0.5

* More robust ip parsing for geolocation

## v0.4

* Added R script to draw samples from log file set

## v0.3

* Database optimization: relations have been normalized to improve DB creation time, DB disk space, and query speed

## v0.2

* Referer support: similar referers are grouped into categories

## v0.1

* Html files are not considered as downloads, except if url ends with ".html" or ".html?vue=integral"
* Good robots are detected using user agent.
* Bad robot are detected using per day, IP based activity stats.
* Domains are associated to domains.
