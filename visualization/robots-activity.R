library("RPostgreSQL")
library("dplyr")
library("tidyr")
library("ggplot2")

drv <- dbDriver("PostgreSQL")
con <- dbConnect(drv, dbname = "logs", host = "localdocker", port = 5432, user = "postgres", password = "postgres")

query <- paste('select download_hour, country, count(*) as number, is_robot, is_bad_robot',
               'from download',
               'where', 
               'download_hour is not null',
               'and country in (select country from download group by country order by count(*) desc limit 5)',               
               'group by download_hour, country, is_robot, is_bad_robot', 
               'order by download_hour asc', sep=" ")

hours <- dbGetQuery(con, query) %>% tbl_df %>%
    mutate(activity_type = ifelse(!is_robot, "human", ifelse(is_robot & !is_bad_robot, "good_robot", "bad_robot"))) %>%
    select(-is_robot, -is_bad_robot)

plot <- ggplot(hours, aes(x=download_hour, y=number, colour=activity_type)) +
    geom_line() +
    facet_grid(. ~ country)

print(plot)

dbDisconnect(con)