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
DROP TABLE IF EXISTS download;
DROP TABLE IF EXISTS article;
DROP TABLE IF EXISTS issue;
DROP TABLE IF EXISTS volume;
DROP TABLE IF EXISTS journal;
CREATE TABLE journal
(
    id SERIAL PRIMARY KEY,
    journal VARCHAR(20) not null
);
CREATE TABLE volume
(
    id SERIAL PRIMARY KEY,
    journal_id integer references journal(id),
    journal VARCHAR(20) not null,
    volume VARCHAR(20) not null
);
CREATE TABLE issue
(
    id SERIAL PRIMARY KEY,
    volume_id integer references volume(id),
    journal VARCHAR(20) not null,
    volume VARCHAR(20) not null,
    issue VARCHAR(20) not null
);
CREATE TABLE article
(
    id SERIAL PRIMARY KEY,
    issue_id integer references issue(id),
    journal VARCHAR(20) not null,
    volume VARCHAR(20) not null,
    issue VARCHAR(20) not null,
    article VARCHAR(20) not null
);
CREATE TABLE download
(
    id SERIAL PRIMARY KEY,
    article_id integer references article(id),
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
    journal VARCHAR(20) not null,
    volume VARCHAR(20) not null,
    issue VARCHAR(20) not null,
    article VARCHAR(20) not null,
    age integer not null
);
```

### Load data into table


```
docker run -it --link download_data_postgres:download_data_postgres --rm -e PGPASSWORD=postgres --volume $PWD/data:/data postgres:9.4 bash 
psql --dbname=logs --host=download_data_postgres --username=postgres
```
 
```
\copy download(time, local_time, proxy_ip, user_ip, url, referer, referer_host, continent, country, geo_coordinates, timezone, user_agent, browser, os, device, journal, volume, issue, article, age) from /data/110302-sample.csv CSV DELIMITER ',' QUOTE '"' ENCODING 'utf-8';
```

```
INSERT INTO article(article, issue, volume, journal) SELECT DISTINCT article, issue, volume, journal FROM download;
INSERT INTO issue(issue, volume, journal) SELECT DISTINCT issue, volume, journal FROM article;
INSERT INTO volume(volume, journal) SELECT DISTINCT volume, journal FROM issue;
INSERT INTO journal(journal) SELECT DISTINCT journal FROM volume;
```


```
UPDATE volume SET journal_id = journal.id FROM journal where volume.journal = journal.journal;
UPDATE issue SET volume_id = volume.id FROM volume where issue.volume = volume.volume and issue.journal = volume.journal;
UPDATE article SET issue_id = issue.id FROM issue where article.issue = issue.issue and article.volume = issue.volume and article.journal = issue.journal;
UPDATE download SET article_id = article.id FROM article where download.article = article.article and download.issue = article.issue and download.volume = article.volume and download.journal = article.journal;
```

```
ALTER TABLE download ALTER COLUMN article_id SET NOT NULL;
ALTER TABLE article ALTER COLUMN issue_id SET NOT NULL;
ALTER TABLE issue ALTER COLUMN volume_id SET NOT NULL;
ALTER TABLE volume ALTER COLUMN journal_id SET NOT NULL;
```


