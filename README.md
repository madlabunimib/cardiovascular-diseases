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

## Graphical User Interface (GUI)

The folder `gui` contains the code to run the graphical user interface (GUI) to estimate the cardiotoxic effect of oncological treatments in young breast cancer survivors. The GUI is written in `Python` using the `pysmile` package. Run the `main.py` script to start the GUI.

## Citations

- Bernasconi, Alice, et al. "A Causal Network Model to Estimate the Cardiotoxic Effect of Oncological Treatments in Young Breast Cancer Survivors." Progress in Artificial Intelligence (2024): 1-13.
- Bernasconi, Alice, et al. "From Real-World Data to Causally Interpretable Models: A Bayesian Network to Predict Cardiovascular Diseases in Adolescents and Young Adults with Breast Cancer." Cancers 16.21 (2024): 3643.
