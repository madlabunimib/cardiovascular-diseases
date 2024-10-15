FROM r-base:4.3.2

WORKDIR /workspace
COPY . .

RUN R -e 'install.packages("renv"); renv::restore()'

CMD Rscript main.R
