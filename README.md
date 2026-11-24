# Gaussian Modeling and Power-Law Visualization in Python

This project visualizes two power-law functions and evaluates a Gaussian model for 1,000 values labeled m0.

## Run and demonstrate

From the repository root with Python 3.12:

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
.\.venv\Scripts\python src/analyze.py
```

On macOS or Linux use `.venv/bin/python`. With NumPy 2.3.5 already installed, run `python src/analyze.py` directly, with no network required. Use `--data` for another plain-text column, `--out` for a separate output directory, and `--seed` and `--trials` to vary the Monte Carlo and bootstrap runs. Default output files are regenerated in place.

- [Technical report](REPORT.md) covers evidence, model, methodology, results, limitations and references.
- [Input data and reference figures](original/Python4Physics/) contains the sample and two reference figures.
- [Analysis](src/analyze.py) is the command-line entry point.
- [Gaussian diagnostics](results/gaussian.svg) and [power-law comparison](results/power_laws.svg) open directly in a browser.
- [Summary](results/summary.json) records numerical results, settings, versions and the input SHA-256.
- [Bin sensitivity](results/bin_sensitivity.csv) gives observed and model-expected counts for 15, 25 and 40 bins.

For a demonstration, run the analysis and review the power-law comparison, Gaussian diagnostics, and simulation results.

## Results at a glance

The Gaussian fit uses all 1,000 m0 values. The sample mean is **1.00132**, and the fitted standard deviation is **0.04781**. The bootstrap 95% interval for the mean is **0.99829 to 1.00430**.

![Histogram with a fitted Gaussian curve and a normal Q–Q plot](results/gaussian.svg)

The red curve shows the expected histogram shape under the fitted Gaussian. The Q–Q plot compares observed and fitted quantiles. The goodness-of-fit test produced a Monte Carlo p-value of **0.7404** from 4,999 simulated samples refitted under the Gaussian model. The test found no evidence against the model under the independent-sampling assumption. The sample's units and collection procedure are unspecified.

## Power-law comparison

![Comparison of x to the power 1.5 and x squared, shown together and separately](results/power_laws.svg)

The curves meet at x = 0 and x = 1. Between those points, x^1.5 is higher. Beyond x = 1, x² grows faster.

## References

1. Lilliefors, H. W. (1967). On the Kolmogorov–Smirnov Test for Normality with Mean and Variance Unknown. Journal of the American Statistical Association, 62(318), 399–402. [DOI](https://doi.org/10.1080/01621459.1967.10482916)
2. SciPy developers. (2025). goodness_of_fit. SciPy 1.15.1 Reference Guide. [Documentation](https://docs.scipy.org/doc/scipy-1.15.1/reference/generated/scipy.stats.goodness_of_fit.html)
3. Assessing the robustness of normality tests under varying skewness and kurtosis: a practical checklist for public health researchers. (2025). BMC Medical Research Methodology, 25, 206. [Publication record](https://pubmed.ncbi.nlm.nih.gov/40890669/)
