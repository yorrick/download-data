library("RPostgreSQL")
library("dplyr")
library("ggplot2")

drv <- dbDriver("PostgreSQL")
con <- dbConnect(drv, dbname = "logs", host = "localdocker", port = 5432, user = "postgres", password = "postgres")

query <- paste('select download_hour, country, count(*) as number',
               'from download',
               'where', 
               'download_hour is not null',
               'and country in (select country from download group by country order by count(*) desc limit 5)',               
               'group by download_hour, country', 
               'order by download_hour asc', sep=" ")

hours <- dbGetQuery(con, query) %>% tbl_df

plot <- ggplot(hours, aes(x=download_hour, y=number, colour=country)) +
    geom_line()

print(plot)

dbDisconnect(con)