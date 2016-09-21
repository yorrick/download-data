[![Build Status](https://travis-ci.org/yorrick/download-data.svg?branch=master)](https://travis-ci.org/yorrick/download-data)

[![Coverage Status](https://coveralls.io/repos/yorrick/download-data/badge.svg?branch=master&service=github)](https://coveralls.io/github/yorrick/download-data?branch=master)

## Setup project

```
virtualenv --no-site-packages --python python2.7 ~/virtualenvs/download-data
source ~/virtualenvs/download-data/bin/activate
pip install -r requirements.txt
```

## Release notes

See [this file](release-notes.md) to keep track of changes along versions.


## Random file sampling

./random-select.R  is used to select random samples among files.
It is stable (it always returns the same results if given the same parameters), and takes as argument:  
 * path to directory containg log files
 * number of log files to draw
 
Drawn log file names are printed on console.

```
./random-select.R data 30
```

Warning! For sampling to work, the number of asked samples must be less or equal than the number of
log files for each year.

## Run tests
```
nosetests
```


## Run log filtering


Log filtering is a python script that produces 1 csv file per log file.


* --debug: enables single process execution for easier debugging.
Here <VERSION> can be v0.10 for instance.

* --minimum-fields: do not export url, geo_coordinates, is_robot, bad_robot fields in csv. Warning! Produced csv cannot be used to build database!
 

Warning! script does not reprocess files that have already been processed (ie, if files are already present in output dir).


### CSV files contents:

 * country ISO code: https://en.wikipedia.org/wiki/ISO_3166-1


### Using docker

```
docker run -ti --volume $SOURCE_DIR:/source --volume $OUTPUT_DIR:/output yorrick/download-data:$VERSION sh -c '
    extract/parse_downloads.py \
    [--debug] \
    [--minimum-fields] \
    [--keep-robots] \
    [--total-number-threshold 100] \
    [--print-stats-for-ip 111.111.111.111] \
    /data/*.log && cat /data/*.log.csv > /data/all.log.csv'
```

Example:

```
export VERSION=v0.10
export SOURCE_DIR=~/test/download-data-source/
export OUTPUT_DIR=~/test/download-data-output/
docker run -ti --memory="2G" --cpuset-cpus="0-1" --volume $SOURCE_DIR:/source --volume $OUTPUT_DIR:/output yorrick/download-data:$VERSION 
cat $OUTPUT_DIR/*.log.csv > $OUTPUT_DIR/all.log.csv
```


### From source

```
export SOURCE_DIR=~/test/download-data-source/
export OUTPUT_DIR=~/test/download-data-output/
./extract/parse_downloads.py $SOURCE_DIR $OUTPUT_DIR \
    [--debug] \
    [--minimum-fields] \
    [--keep-robots] \
    [--total-number-threshold 100] \
    [--print-stats-for-ip 111.111.111.111] \
    /data/*.log && cat /data/*.log.csv > /data/all.log.csv'
```


## Run postgres database with docker


### Run DB

```
docker-compose up -d
```

### Remove database 

To update database, it's necessary to remove volume

```
docker-compose rm
# docker-compose rm -v does not work, so use
docker volume rm downloaddata_postgres-data
```



### Connnect to DB

With 0xDBE, use the following URL

```
jdbc:postgresql://localhost:5432/logs
```

With docker only (command line), use

```
docker-compose run psql
select * from download limit 10;
```


### Create table, and load data


```
docker-compose run psql -f /sql/build_database.sql
```

OR

```
/Applications/Postgres.app/Contents/Versions/9.4/bin/psql -f sql/build_database.sql
```


See downloads of articles that can be accessed by multiple urls paths (we consider them as different):

```
select url, article from download
where article in (select article from article GROUP BY article HAVING count(article) > 1)
order by article;
```


Check issue publication year consistence (this query should return no results)
```
select issue_id from download GROUP BY issue_id having COUNT(DISTINCT(publication_year)) > 1;
```


See issues that have been published late:
```
select journal, volume, issue, publication_year, online_year, (online_year - publication_year) as delay
from issue, volume, journal
where 
    publication_year <> online_year
    and publication_year >= (SELECT MIN(download_year) FROM download)
    and issue.volume_id = volume.id
    and volume.journal_id = journal.id
order by journal, volume, issue;
```


## Run article referential extraction (from NLM files, one xml file per article)

```
extract/build-article-referential.sh ~/test/nlm data/all_articles.csv
```

