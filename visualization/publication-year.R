library("RPostgreSQL")
library("dplyr")
library("ggplot2")

drv <- dbDriver("PostgreSQL")
con <- dbConnect(drv, dbname = "logs", host = "localdocker", port = 5432, user = "postgres", password = "postgres")

query <- paste('select count(*) as number, publication_year',
               'from download',
               'group by publication_year', 
               'order by publication_year desc', sep=" ")

downloadAges <- dbGetQuery(con, query) %>% tbl_df
    
plot <- ggplot(downloadAges, aes(x=publication_year, y=number)) +
    geom_line() +
    labs(
        x = "Année de publication des articles téléchargés",
        y = "Nombre d'articles téléchargés"
    )

print(plot)

