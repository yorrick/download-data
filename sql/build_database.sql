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
    issue VARCHAR(20) not null,
    publication_year integer,
    online_year integer
);


CREATE TABLE article
(
    id SERIAL PRIMARY KEY,
    issue_id integer references issue(id),
    journal VARCHAR(20) not null,
    volume VARCHAR(20) not null,
    issue VARCHAR(20) not null,
    publication_year integer not null,
    article VARCHAR(20) not null
);


CREATE TABLE download
(
    id SERIAL PRIMARY KEY,
    article_id integer references article(id),
    issue_id integer references issue(id),
    volume_id integer references volume(id),
    journal_id integer references journal(id),
    time TIMESTAMP not null,
    local_time TIMESTAMP,
    proxy_ip VARCHAR(20) not null,
    user_ip VARCHAR(32) not null,
    url VARCHAR(500) not null,
    referer VARCHAR(500),
    referer_host VARCHAR(500),
    continent VARCHAR(10),
    country VARCHAR(100),
    geo_coordinates VARCHAR(100),
    timezone VARCHAR(100),
    user_agent VARCHAR(100),
    browser VARCHAR(200),
    os VARCHAR(200),
    device VARCHAR(200),
    journal VARCHAR(20) not null,
    volume VARCHAR(20) not null,
    issue VARCHAR(20) not null,
    article VARCHAR(20) not null,
    publication_year integer not null,
    age integer not null,
    is_robot boolean,
    is_bad_robot boolean,
    download_year integer,
    download_hour integer,  -- local hour in IP's timezone: can be null, since geo location sometimes cannot find a timezone
    online_year integer,
    embargo boolean
);

CREATE INDEX ON download (download_year);
CREATE INDEX ON download (download_hour);
CREATE INDEX ON download (publication_year);
CREATE INDEX ON download (article);
CREATE INDEX ON download (article_id);
CREATE INDEX ON download (issue);
CREATE INDEX ON download (issue_id);
CREATE INDEX ON download (volume);
CREATE INDEX ON download (volume_id);
CREATE INDEX ON download (journal);
CREATE INDEX ON download (journal_id);
CREATE INDEX ON download (country);

CREATE INDEX ON article (journal);
CREATE INDEX ON article (volume);
CREATE INDEX ON article (issue);
CREATE INDEX ON article (issue_id);
CREATE INDEX ON article (article);

CREATE INDEX ON issue (journal);
CREATE INDEX ON issue (volume);
CREATE INDEX ON issue (volume_id);
CREATE INDEX ON issue (issue);

CREATE INDEX ON volume (journal);
CREATE INDEX ON volume (journal_id);
CREATE INDEX ON volume (volume);

CREATE INDEX ON journal (journal);


-- client copy of CSV file, to download table
\copy download(time, local_time, proxy_ip, user_ip, url, referer, referer_host, continent, country, geo_coordinates, timezone, user_agent, browser, os, device, journal, volume, issue, publication_year, article, age, is_robot, is_bad_robot) from /data/all.log.csv CSV DELIMITER ',' QUOTE '"' ENCODING 'utf-8';


INSERT INTO article(article, issue, volume, journal, publication_year) SELECT DISTINCT article, issue, volume, journal, publication_year FROM download;
INSERT INTO issue(issue, volume, journal, publication_year) SELECT DISTINCT issue, volume, journal, publication_year FROM article;
INSERT INTO volume(volume, journal) SELECT DISTINCT volume, journal FROM issue;
INSERT INTO journal(journal) SELECT DISTINCT journal FROM volume;


-- set FK to volume, issue and article tables
UPDATE volume SET journal_id = journal.id
FROM journal where volume.journal = journal.journal;

UPDATE issue SET volume_id = volume.id
FROM volume where issue.volume = volume.volume and issue.journal = volume.journal;

UPDATE article SET issue_id = issue.id
FROM issue
where
    article.issue = issue.issue
    and article.publication_year = issue.publication_year
    and article.volume = issue.volume
    and article.journal = issue.journal;


-- set all foreign keys to download table
UPDATE download SET article_id = article.id
FROM article
WHERE
    download.publication_year = article.publication_year
    and download.article = article.article
    and download.issue = article.issue
    and download.volume = article.volume
    and download.journal = article.journal;

UPDATE download SET issue_id = article.issue_id FROM article where download.article_id = article.id;
UPDATE download SET volume_id = issue.volume_id FROM issue where download.issue_id = issue.id;
UPDATE download SET journal_id = volume.journal_id FROM volume where download.volume_id = volume.id;
UPDATE download SET download_year = EXTRACT(YEAR FROM time);
UPDATE download SET download_hour = EXTRACT(HOUR FROM local_time);


-- compute publication_year for issue using download publication_year (extracted from url)
-- (MIN(publication_year) is just a way to select a single year, we could have used MAX also as all year are the same)
--UPDATE issue SET publication_year = publication_data.year
--FROM (SELECT MIN(publication_year) AS year, issue_id FROM download GROUP BY issue_id) AS publication_data
--WHERE issue.id = publication_data.issue_id;


-- compute online_year for each issue (articles in the same issue are all published at the same time)
-- for issues that where published after earliest year of sample (2010, or (SELECT MIN(download_year) FROM download))
-- before that, we have no data to compute a more accurate online_year, we'll just consider that online_year = publication_year
UPDATE issue SET online_year = online_data.year
FROM
    (SELECT MIN(download_year) AS year, issue_id FROM download GROUP BY issue_id) AS online_data
WHERE
    issue.id = online_data.issue_id
    and issue.publication_year >= (SELECT MIN(download_year) FROM download);

-- set online_year for issues that were published before earliest year of sample (2010, or (SELECT MIN(download_year) FROM download))
UPDATE issue SET online_year = publication_year
WHERE publication_year < (SELECT MIN(download_year) FROM download);


-- compute embargo flag for downloads: true means downloaded article is under embargo, false means article was freely available
-- embargo is computed using issue's online year: publication are often late, and using publication year would lead to wrong results
UPDATE download SET online_year = issue.online_year
FROM issue
WHERE download.issue_id = issue.id;

UPDATE download SET embargo = (download_year - online_year) <= 1;


-- enforce constraints
ALTER TABLE download ALTER COLUMN article_id SET NOT NULL;
ALTER TABLE download ALTER COLUMN issue_id SET NOT NULL;
ALTER TABLE download ALTER COLUMN volume_id SET NOT NULL;
ALTER TABLE download ALTER COLUMN journal_id SET NOT NULL;
ALTER TABLE download ALTER COLUMN download_year SET NOT NULL;
ALTER TABLE download ALTER COLUMN online_year SET NOT NULL;
ALTER TABLE download ALTER COLUMN embargo SET NOT NULL;
ALTER TABLE article ALTER COLUMN issue_id SET NOT NULL;
ALTER TABLE issue ALTER COLUMN volume_id SET NOT NULL;
ALTER TABLE issue ALTER COLUMN publication_year SET NOT NULL;
ALTER TABLE issue ALTER COLUMN online_year SET NOT NULL;
ALTER TABLE volume ALTER COLUMN journal_id SET NOT NULL;


-- cleanup columns that were only used to build schema
ALTER TABLE article DROP COLUMN journal, DROP COLUMN volume, DROP COLUMN issue, DROP COLUMN publication_year;
ALTER TABLE issue DROP COLUMN journal, DROP COLUMN volume;
ALTER TABLE volume DROP COLUMN journal;
