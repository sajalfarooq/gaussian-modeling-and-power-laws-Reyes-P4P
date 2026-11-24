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
