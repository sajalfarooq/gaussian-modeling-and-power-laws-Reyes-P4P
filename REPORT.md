# Technical report

## Objectives and data

Compare x^1.5 and x^2 on a shared domain and assess a Gaussian model for the m0 sample. The sample consists of 1,000 finite values ranging from 0.85636 to 1.14039. The physical units and acquisition procedure are unspecified. The input directory includes the data and two reference figures.

## Methodology and literature

The analysis uses Python and NumPy to fit a Gaussian by maximum likelihood and generate standalone SVG figures. The fitted location is the arithmetic mean and the fitted scale is the root mean squared deviation from that mean. The histogram curve uses N × bin width × fitted density for display. The bin comparison table integrates the CDF over each bin for exact expected counts under the fitted model. Its expected counts cover the observed range, with Gaussian tail mass outside that range.

The Q–Q plot pairs sorted data with fitted Gaussian quantiles at probabilities (i − 0.5)/N. The two-sided Kolmogorov–Smirnov statistic is the maximum difference between the empirical CDF and the fitted Gaussian CDF, evaluated on both sides of the jumps. Estimating location and scale changes the null distribution, as shown by Lilliefors [1]. Each of 4,999 independent standard-normal null replicates of size 1,000 is refitted using the same maximum-likelihood rule. Using standard-normal replicates follows from location and scale invariance. The p-value is (1 + number of replicate distances at least as large as observed)/(1 + number of replicates), following the modern Monte Carlo workflow documented by SciPy [2]. The implementation here uses NumPy and the Python standard library. It uses maximum-likelihood scale throughout, whereas SciPy's normal-family helper defaults to bias-corrected scale. The mean interval is the 2.5th and 97.5th percentiles of 4,999 independent nonparametric resamples of size 1,000.

A project-specific stress experiment took the empirical 95th-percentile null cutoff and tested 500 fresh Gaussian and 500 fresh unit-variance Laplace samples, each of size 1,000. Gaussian samples check empirical false-positive frequency. Laplace samples quantify detection under one heavier-tailed, more peaked alternative. The rejection-rate intervals are Wilson 95% intervals conditional on the simulated cutoff. Recent comparative research [3] evaluates many tests across skewness, kurtosis and sample size. Our two-generator trial addresses a narrower setting defined by the sample size.

## Results

| Quantity | Observed result |
|---|---:|
| Sample size | 1,000 |
| Sample mean | 1.001321 |
| Gaussian fitted scale | 0.047813 |
| Sample standard deviation | 0.047837 |
| Bootstrap 95% mean interval | 0.998287–1.004303 |
| Fitted KS distance | 0.016806 |
| Monte Carlo p-value | 0.7404 |
| Monte Carlo standard error of p | 0.0062 |
| Simulated 5% critical distance | 0.028929 |
| Gaussian false-positive frequency | 21/500 (4.2%, 95% interval 2.8–6.3%) |
| Laplace rejection frequency | 500/500 (100%, 95% interval 99.2–100%) |

The Q–Q plot and refitted test support the Gaussian as a descriptive approximation at this sample size. The maximum fitted CDF discrepancy was about 1.68 percentage points. The 25-bin histogram peaks at 100 observations. The 15- and 40-bin tables show how the count comparison varies with bin choice. The fitted-CDF test is independent of histogram binning. The experiment detected the chosen Laplace alternative in all 500 simulations, with uncertainty shown by the interval.

## Discussion and future work

Sampling design, units, independence, repeat measurements and instrumentation are unknown. The p-value and bootstrap interval rely on independent observations. The p-value measures compatibility under the Gaussian null and its assumptions. The interval measures uncertainty about the mean under the resampling model. It omits measurement systematics. The stress experiment covers one strong alternative and one sample size. Performance for weak alternatives, dependence or other sample sizes remains unmeasured.

If sampling records become available, first document the meaning and units of m0 and assess dependence or repeated grouping. Tail-sensitive Anderson–Darling checks, additional alternatives, and an independent validation sample are optional extensions motivated by a specific scientific question.

## References

1. Lilliefors, H. W. (1967). On the Kolmogorov–Smirnov Test for Normality with Mean and Variance Unknown. Journal of the American Statistical Association, 62(318), 399–402. [DOI](https://doi.org/10.1080/01621459.1967.10482916)
2. SciPy developers. (2025). goodness_of_fit. SciPy 1.15.1 Reference Guide. [Documentation](https://docs.scipy.org/doc/scipy-1.15.1/reference/generated/scipy.stats.goodness_of_fit.html)
3. Assessing the robustness of normality tests under varying skewness and kurtosis: a practical checklist for public health researchers. (2025). BMC Medical Research Methodology, 25, 206. [Publication record](https://pubmed.ncbi.nlm.nih.gov/40890669/)
