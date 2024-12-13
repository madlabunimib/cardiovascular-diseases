library(bnlearn)
library(Rgraphviz)
library(gRain)
library(splitTools)
library(caret)
library(pROC)
library(rms)
library(zeallot)

library(igraph)
library(readxl)
library(pcalg)
library(stdReg)

#### Causal Discovery ####

# Load data frame.
df <- read.csv("./data/preprocessed.csv", colClasses = "factor", na.string = "")
summary(df)

# Load model from string.
prior_bn <- paste0(readLines("./data/model.txt"), collapse = "\n")
prior_bn <- gsub("\n", "", prior_bn)
prior_bn <- gsub("\t", "", prior_bn)
prior_bn <- gsub("\r", "", prior_bn)
prior_bn <- gsub(" ", "_", tolower(prior_bn))
prior_bn <- model2network(prior_bn)
print(prior_bn)

# Plot prior model.
pdf(paste0("./data/prior_model.pdf"))
graphviz.plot(prior_bn, shape = "rectangle")
dev.off()

# Split dataset depending on the population.
df_0 <- df[df$cohort == "h", ]
df_1 <- df[df$cohort == "pb", ]

# Set prediction target.
target <- "cvds"

# Set rng seed.
seed <- 31
set.seed(seed)

# Generate train and test indexes using stratification.
c(train, test) %<-% partition(
    df_1[[target]],
    p = c(0.6, 0.4),
    type = "stratified",
    shuffle = TRUE,
    seed = seed
)
# Split dataset in train and test, add reference population.
train <- rbind(df_0, df_1[train, ])
test <- df_1[test, ]

print(paste0(
    "Train ratio w.r.t. overall sample size: ",
    round(nrow(train) / (nrow(train) + nrow(test)), digits = 3)
))

# Fit prior model.
print("Fitting prior model ... ")
prior_bn <- bn.fit(prior_bn, train, method = "bayes")

# Extend prior model.
print("Performing Structural EM to extend prior model ... ")
extended_bn <- structural.em(
    train,
    maximize.args = list(whitelist = arcs(prior_bn)),
    fit = "bayes",
    start = prior_bn,
    max.iter = 5,
    return.all = TRUE
)
extended_bn <- extended_bn$fitted

# Plot extended model.
pdf(paste0("./data/extended_model.pdf"))
graphviz.plot(bn.net(extended_bn), shape = "rectangle")
dev.off()

# Export extended model.
write.bif("./data/extended_model.bif", extended_bn)
write.net("./data/extended_model.net", extended_bn)

# Compare models.
pdf(paste0("./data/compared_models.pdf"))
graphviz.compare(
    bn.net(prior_bn),
    bn.net(extended_bn),
    shape = "rectangle",
    diff.args = list(
        fp.col = "blue",
        fp.lwd = 3
    )
)
dev.off()

# Plot fitted model.
pdf(paste0("./data/prior_model_fitted.pdf"))
graphviz.chart(prior_bn)
dev.off()
pdf(paste0("./data/extended_model_fitted.pdf"))
graphviz.chart(extended_bn)
dev.off()

# Define predict function with NA.
predict_with_na <- function(bn, data, target) {
    # Extract true labels.
    true_labels <- data[[target]]
    # Predict labels.
    pred_labels <- c()
    pred_probs <- data.frame()

    for (i in seq_len(nrow(data))) {
        # Include variables that are not NA.
        not_na <- names(which(colSums(is.na(data[i, ])) == 0))
        not_na <- not_na[!not_na %in% c(target)]
        # Predict i-th row. Suppress warnings, which will cause GridR to fail.
        p <- predict(
            bn,
            node = target,
            data = data[i, not_na],
            method = "bayes-lw",
            n = 1000,
            from = not_na,
            prob = TRUE
        )
        # Append results.
        pred_labels <- append(pred_labels, p)
        pred_probs <- rbind(pred_probs, t(attributes(p)$prob))
    }

    list(
        true_labels = true_labels,
        pred_labels = pred_labels,
        pred_probs = pred_probs
    )
}

# In- and out-of-sample prediction.
prior_in_sample <- predict_with_na(prior_bn, train, target)
prior_out_of_sample <- predict_with_na(prior_bn, test, target)
extended_in_sample <- predict_with_na(extended_bn, train, target)
extended_out_of_sample <- predict_with_na(extended_bn, test, target)

# Plot ROC AUC.
plot_roc <- function(data, label) {
    pdf(paste0("./data/", label, ".pdf"))
    roc_curve <- pROC::roc(
        data$true_labels,
        data$pred_probs[, 2],
        smoothed = TRUE,
        # CI
        ci = TRUE, ci.alpha = 0.95, stratified = FALSE,
        # PLOT
        plot = TRUE, grid = TRUE, show.thres = TRUE,
        auc.polygon = TRUE, max.auc.polygon = TRUE, print.auc = TRUE,
    )

    roc_curve <- pROC::ci.se(roc_curve)

    plot(roc_curve, type = "shape", col = "lightblue")
    plot(roc_curve, type = "bars")
    dev.off()
}

plot_roc(prior_in_sample, "prior_model_in_roc")
plot_roc(prior_out_of_sample, "prior_model_out_roc")
plot_roc(extended_in_sample, "extended_model_in_roc")
plot_roc(extended_out_of_sample, "extended_model_out_roc")

# Plot calibration curve.
pdf(paste0("./data/prior_model_in_calibration.pdf"))
val.prob(prior_in_sample$pred_probs[, 2], prior_in_sample$true_labels == "yes")
dev.off()
pdf(paste0("./data/prior_model_out_calibration.pdf"))
val.prob(prior_out_of_sample$pred_probs[, 2], prior_out_of_sample$true_labels == "yes")
dev.off()
pdf(paste0("./data/extended_model_in_calibration.pdf"))
val.prob(extended_in_sample$pred_probs[, 2], extended_in_sample$true_labels == "yes")
dev.off()
pdf(paste0("./data/extended_model_out_calibration.pdf"))
val.prob(extended_out_of_sample$pred_probs[, 2], extended_out_of_sample$true_labels == "yes")
dev.off()

#### Causal Inference ####

# Return the ACE estimator as LaTeX formula.
identify_ace <- function(x, y, m) {
    # Get variables.
    v <- nodes(m)
    # Get adjacency matrix.
    a <- bnlearn::amat(m)
    colnames(a) <- NULL
    rownames(a) <- NULL
    # Labels to index.
    x <- which(v == x)
    y <- which(v == y)
    # Get adjustment set.
    z <- pcalg::backdoor(a, x, y, type = "dag", verbose = TRUE)
    # Index to labels.
    sapply(z, function(i) v[i])
}

# Estimate ACE from LaTeX (adjustment) formula and the data and target "yes" level.
estimate_ace <- function(x, y, z, d, l, r) {
    # Set level "l" as 1.
    d_prime <- data.frame(d)
    d_prime[, y] <- as.factor(ifelse(d_prime[, y] == l, 1, 0))
    # Define formula.
    f <- paste(y, "~", x)
    if (!is.null(z)) {
        f <- paste(f, "+", paste(z, collapse = "+"))
    }
    # Fit model.
    f <- glm(as.formula(f), data = d_prime, family = "binomial")
    # Estimate the ACE.
    f <- stdGlm(f, data = d_prime, X = x)

    summary(f, contrast = "ratio", reference = r)
}

# Read model from file.
m <- read.bif("./data/extended_model.bif")
# Read the data from file.
d <- read.csv("./data/preprocessed.csv", colClasses = "factor", na.string = "")
# Impute missing data.
d <- impute(m, data = d, method = "bayes-lw")
# Read treatment-outcome pairs from file.
p <- read_excel("./data/treatment_outcome_pairs.xlsx")
p <- as.data.frame(p)

# Open log file.
sink("./data/causal_inference.log")
# Print separator.
sep <- paste(rep("=", 80), collapse = "")
cat(sep, "\n")

# Estimate ACE for each treatment-outcome pair.
for (i in 1:nrow(p)) {
    # Identify effect.
    x <- p[i, "treatment"]
    y <- p[i, "outcome"]
    z <- identify_ace(x, y, m)
    # Estimate effect unadjusted and adjusted effects.
    l <- p[i, "level"]
    r <- p[i, "reference"]
    print("Unadjusted effect:")
    print(estimate_ace(x, y, NULL, d, l, r))
    print("Adjusted effect:")
    print(estimate_ace(x, y, z, d, l, r))
    # Print formatted output.
    cat(sep, "\n")
}

# Close log file.
sink()

# Print message.
cat("Check ./data/causal_inference.log for results.\n")
