[![Build Status](https://travis-ci.org/yorrick/download-data.svg?branch=master)](https://travis-ci.org/yorrick/download-data)

[![Coverage Status](https://coveralls.io/repos/yorrick/download-data/badge.svg?branch=master&service=github)](https://coveralls.io/github/yorrick/download-data?branch=master)

## Setup project

```
virtualenv --no-site-packages --python python2.7 ~/virtualenvs/download-data
source ~/virtualenvs/download-data/bin/activate
pip install -r requirements.txt
```


## Run tests
```
nosetests
```


## Run log filtering

--debug enables single process execution for easier debugging.

```
./extract/parse_downloads.py [--debug] [--keep-robots] data/*.log && cat data/*.log.csv > data/all.log.csv
```


## Setup database

Postgres is used as a test database.
Using docker 1.9 and volume support:


```
docker volume create --name=download_data
```


### Run DB

```
docker run --name download_data_postgres -d -e POSTGRES_PASSWORD=postgres -e POSTGRES_USER=postgres -e POSTGRES_DB=logs -p 5432:5432 --volume download_data:/var/log/postgres/data postgres:9.4
```

### Connnect to DB

With 0xDBE, use the following URL

```
jdbc:postgresql://localdocker:5432/logs
```

With docker only (command line), use

```
docker run -it --link download_data_postgres:download_data_postgres --rm -e PGPASSWORD=postgres postgres:9.4 psql --dbname=logs --host=download_data_postgres --username=postgres --command="select * from download limit 10"
```


### Create table, and load data


```
docker run -it --link download_data_postgres:download_data_postgres --rm -e PGPASSWORD=postgres --volume $PWD/data:/data --volume $PWD/sql:/sql postgres:9.4 psql --dbname=logs --host=download_data_postgres --username=postgres -v ON_ERROR_STOP=1 -f /sql/build_database.sql
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


select count(*) from issue where publication_year <> online_year;
