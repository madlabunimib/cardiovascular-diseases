# A Causal Network Model to Estimate the Cardiotoxic Effect of Oncological Treatments in Young Breast Cancer Survivors

## Introduction

This repository contains the code and data used to estimate the cardiotoxic effect of oncological treatments in young breast cancer survivors.

The code is written in `R`. The code is organized in the following way:

- `main.R` is the main script that runs the analysis.
- `Dockerfile` is the file used to create the Docker image.
- `renv.lock` is the file used to create the R environment.

## Usage

If you have Docker installed, then, you can run the following command:

```bash
docker build -t cvds:latest .
docker run cvds:latest
```

If you don't want to use Docker, you can run the following command:

```bash
R -e 'install.packages("renv"); renv::restore()'
Rscript main.R
```
