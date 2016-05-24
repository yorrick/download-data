library("dplyr")
library("tidyr")
library("ggplot2")

setwd("~/download-data/data/")

#activityFile <- "110302-sample.log.activity.csv"
#activityFile <- "130306.log.activity.csv"
activityFile <- "130206.log.activity.csv"


compute_source_type <- function(total, download, css, javascript, image) {
    ifelse(download >= 20 & download / total >= 0.9 & css == 0 & javascript == 0 & image == 0, "robot", "human")
}


activity <- read.csv(activityFile) %>% tbl_df %>% 
    mutate(declared_source_type = ifelse(good_robot > 0, "robot", "human")) %>%
    mutate(computed_source_type = compute_source_type(total, download, css, javascript, image)) %>%
    select(-good_robot, -maybe_human) %>%
    #filter(total > 100) %>%
    gather(type, value, download, css, javascript, image) %>%
    mutate(ratio = value / total) 

# bad robots
#activity %>% filter(user_ip %in% c("41.83.44.215", "41.83.47.224", "185.12.14.122"))

plot <- ggplot(activity, aes(total, ratio)) +
    geom_point(alpha = 0.7, aes(color = declared_source_type)) +
    scale_x_log10() + 
    labs(x="Total activity", y="Activity") +
    facet_wrap(~type)

print(plot)
    
    
    
    
    
    
    
    