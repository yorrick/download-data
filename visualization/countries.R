library("RPostgreSQL")
library("dplyr")
library("ggplot2")

drv <- dbDriver("PostgreSQL")
con <- dbConnect(drv, dbname = "logs", host = "localdocker", port = 5432, user = "postgres", password = "postgres")


query <- paste('select count(*) as number, country',
               'from download',
               'where country is not null', 
               'group by country', 
               'order by number desc',
               'limit 10', sep=" ")

downloadCountries <- dbGetQuery(con, query) %>% tbl_df %>%
    # create an ordered factor for countries
    mutate(country = factor(downloadCountries$country, 
                            levels = downloadCountries$country[order(-downloadCountries$number)]))

plot <- ggplot(downloadCountries, aes(x=country, y=number)) +
    theme(axis.text.x = element_text(angle = 90), legend.position="none") +
    geom_histogram(stat="identity") +
    labs(x = "", y = "")

print(plot)

dbDisconnect(con)