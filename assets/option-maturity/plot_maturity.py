"""Reproduce the /option-maturity/ European-call figure and numerical checks.

Run: python3 -B plot_maturity.py new_results
Requires NumPy, SciPy, and Matplotlib. The output directory must not exist.
"""
import argparse
import csv
import json
import math
from pathlib import Path
import platform

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import scipy
from scipy.integrate import quad
from scipy.special import ndtr

STRIKE, VOLATILITY = 100.0, 0.2
MATURITIES = [1.0, 0.25, 30 / 365, 1 / 365]
LABELS = ["1 year", "3 months (0.25 yr)", "30 days", "1 day"]
COLORS = ["#2f62b5", "#087f81", "#c07010", "#ae3973"]


def call_price(spot, maturity):
    """Black-Scholes call for positive spot, r=q=0, including expiry."""
    spot = np.asarray(spot, dtype=float)
    if np.any(spot <= 0) or maturity < 0:
        raise ValueError("Spot must be positive and maturity nonnegative.")
    if maturity == 0:
        return np.maximum(spot - STRIKE, 0)
    width = VOLATILITY * np.sqrt(maturity)
    d1 = np.log(spot / STRIKE) / width + width / 2
    return spot * ndtr(d1) - STRIKE * ndtr(d1 - width)


def numerical_checks():
    # Integrate the terminal payoff independently of the closed-form price.
    discrepancies = []
    for spot, maturity in [(90., 1.), (100., .25), (100., 1/365), (110., 30/365)]:
        width = VOLATILITY * math.sqrt(maturity)
        cutoff = (math.log(STRIKE / spot) + width**2 / 2) / width
        price = quad(
            lambda z: max(spot * math.exp(-width**2 / 2 + width*z) - STRIKE, 0)
            * math.exp(-z*z/2) / math.sqrt(2*math.pi),
            max(cutoff, -12), 12, epsabs=1e-11, epsrel=1e-11,
        )[0]
        discrepancies.append(abs(price - float(call_price(spot, maturity))))
    assert max(discrepancies) < 1e-10
    grid = np.linspace(60, 140, 3201)
    values = np.array([call_price(grid, t) for t in [0, *reversed(MATURITIES)]])
    assert np.all(np.diff(values, axis=0) >= -1e-12)
    assert np.all(values >= np.maximum(grid - STRIKE, 0) - 1e-12)
    assert np.all(values <= grid + 1e-12)
    expiry_error = float(np.max(np.abs(call_price(grid, 1e-12) - call_price(grid, 0))))
    assert expiry_error < 1e-5
    # Check the displayed spot derivatives with centered price differences.
    derivative_errors = []
    step = 1e-3
    for maturity in MATURITIES:
        for spot in [95., 100., 105.]:
            width = VOLATILITY * math.sqrt(maturity)
            d1 = math.log(spot / STRIKE) / width + width / 2
            delta = ndtr(d1)
            gamma = math.exp(-d1*d1/2) / (math.sqrt(2*math.pi)*spot*width)
            left, middle, right = (float(call_price(s, maturity))
                                   for s in [spot-step, spot, spot+step])
            delta_error = abs((right-left)/(2*step) - delta)
            gamma_error = abs((right-2*middle+left)/step**2 - gamma)
            assert delta_error < 1e-7 and gamma_error < 1e-6
            derivative_errors.append((delta_error, gamma_error))
    return {
        "model": "Black-Scholes European call",
        "strike": STRIKE, "volatility": VOLATILITY, "rate": 0, "dividend_yield": 0,
        "day_convention": "365 days/year; three months = 0.25 years",
        "quadrature_max_abs_discrepancy": max(discrepancies),
        "expiry_limit_grid_max_abs_error_at_1e-12_years": expiry_error,
        "delta_finite_difference_max_abs_discrepancy": max(x[0] for x in derivative_errors),
        "gamma_finite_difference_max_abs_discrepancy": max(x[1] for x in derivative_errors),
        "atm_prices": [{"remaining_years": t, "price": float(call_price(STRIKE, t))}
                       for t in [*MATURITIES, 0]],
        "versions": {"python": platform.python_version(), "numpy": np.__version__,
                     "scipy": scipy.__version__, "matplotlib": matplotlib.__version__},
    }


def main(output):
    summary = numerical_checks()
    output.mkdir(parents=True, exist_ok=False)
    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 11,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.edgecolor": "#a7b1bd", "axes.labelcolor": "#263445",
        "text.color": "#263445", "xtick.color": "#526171", "ytick.color": "#526171",
        "svg.fonttype": "path",
    })
    spots = np.linspace(60, 140, 3201)
    fig, axes = plt.subplots(1, 2, figsize=(12, 5.5))
    fig.subplots_adjust(top=.72, bottom=.19, left=.075, right=.975, wspace=.22)
    fig.suptitle("As expiry approaches, the price approaches the payoff", x=.075, y=.97,
                 ha="left", fontsize=18)
    fig.text(.075, .89, "European call  |  K = 100  |  volatility = 20%  |  rate = dividend yield = 0", fontsize=11)
    for ax in axes:
        ax.axvline(STRIKE, color="#a7b1bd", lw=1, zorder=0)
        ax.grid(axis="y", color="#dce2e8", lw=.7, zorder=0)
        for maturity, label, color in zip(MATURITIES, LABELS, COLORS):
            ax.plot(spots, call_price(spots, maturity), lw=2.4, color=color, label=label)
        ax.plot(spots, call_price(spots, 0), color="#263445", lw=1.8, ls=(0, (5, 3)),
                label="Expiry payoff")
        ax.set_xlabel("Spot price S", labelpad=10)
        ax.set_ylabel("Call price C", labelpad=10)
    axes[0].set(xlim=(60, 140), ylim=(-.7, 43), xticks=[60, 80, 100, 120, 140])
    axes[0].set_title("Price curves", loc="left", fontsize=13, pad=14)
    axes[1].set(xlim=(94, 106), ylim=(-.25, 12), xticks=[94, 97, 100, 103, 106])
    axes[1].set_title("Near the strike", loc="left", fontsize=13, pad=14)
    for maturity, color in zip(MATURITIES, COLORS):
        price = float(call_price(STRIKE, maturity))
        axes[1].scatter(STRIKE, price, color=color, s=26, zorder=5)
        axes[1].annotate(f"{price:.2f}", (STRIKE, price), xytext=(-10, 8),
                         textcoords="offset points", ha="right", color=color, fontsize=10,
                         bbox={"facecolor": "white", "edgecolor": "none", "pad": 1})
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper left", bbox_to_anchor=(.065, .855),
               ncol=5, frameon=False, handlelength=2, columnspacing=1.8, fontsize=10)
    fig.text(.075, .055, "Other inputs are fixed. Every positive-maturity curve is smooth; the kink appears at expiry.", fontsize=10)
    for suffix in ("png", "svg"):
        fig.savefig(output / f"call-maturity.{suffix}", dpi=190, facecolor="white")
    plt.close(fig)
    with (output / "call-maturity.csv").open("w", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["spot", "remaining_years", "call_price"])
        for maturity in [*MATURITIES, 0]:
            writer.writerows(zip(spots, np.full_like(spots, maturity), call_price(spots, maturity)))
    (output / "checks.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path, help="New output directory (must not exist)")
    main(parser.parse_args().output)
