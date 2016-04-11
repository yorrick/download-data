
EXPLAIN ANALYZE
select user_ip, proxy_ip, date(time) as date, count(*) as number
from download
group by user_ip, date, proxy_ip
order by number desc;

------------------------------------------------------------------------------

EXPLAIN ANALYZE
select distinct i.publication_year, url from download d, article a, issue i
where
    d.article_id = a.id and a.issue_id = i.id
    and url not like '%pdf%'
    and url like '%html'
group by i.publication_year, url
order by i.publication_year desc;

------------------------------------------------------------------------------

EXPLAIN ANALYZE
select EXTRACT(HOUR FROM local_time) as download_hour, country, count(*) as number
from download
where local_time is not null
and country in
    (
        select country from download
        group by country
        order by count(*) desc
        limit 5
    )
group by local_time, country
order by download_hour asc;

------------------------------------------------------------------------------

EXPLAIN ANALYZE
select EXTRACT(HOUR FROM local_time) as download_hour, country, count(*) as number, is_robot, is_bad_robot, user_ip
from download
where local_time is not null
and country in
    (
        select country from download
        group by country
        order by count(*) desc
        limit 5
    )
group by local_time, country, is_robot, is_bad_robot, user_ip
order by download_hour asc, is_robot, is_bad_robot;

------------------------------------------------------------------------------

-- Number of non-OA, full OA and ended embargo
EXPLAIN ANALYZE
select j.full_oa, dw.embargo, count(*) as number
	from download dw
		inner join article a on dw.article_id = a.id
		inner join issue i on a.issue_id = i.id
		inner join volume v on i.volume_id = v.id
		inner join journal j on v.journal_id = j.id
	group by j.full_oa, dw.embargo
	order by number desc;

------------------------------------------------------------------------------

-- Number of downloads by domain
EXPLAIN ANALYZE
select count(*) as number, speciality
	from download dw
		inner join article a on dw.article_id = a.id
		inner join issue i on a.issue_id = i.id
		inner join volume v on i.volume_id = v.id
		inner join journal j on v.journal_id = j.id
	group by speciality
	order by number desc;

------------------------------------------------------------------------------

-- Publication year of the downloads
EXPLAIN ANALYZE
select i.publication_year, count(*) as number, is_robot, is_bad_robot
	from download dw
		inner join article a on dw.article_id = a.id
		inner join issue i on a.issue_id = i.id
	group by publication_year, is_robot, is_bad_robot
	order by publication_year asc, is_robot, is_bad_robot;
