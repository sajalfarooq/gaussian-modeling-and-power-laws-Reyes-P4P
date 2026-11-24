"""Visualize power laws and fit a Gaussian model to a sample."""
import argparse
import csv
import hashlib
import json
from math import erfc, sqrt
from pathlib import Path
import platform
from statistics import NormalDist

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
NORMAL = NormalDist()


def fitted_ks(samples):
    """Two-sided ECDF distance after fitting a Gaussian to each row."""
    samples = np.atleast_2d(samples)
    n = samples.shape[1]
    z = (np.sort(samples, axis=1) - samples.mean(axis=1, keepdims=True))
    z /= samples.std(axis=1, keepdims=True)
    probabilities = np.fromiter(
        (0.5 * erfc(-value / sqrt(2)) for value in z.flat), float, count=z.size
    ).reshape(z.shape)
    grid = np.arange(1, n + 1) / n
    return np.maximum((grid - probabilities).max(axis=1),
                      (probabilities - grid + 1 / n).max(axis=1))


def run_simulations(data, trials, seed):
    seed_fit, seed_mean, seed_stress = np.random.SeedSequence(seed).spawn(3)
    rng = np.random.default_rng(seed_fit)
    null = np.concatenate([
        fitted_ks(rng.normal(size=(min(128, trials - start), data.size)))
        for start in range(0, trials, 128)
    ])
    observed = float(fitted_ks(data)[0])
    exceed = int(np.count_nonzero(null >= observed))
    p_value = (exceed + 1) / (trials + 1)

    # Center uncertainty assuming exchangeable independent observations.
    rng = np.random.default_rng(seed_mean)
    means = np.concatenate([
        rng.choice(data, size=(min(128, trials - start), data.size)).mean(axis=1)
        for start in range(0, trials, 128)
    ])

    # Independent evaluation samples. Laplace has unit variance here.
    rng = np.random.default_rng(seed_stress)
    cutoff = float(np.quantile(null, 0.95, method="higher"))
    stress = []
    for label, draw in [
        ("Normal", rng.normal),
        ("Laplace", lambda size: rng.laplace(scale=1 / sqrt(2), size=size)),
    ]:
        rejected = sum(
            np.count_nonzero(fitted_ks(draw(size=(100, data.size))) > cutoff)
            for _ in range(5)
        )
        proportion = float(rejected / 500)
        z = NORMAL.inv_cdf(0.975)
        denominator = 1 + z**2 / 500
        center = (proportion + z**2 / 1000) / denominator
        margin = z * sqrt(proportion * (1 - proportion) / 500 + z**2 / 1000000) / denominator
        stress.append({
            "generator": label, "replicates": 500, "rejected": int(rejected),
            "rate": proportion, "wilson_95": [max(0, center - margin), min(1, center + margin)],
        })
    return {
        "ks": observed, "p_value": p_value, "exceedances": exceed,
        "p_value_mc_se": sqrt(p_value * (1 - p_value) / trials),
        "mean_bootstrap_95": np.quantile(means, [0.025, 0.975]).tolist(),
        "stress_critical_value": cutoff, "stress": stress,
    }


def chart(path, title, panels):
    """Write a standalone SVG with linear axes and data-space series."""
    width, panel_height = 790, 245
    height = 52 + panel_height * len(panels)
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        '<g font-family="system-ui, sans-serif" fill="#18263d" font-size="13">',
        f'<text x="24" y="30" font-size="21" font-weight="bold">{title}</text>',
    ]
    for i, (label, xlabel, ylabel, bounds, series) in enumerate(panels):
        top, left, span_x, span_y = 78 + i * panel_height, 86, 665, 150
        xmin, xmax, ymin, ymax = bounds

        def px(x):
            return left + span_x * (x - xmin) / (xmax - xmin)

        def py(y):
            return top + span_y * (ymax - y) / (ymax - ymin)

        svg.append(f'<text x="{left}" y="{top-10}" font-weight="bold">{label}</text>')
        for x in np.linspace(xmin, xmax, 6):
            svg.append(f'<text x="{px(x):.2f}" y="{top+span_y+19}" text-anchor="middle">{x:.3g}</text>')
        for y in np.linspace(ymin, ymax, 5):
            svg.extend([
                f'<path d="M{left},{py(y):.2f} h{span_x}" stroke="#dce3ed"/>',
                f'<text x="{left-9}" y="{py(y)+4:.2f}" text-anchor="end">{y:.3g}</text>',
            ])
        svg.extend([
            f'<text x="{left+span_x/2}" y="{top+span_y+39}" text-anchor="middle">{xlabel}</text>',
            f'<text transform="translate(23,{top+span_y/2}) rotate(-90)" text-anchor="middle">{ylabel}</text>',
        ])
        for kind, x, y, color in series:
            if kind == "bars":
                for lo, hi, count in zip(x[:-1], x[1:], y):
                    svg.append(f'<rect x="{px(lo):.2f}" y="{py(count):.2f}" width="{px(hi)-px(lo):.2f}" height="{py(0)-py(count):.2f}" fill="{color}" stroke="white" stroke-width="0.8"/>')
            elif kind == "dots":
                for xi, yi in zip(x, y):
                    svg.append(f'<circle cx="{px(xi):.2f}" cy="{py(yi):.2f}" r="2" fill="{color}" opacity=".55"/>')
            else:
                points = " ".join(f"{px(xi):.2f},{py(yi):.2f}" for xi, yi in zip(x, y))
                svg.append(f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="2"/>')
    path.write_text("\n".join([*svg, "</g>", "</svg>"]), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=ROOT / "original/Python4Physics/data_modified")
    parser.add_argument("--out", type=Path, default=ROOT / "results")
    parser.add_argument("--seed", type=int, default=20261124)
    parser.add_argument("--trials", type=int, default=4999)
    args = parser.parse_args()
    data = np.loadtxt(args.data, ndmin=2)
    if (data.shape[1] != 1 or data.size < 3 or not np.isfinite(data).all()
            or np.ptp(data) == 0 or args.trials < 199 or args.seed < 0):
        parser.error("Provide one finite, nonconstant column with at least 3 values, 199 trials and a nonnegative seed.")
    data = data[:, 0]
    out = args.out
    out.mkdir(parents=True, exist_ok=True)
    n = data.size
    mean, sigma = float(data.mean()), float(data.std())
    fitted = NormalDist(mean, sigma)
    report = {
        "input_sha256": hashlib.sha256(args.data.read_bytes()).hexdigest(),
        "python": platform.python_version(), "numpy": np.__version__,
        "seed": args.seed, "trials": args.trials, "n": n,
        "mean": mean, "sigma_mle": sigma, "sample_sd": float(data.std(ddof=1)),
        "median": float(np.median(data)), "min": float(data.min()), "max": float(data.max()),
        **run_simulations(data, args.trials, args.seed),
    }

    # Compare observed and fitted counts across bin choices.
    with (out / "bin_sensitivity.csv").open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["bins", "lower_edge", "upper_edge", "observed_count", "fitted_expected_count"])
        for bins in (15, 25, 40):
            counts, edges = np.histogram(data, bins=bins)
            expected = n * np.diff([fitted.cdf(e) for e in edges])
            writer.writerows(zip([bins] * bins, edges[:-1], edges[1:], counts, expected))
    report["histogram_25_bin_peak"] = int(np.histogram(data, bins=25)[0].max())
    (out / "summary.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    x = np.linspace(0, 1.95, 196)
    red, blue = "#b52333", "#17678b"
    r, b = ("line", x, x**1.5, red), ("line", x, x**2, blue)
    chart(out / "power_laws.svg", "Power-law comparison", [
        ("Overlay", "x", "y", (0, 1.95, 0, 4), [r, b]),
        ("Red curve · x^1.5", "x", "y", (0, 1.95, 0, 3), [r, ("dots", x[::10], x[::10]**1.5, red)]),
        ("Blue curve · x^2", "x", "y", (0, 1.95, 0, 4), [b, ("dots", x[::10], x[::10]**2, blue)]),
    ])

    counts, edges = np.histogram(data, bins=25)
    x = np.linspace(min(edges[0], mean - 4*sigma), max(edges[-1], mean + 4*sigma), 400)
    height = n * (edges[1] - edges[0]) * np.array([fitted.pdf(value) for value in x])
    theoretical = np.array([fitted.inv_cdf((i + 0.5) / n) for i in range(n)])
    observed = np.sort(data)
    lo = min(theoretical[0], observed[0])
    hi = max(theoretical[-1], observed[-1])
    chart(out / "gaussian.svg", "Gaussian model diagnostics for m0", [
        ("25-bin histogram and fitted Gaussian (red)", "m0", "Count",
         (x[0], x[-1], 0, 1.1 * max(counts.max(), height.max())),
         [("bars", edges, counts, blue), ("line", x, height, red)]),
        ("Normal Q–Q plot and identity line (red)", "Fitted Gaussian quantile", "Observed quantile",
         (lo, hi, lo, hi), [("line", [lo, hi], [lo, hi], red), ("dots", theoretical, observed, blue)]),
    ])
    print(out / "summary.json")


if __name__ == "__main__":
    main()
