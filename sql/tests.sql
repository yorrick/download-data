do
$$
declare
  wrong_online_year integer;
  wrong_embargo integer;
begin
  select count(*)
  into wrong_online_year
  from download
  where online_year < publication_year;

  if (wrong_online_year > 0) then
    raise exception 'No download should have an online year before publication year';
  end if;



  select count(*)
  into wrong_embargo
  from download d, journal j
  where d.journal_id = j.id and d.embargo is true and j.full_oa is true;

  if (wrong_embargo > 0) then
    raise exception 'No download from a full oa journal should have embargo = true';
  end if;
end;
$$
