-- test online years on dowloads

do
$$
declare
  wrong_online_year integer;
begin
  select count(*)
  into wrong_online_year
  from download
  where online_year < publication_year;

  if (wrong_online_year > 0) then
    raise exception 'No download should have an online year before publication year';
  end if;
end;
$$