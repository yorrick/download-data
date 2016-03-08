#! /usr/bin/env Rscript 

suppressMessages(library(dplyr))

args <- commandArgs(trailingOnly = TRUE)

path <- args[1]
nb <- args[2]

# sampling function: selects nb elements out of files, with no replacement
select_n <- function(files) {
    sample(files, size = nb, replace = FALSE)
}

log_files <- list.files(path = path, all.files = F, pattern = "^[0-9]{6}.log$")

# extracts years from file names, using first 2 chars of filename
years = substr(log_files, start = 1, stop = 2)

# set the seed so result is stable (stay the same across time)
set.seed(1)
selected_files <- log_files %>% tapply(INDEX = years, FUN = select_n)

for (file in selected_files) {
    cat(file, "\n")
}
