do
$$
declare
  l_count integer;
begin
  select count(*)
    into l_count
  from foo
  where is_bad_foo;
  if (l_count > 0) then
    raise exception 'too may rows';
  end if;
end;
$$