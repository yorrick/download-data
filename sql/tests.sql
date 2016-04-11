do
$$
declare
  wrong_online_year integer;
  wrong_embargo integer;
  journal_count integer;
begin
  select count(*)
  into wrong_online_year
  from issue
  where online_year < publication_year;

  if (wrong_online_year > 0) then
    raise exception 'No issue should have an online year before publication year';
  end if;



  select count(*)
  into wrong_embargo
  from download d, article a, issue i, volume v, journal j
  where
        d.article_id = a.id AND a.issue_id = i.id AND i.volume_id = v.id AND v.journal_id = j.id
        and d.embargo is true and j.full_oa is true;

  if (wrong_embargo > 0) then
    raise exception 'No download from a full oa journal should have embargo = true';
  end if;


  select count(*)
  into journal_count
  from journal;

  if (journal_count = 0) then
    raise exception 'No journals have been created';
  end if;


end;
$$
