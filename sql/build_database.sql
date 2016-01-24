DROP TABLE IF EXISTS download;
DROP TABLE IF EXISTS article;
DROP TABLE IF EXISTS issue;
DROP TABLE IF EXISTS volume;
DROP TABLE IF EXISTS domain;
DROP TABLE IF EXISTS journal;


CREATE TABLE journal
(
    id SERIAL PRIMARY KEY,
    journal VARCHAR(20) not null UNIQUE,
    full_oa BOOLEAN
);


CREATE TABLE domain
(
    id SERIAL PRIMARY KEY,
    journal VARCHAR(20) not null REFERENCES journal(journal),
    domain VARCHAR(40)
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
    time TIMESTAMP not null,
    local_time TIMESTAMP,
    proxy_ip VARCHAR(20) not null,
    user_ip VARCHAR(32) not null,
    url VARCHAR(500) not null,

    -- TODO remove those fields
    referer VARCHAR(500),

    referer_host VARCHAR(500),
    continent VARCHAR(10),
    country VARCHAR(100),
    geo_coordinates VARCHAR(100),
    timezone VARCHAR(100),

    -- TODO remove those fields
    user_agent VARCHAR(100),

    browser VARCHAR(200),
    os VARCHAR(200),
    device VARCHAR(200),

    -- temporary fields, removed when article, issue, volume, and journal tables are built
    journal VARCHAR(20) not null,
    volume VARCHAR(20) not null,
    issue VARCHAR(20) not null,
    article VARCHAR(20) not null,

    -- TODO remove this column and use issue.publication_year instead
    publication_year integer not null,

    age integer not null,  -- age of article, at the moment of download
    is_robot boolean,
    is_bad_robot boolean,

    -- TODO remove this column and use issue.online_year instead
--    online_year integer,
    embargo boolean
);

CREATE INDEX download_year ON download (EXTRACT(YEAR FROM time));
-- local hour in IP's timezone: can be null, since geo location sometimes cannot find a timezone
CREATE INDEX download_hour ON download (EXTRACT(HOUR FROM local_time));

-- TODO cleanup indexes
CREATE INDEX ON download (publication_year);
CREATE INDEX ON download (article);
CREATE INDEX ON download (article_id);
CREATE INDEX ON download (issue);
CREATE INDEX ON download (volume);
CREATE INDEX ON download (journal);
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

CREATE INDEX ON journal (full_oa);


-- client copy of CSV file, to download table
\copy download(time, local_time, proxy_ip, user_ip, url, referer, referer_host, continent, country, geo_coordinates, timezone, user_agent, browser, os, device, journal, volume, issue, publication_year, article, age, is_robot, is_bad_robot) from /data/all.log.csv CSV DELIMITER ',' QUOTE '"' ENCODING 'utf-8';


-- client copy of CSV file, to journal table
\copy journal(journal, full_oa) from /data/journal.csv CSV DELIMITER ',' QUOTE '"' ENCODING 'utf-8';

-- client copy of CSV file, to journal domain table
\copy domain(journal, domain) from /data/journal-domain.csv CSV DELIMITER ',' QUOTE '"' ENCODING 'utf-8';


INSERT INTO article(article, issue, volume, journal, publication_year) SELECT DISTINCT article, issue, volume, journal, publication_year FROM download;
INSERT INTO issue(issue, volume, journal, publication_year) SELECT DISTINCT issue, volume, journal, publication_year FROM article;
INSERT INTO volume(volume, journal) SELECT DISTINCT volume, journal FROM issue;

-- insert journal that do not exist in csv journal referential
INSERT INTO journal(journal, full_oa)
    (
        SELECT DISTINCT
            journal,
            NULL :: BOOLEAN
        FROM volume
        WHERE journal NOT IN (SELECT journal FROM journal)
    );

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

-- compute online_year for each issue (articles in the same issue are all published at the same time)
-- for issues that where published after earliest year of sample (2010, or (SELECT MIN(EXTRACT(YEAR FROM time)) FROM download))
-- before that, we have no data to compute a more accurate online_year, we'll just consider that online_year = publication_year
UPDATE issue SET online_year = online_data.year
FROM
    (
        SELECT MIN(EXTRACT(YEAR FROM time)) AS year, a.issue_id
        FROM download d, article a
        WHERE d.article_id = a.id
        GROUP BY a.issue_id
    ) AS online_data
WHERE
    issue.id = online_data.issue_id
    and issue.publication_year >= (SELECT MIN(EXTRACT(YEAR FROM time)) FROM download);

-- set online_year for issues that were published before earliest year of sample (2010, or (SELECT MIN(EXTRACT(YEAR FROM time)) FROM download))
UPDATE issue SET online_year = publication_year
WHERE publication_year < (SELECT MIN(EXTRACT(YEAR FROM time)) FROM download);


-- compute embargo flag for downloads: true means downloaded article is under embargo, false means article was freely available
-- embargo is computed using issue's online year: publication are often late, and using publication year would lead to wrong results
UPDATE download SET embargo = (EXTRACT(YEAR FROM time) - i.online_year) <= 1
FROM article a, issue i, volume v, (SELECT * FROM journal j WHERE full_oa IS NULL OR full_oa IS FALSE) as j
WHERE
    article_id = a.id AND a.issue_id = i.id AND i.volume_id = v.id AND v.journal_id = j.id;

UPDATE download SET embargo = FALSE
FROM article a, issue i, volume v, journal j
WHERE
    article_id = a.id AND a.issue_id = i.id AND i.volume_id = v.id AND v.journal_id = j.id
    AND j.full_oa IS TRUE;


-- enforce constraints
ALTER TABLE download ALTER COLUMN article_id SET NOT NULL;
--ALTER TABLE download ALTER COLUMN online_year SET NOT NULL;
ALTER TABLE download ALTER COLUMN embargo SET NOT NULL;
ALTER TABLE article ALTER COLUMN issue_id SET NOT NULL;
ALTER TABLE issue ALTER COLUMN volume_id SET NOT NULL;
ALTER TABLE issue ALTER COLUMN publication_year SET NOT NULL;
ALTER TABLE issue ALTER COLUMN online_year SET NOT NULL;
ALTER TABLE volume ALTER COLUMN journal_id SET NOT NULL;


-- cleanup columns that were only used to build schema
ALTER TABLE download DROP COLUMN journal, DROP COLUMN volume, DROP COLUMN issue, DROP COLUMN article;
ALTER TABLE article DROP COLUMN journal, DROP COLUMN volume, DROP COLUMN issue, DROP COLUMN publication_year;
ALTER TABLE issue DROP COLUMN journal, DROP COLUMN volume;
ALTER TABLE volume DROP COLUMN journal;

