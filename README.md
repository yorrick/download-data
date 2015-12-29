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
./extract/parse_downloads.py [--debug] data/*.log
```


## Setup database

Postgres is used as a test database.
Using docker 1.9 and volume support:

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
docker run -it --link download_data_postgres:download_data_postgres --rm -e PGPASSWORD=postgres postgres:9.4 sh -c 'exec psql --dbname=logs --host=download_data_postgres --username=postgres --command="select * from downloads"'
```


### Create table


```
DROP TABLE downloads;
CREATE TABLE downloads
(
    time VARCHAR(30) not null,
    local_time VARCHAR(30),
    proxy_ip VARCHAR(20) not null,
    user_ip VARCHAR(30) not null,
    url VARCHAR(500) not null,
    referer VARCHAR(1000),
    referer_host VARCHAR(1000),
    continent VARCHAR(10),
    country VARCHAR(100),
    geo_coordinates VARCHAR(100),
    timezone VARCHAR(100),
    user_agent VARCHAR(400),
    browser VARCHAR(200),
    os VARCHAR(200),
    device VARCHAR(200),
    journal_name VARCHAR(20) not null,
    volume VARCHAR(20) not null,
    issue VARCHAR(20) not null,
    article_id VARCHAR(20) not null,
    age integer not null
);
```


### Load data into table

```
docker run -it --link download_data_postgres:download_data_postgres --rm -e PGPASSWORD=postgres --volume $PWD/data:/data postgres:9.4 bash 
psql --dbname=logs --host=download_data_postgres --username=postgres
```
 
```
\copy downloads(journal_name, volume, issue, article_id) from /data/110302-sample.csv CSV DELIMITER ',' QUOTE '"' ENCODING 'utf-8';
```

