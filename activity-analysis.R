library("dplyr")
library("tidyr")
library("ggplot2")

setwd("~/download-data/data/")

#activityFile <- "110302-sample.activity.csv"
#activityFile <- "130306.log.activity.csv"
activityFile <- "130206.log.activity.csv"

activity <- read.csv(activityFile) %>% tbl_df %>% 
    mutate(source_type = ifelse(good_robot > 0, "robot", "maybe_human")) %>% 
    select(-good_robot, -maybe_human) %>%
    #filter(total > 100) %>%
    gather(type, value, download, css, javascript, image)

# bad robots
#activity %>% filter(user_ip %in% c("41.83.44.215", "41.83.47.224", "185.12.14.122"))

plot <- ggplot(activity, aes(total, value)) +
    geom_point(alpha = 0.7, aes(color = source_type)) +
    scale_x_log10() + scale_y_log10() +
    labs(x="Total activity", y="Activity") +
    facet_wrap(~type)

print(plot)
    
    
    
    
    
    
    
    