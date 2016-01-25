
EXPLAIN ANALYZE
select user_ip, proxy_ip, date(time) as date, count(*) as number
from download
group by user_ip, date, proxy_ip
order by number desc;

------------------------------------------------------------------------------

EXPLAIN ANALYZE
select distinct publication_year, url from download
where
    url not like '%pdf%'
    and url like '%html'
group by publication_year, url
order by publication_year desc;

------------------------------------------------------------------------------

EXPLAIN ANALYZE
select download_hour, country, count(*) as number
from download
where local_time is not null
and country in
    (
        select country from download
        group by country
        order by count(*) desc
        limit 5
    )
group by download_hour, country
order by download_hour asc;

------------------------------------------------------------------------------

EXPLAIN ANALYZE
select download_hour, country, count(*) as number, is_robot, is_bad_robot, user_ip
from download
where local_time is not null
and country in
    (
        select country from download
        group by country
        order by count(*) desc
        limit 5
    )
group by download_hour, country, is_robot, is_bad_robot, user_ip
order by download_hour asc, is_robot, is_bad_robot;
