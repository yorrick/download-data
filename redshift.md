DROP TABLE yorrick_test;


CREATE TABLE yorrick_test
(
    id INT IDENTITY(1, 1) PRIMARY KEY,
    time TIMESTAMP not null,
    local_time TIMESTAMP,
    proxy_ip VARCHAR(80) not null,
    user_ip VARCHAR(128) not null,
    url VARCHAR(2000) not null,

    referer_host VARCHAR(2000),
    continent VARCHAR(40),
    country VARCHAR(8),
    city VARCHAR(200),
    region VARCHAR(200),
    geo_coordinates VARCHAR(400),
    timezone VARCHAR(400),

    browser VARCHAR(800),
    os VARCHAR(800),
    device_type VARCHAR(4),

    -- temporary fields, removed when article, issue, volume, and journal tables are built
    journal VARCHAR(80) not null,
    volume VARCHAR(80) not null,
    issue VARCHAR(80) not null,
    article VARCHAR(80) not null,
    publication_year integer not null,

    age integer not null,  -- age of article, at the moment of download
    is_robot boolean,
    is_bad_robot boolean,

    embargo boolean  -- value of this column is computed after having loaded all the data from downloads
);


COPY yorrick_test
(time, local_time, proxy_ip, user_ip, url, referer_host, continent, country, city, region, geo_coordinates, timezone, browser, os, device_type, journal, volume, issue, publication_year, article, age, is_robot, is_bad_robot)
FROM 's3://test.1science.io/yorrick/all.csv'
CREDENTIALS 'aws_access_key_id=xxx;aws_secret_access_key=xxx'
CSV DELIMITER ',' QUOTE '"';


select * from yorrick_test;



find nlm -type f -name "*.xml" |xargs xmlstarlet sel -n -t -v "concat(//_:journal-id[@journal-id-type='other'], ';', //_:journal-title, ';', //_:journal-subtitle, ';', //_:volume, ';', //_:issue, ';', //_:article-id[@pub-id-type='other'], ';', //_:pub-date[@pub-type='epub']/_:year, '##')" | tr '\n' ' ' | sed "y/’āáǎàâēéěèīíǐìōóǒòūúǔùǖǘǚǜĀÁǍÀĒÉĚÈĪÍǏÌŌÓǑÒŪÚǓÙǕǗǙǛ/'aaaaaeeeeiiiioooouuuuüüüüAAAAEEEEIIIIOOOOUUUUÜÜÜÜ/"| sed 's/##/\'$'\n/g' | sed '$ d'| sed -e 's/•//g' | sed -e "s/  */ /g" > ~/download-data/data/articles.csv


\copy article_referential(journal_id, journal, journal_subtitle, volume, issue, article, publication_year) from /data/articles.csv CSV DELIMITER ';' QUOTE '"' ENCODING 'utf-8';

select DISTINCT(concat(lower(trim(journal_id)), '; ', lower(trim(journal)), '; ', lower(trim(journal_subtitle))))
from article_referential
order by concat(lower(trim(journal_id)), '; ', lower(trim(journal)), '; ', lower(trim(journal_subtitle)));