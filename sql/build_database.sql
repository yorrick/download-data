DROP TABLE IF EXISTS download;
DROP TABLE IF EXISTS article;
DROP TABLE IF EXISTS journal_other_ids;
DROP TABLE IF EXISTS journal;


CREATE TABLE journal
(
    id SERIAL PRIMARY KEY,
    journal VARCHAR(20) not null UNIQUE,
    general_discipline VARCHAR(50),
    general_discipline_fr VARCHAR(50),
    discipline VARCHAR(50),
    discipline_fr VARCHAR(50),
    speciality VARCHAR(50),
    speciality_fr VARCHAR(50),
    full_oa BOOLEAN
);


CREATE TABLE journal_other_ids
(
    journal VARCHAR(20) REFERENCES journal(journal),
    other_id VARCHAR(20) PRIMARY KEY
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
    online_year integer  -- value of this column is computed after having loaded all the data from downloads
);


CREATE TABLE article
(
    id SERIAL PRIMARY KEY,
    issue_id integer references issue(id),
    journal_id integer references journal(id),
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

    referer_host VARCHAR(500),
    continent VARCHAR(10),
    country VARCHAR(2),
    city VARCHAR(50),
    region VARCHAR(50),
    geo_coordinates VARCHAR(100),
    timezone VARCHAR(100),

    browser VARCHAR(200),
    os VARCHAR(200),
    device_type VARCHAR(1),

    -- temporary fields, removed when article, issue, volume, and journal tables are built
    journal VARCHAR(20) not null,
    volume VARCHAR(20) not null,
    issue VARCHAR(20) not null,
    article VARCHAR(20) not null,
    publication_year integer not null,

    age integer not null,  -- age of article, at the moment of download
    is_robot boolean,
    is_bad_robot boolean,

    embargo boolean  -- value of this column is computed after having loaded all the data from downloads
);


-- client copy of CSV file, to download table
\copy download(time, local_time, proxy_ip, user_ip, url, referer_host, continent, country, city, region, geo_coordinates, timezone, browser, os, device_type, journal, volume, issue, publication_year, article, age, is_robot, is_bad_robot) from /data/all.log.csv CSV DELIMITER ',' QUOTE '"' ENCODING 'utf-8';


-- client copy of CSV file, to journal table
\copy journal(journal, general_discipline, general_discipline_fr, discipline, discipline_fr, speciality, speciality_fr, full_oa) from /data/journal.csv CSV DELIMITER ',' QUOTE '"' ENCODING 'utf-8';


-- client copy of CSV file, to journal table
\copy journal_other_ids(journal, other_id) from /data/journal_other_ids.csv CSV DELIMITER ',' QUOTE '"' ENCODING 'utf-8';


-- relational model building, from download data
INSERT INTO article(article, issue, volume, journal, publication_year) SELECT DISTINCT article, issue, volume, journal, publication_year FROM download;
INSERT INTO issue(issue, volume, journal, publication_year) SELECT DISTINCT issue, volume, journal, publication_year FROM article;
INSERT INTO volume(volume, journal) SELECT DISTINCT volume, journal FROM issue;

-- insert journals that do not exist in csv journal referential: unfortunately, some of the journals that are present in downloads are not listed in journal referential
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

UPDATE article SET journal_id = volume.journal_id
FROM issue, volume
where
    article.issue_id = issue.id
    and issue.volume_id = volume.id;


-- set all foreign keys to download table
UPDATE download SET article_id = article.id
FROM article
WHERE
    download.publication_year = article.publication_year
    and download.article = article.article
    and download.issue = article.issue
    and download.volume = article.volume
    and download.journal = article.journal;

-- Compute more accurate online_year for issues: all articles from an issue are published at the same time, but there
-- can be big differences between publication_year and the moment at which the issue was made available online (thus we named it online_year).
-- This has impacts on the computation of embargo mobile barrier, which is very important for this study

-- The way we compute a more precise online_year is that we consider online_year to be the year of the first download we have
-- for an issue, for the years we have download data. For publication_year before 2010 (earliest download log data we have)
-- we have no choice but to consider online_year the same as publication_year.

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
ALTER TABLE download ALTER COLUMN embargo SET NOT NULL;
ALTER TABLE article ALTER COLUMN issue_id SET NOT NULL;
ALTER TABLE article ALTER COLUMN journal_id SET NOT NULL;
ALTER TABLE issue ALTER COLUMN volume_id SET NOT NULL;
ALTER TABLE issue ALTER COLUMN publication_year SET NOT NULL;
ALTER TABLE issue ALTER COLUMN online_year SET NOT NULL;
ALTER TABLE volume ALTER COLUMN journal_id SET NOT NULL;


-- cleanup columns that were only used to build relational schema
ALTER TABLE download DROP COLUMN journal, DROP COLUMN volume, DROP COLUMN issue, DROP COLUMN article, DROP COLUMN publication_year;
ALTER TABLE article DROP COLUMN journal, DROP COLUMN volume, DROP COLUMN issue, DROP COLUMN issue_id;
ALTER TABLE issue DROP COLUMN journal, DROP COLUMN volume;
ALTER TABLE volume DROP COLUMN journal;

-- cleanup volume and issue tables that are not used later
DROP TABLE issue;
DROP TABLE volume;















-- article referential (erudit) data (from NLM file)

DROP TABLE IF EXISTS all_article;
DROP TABLE IF EXISTS all_journal;

CREATE TABLE all_journal
(
    journal VARCHAR(20) NOT NULL PRIMARY KEY
);

CREATE TABLE all_article
(
    journal VARCHAR(20) NOT NULL,
    journal_title VARCHAR(100) NOT NULL,
    journal_subtitle VARCHAR(200),
    article VARCHAR(20) NOT NULL,
    epub_year INTEGER,
    collection_year VARCHAR(9),
    publication_year INTEGER
);

\copy all_article(journal, journal_title, journal_subtitle, article, epub_year, collection_year) from /data/all_articles.csv CSV DELIMITER '@' QUOTE '"' ENCODING 'utf-8';

UPDATE all_article SET journal = lower(trim(journal));
UPDATE all_article SET publication_year = left(collection_year, 4)::integer;

INSERT INTO all_journal(journal)
    (
        SELECT journal
        from all_article
        group by journal
    );

ALTER TABLE all_article ADD CONSTRAINT journal_fk
FOREIGN KEY (journal) REFERENCES all_journal;

ALTER TABLE all_article DROP COLUMN journal_title, DROP COLUMN journal_subtitle;




-- this table allows for joins between erudit's journal ids (all_journal) and download's journal ids


--CREATE TABLE journal_alternate_ids
--(
--    download_id VARCHAR(20),
--    referential_id VARCHAR(20) PRIMARY KEY NOT NULL,
--    CONSTRAINT journal_alternate_ids_download_id_fkey FOREIGN KEY (download_id) REFERENCES journal (journal),
--    CONSTRAINT journal_alternate_ids_referential_id_fkey FOREIGN KEY (referential_id) REFERENCES all_journal (journal)
--);
--
--\copy journal_alternate_ids(download_id, referential_id) from /data/journal_other_ids.csv CSV DELIMITER ',' QUOTE '"' ENCODING 'utf-8';
