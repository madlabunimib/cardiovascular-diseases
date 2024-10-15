# Set CRAN remotes.
repos <- c(CRAN = "https://cloud.r-project.org")
options(repos = repos)
# Set the default number of threads.
Sys.setenv(MAKEFLAGS = paste0("-j", parallel::detectCores()))
# Install `renv`.
source("renv/activate.R")
# Configure `renv` to use the `pak` package.
options(renv.config.pak.enabled = TRUE)
