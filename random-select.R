#! /usr/bin/env Rscript 

args <- commandArgs(trailingOnly = TRUE)

path <- args[1]
year <- args[2]
nb <- args[3]

file_pattern <- paste0("^", year, "[0-9]{4}.log$")

log_files <- list.files(path = path, all.files = F, 
                pattern = file_pattern)

set.seed(1)
selected_files <- sample(log_files, size = nb, replace = FALSE)

for (file in selected_files) {
    cat(file, "\n")
}
