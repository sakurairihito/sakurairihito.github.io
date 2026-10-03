"""Reproduce the Black–Scholes surface and low-rank experiment at /compression/.

Run: python3 _assets/scripts/bs1d_demo.py
Requires numpy, scipy, matplotlib. All 128 x 128 prices are evaluated for
diagnostics and full-residual pivot search; retained entries are NOT a budget
of function evaluations. Errors describe this grid, not a continuum guarantee.
"""
from pathlib import Path
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
import numpy as np
from scipy.integrate import quad
from scipy.special import ndtr

OUTPUT = Path(__file__).resolve().parents[1] / "compression"
GREEN, ORANGE, INK = "#22634e", "#b56432", "#24312d"
STRIKE, RATE, MATURITY = 100.0, 0.03, 1.0


def call_price(spot, volatility, strike=STRIKE, rate=RATE, maturity=MATURITY):
    """No-dividend European call, positive spot/volatility/time."""
    scale = volatility * np.sqrt(maturity)
    d1 = (np.log(spot / strike) + (rate + volatility**2 / 2) * maturity) / scale
    return spot * ndtr(d1) - strike * np.exp(-rate * maturity) * ndtr(d1 - scale)


def cross_steps(a, max_rank):
    """Greedy maximum-residual pivots and skeleton reconstruction."""
    rows, columns = [], []
    residual = a.copy()
    for rank in range(1, max_rank + 1):
        magnitude = np.abs(residual)
        magnitude[rows, :] = -1
        magnitude[:, columns] = -1
        i, j = np.unravel_index(np.argmax(magnitude), a.shape)
        rows.append(int(i))
        columns.append(int(j))
        p = a[np.ix_(rows, columns)]
        approximation = a[:, columns] @ np.linalg.solve(p, a[rows, :])
        residual = a - approximation
        yield rank, rows.copy(), columns.copy(), approximation, float(np.linalg.cond(p))


def save(fig, filename):
    fig.savefig(OUTPUT / filename, dpi=180, facecolor="white", bbox_inches="tight")
    plt.close(fig)


def surface(ax, spots, vols, values, title):
    x, y = np.meshgrid(spots, vols * 100, indexing="ij")
    ax.plot_surface(x, y, values, cmap="viridis", norm=Normalize(0, 65),
                    rcount=128, ccount=128, linewidth=0, edgecolor="none", antialiased=False)
    ax.set(xlabel="Spot price S", ylabel="Volatility (%)",
           title=title, xlim=(50, 150), ylim=(5, 60), zlim=(0, 65))
    ax.view_init(elev=26, azim=-125)
    ax.set_box_aspect((1.2, 1, .8))
    ax.xaxis.labelpad = ax.yaxis.labelpad = 9
    ax.zaxis.labelpad = 7
    ax.text2D(.01, .84, "Call price C", transform=ax.transAxes, fontsize=10)


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11,
                         "text.color": INK, "axes.labelcolor": INK,
                         "axes.spines.top": False, "axes.spines.right": False})
    n, selected_rank, max_rank = 128, 8, 12
    spots, vols = np.linspace(50, 150, n), np.linspace(.05, .60, n)
    a = call_price(spots[:, None], vols[None, :])
    u, singular, vt = np.linalg.svd(a, full_matrices=False)
    norm = np.linalg.norm(a)
    steps = list(cross_steps(a, max_rank))
    _, rows, columns, approximation, condition = steps[selected_rank - 1]
    mask = np.zeros(a.shape, dtype=bool)
    mask[rows, :] = True
    mask[:, columns] = True
    errors = []
    for rank, _, _, b, cond in steps:
        best = (u[:, :rank] * singular[:rank]) @ vt[:rank]
        svd_error = float(np.linalg.norm(a - best) / norm)
        mci_error = float(np.linalg.norm(a - b) / norm)
        assert np.isclose(svd_error, np.linalg.norm(singular[rank:]) / norm, atol=1e-14)
        assert svd_error <= mci_error + 1e-14
        errors.append({"rank": rank, "svd_relative_frobenius": svd_error,
                       "mci_relative_frobenius": mci_error,
                       "mci_max_absolute": float(np.max(np.abs(a - b))),
                       "retained_unique_entries": rank * (2*n) - rank**2,
                       "pivot_condition_number": cond})

    # Independent checks against discounted payoff integration, not the BS formula.
    for spot, vol in [(80., .1), (100., .2), (120., .5)]:
        cutoff = (np.log(STRIKE / spot) - (RATE - vol**2/2)*MATURITY) / (vol*np.sqrt(MATURITY))
        def integrand(z):
            terminal = spot * np.exp((RATE-vol**2/2)*MATURITY + vol*np.sqrt(MATURITY)*z)
            return (terminal-STRIKE) * np.exp(-z*z/2) / np.sqrt(2*np.pi)
        expected = np.exp(-RATE*MATURITY) * quad(integrand, cutoff, 12, epsabs=1e-10)[0]
        assert np.isclose(call_price(spot, vol), expected, rtol=1e-10, atol=1e-10)
    assert np.all(a >= np.maximum(spots[:, None] - STRIKE*np.exp(-RATE*MATURITY), 0) - 1e-12)
    assert np.all(a <= spots[:, None])
    assert np.all(np.diff(a, axis=0) >= -1e-12) and np.all(np.diff(a, axis=1) >= -1e-12)
    assert np.allclose(approximation[rows, :], a[rows, :], atol=1e-9, rtol=0)
    assert np.allclose(approximation[:, columns], a[:, columns], atol=1e-9, rtol=0)
    assert mask.sum() == selected_rank * (2*n) - selected_rank**2 == 1984

    fig = plt.figure(figsize=(9, 7.2), layout="constrained")
    ax = fig.add_subplot(111, projection="3d")
    surface(ax, spots, vols, a, "Black–Scholes: one asset, two varying inputs")
    fig.suptitle("K = 100   |   time to maturity = 1 year   |   rate = 3%   |   no dividends", fontsize=11)
    save(fig, "bs1d-surface.png")

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.7), layout="constrained")
    axes[0].semilogy(np.arange(1, 25), singular[:24]/singular[0], "o-", color=GREEN, markersize=4)
    axes[0].set(title="Singular values decay rapidly", xlabel="Singular-value index k",
                ylabel="Singular value / largest", xticks=[1, 4, 8, 12, 16, 20, 24])
    ranks = np.arange(1, max_rank+1)
    axes[1].semilogy(ranks, [e["svd_relative_frobenius"] for e in errors], "o-", color=GREEN, label="Truncated SVD (best on this grid)")
    axes[1].semilogy(ranks, [e["mci_relative_frobenius"] for e in errors], "s--", color=ORANGE, label="Matrix cross interpolation")
    axes[1].set(title="How many components are needed?", xlabel="Approximation rank r",
                ylabel="Relative Frobenius error", xticks=[1, 2, 4, 6, 8, 10, 12])
    axes[1].legend(fontsize=9)
    for ax in axes:
        ax.grid(alpha=.2)
    save(fig, "bs1d-rank.png")

    fig = plt.figure(figsize=(11, 9.5), layout="constrained")
    surface(fig.add_subplot(221, projection="3d"), spots, vols, a, "Original price surface")
    surface(fig.add_subplot(222, projection="3d"), spots, vols, approximation, "MCI reconstruction: rank 8")
    ax = fig.add_subplot(223)
    cmap = plt.colormaps["viridis"].copy()
    cmap.set_bad("#edf0ec")
    # pcolormesh locates selected rows and columns on the actual sample coordinates.
    im = ax.pcolormesh(spots, vols*100, np.ma.masked_where(~mask, a).T,
                       shading="nearest", cmap=cmap, vmin=0, vmax=65, rasterized=True)
    ax.set(title="Selected cross: 1,984 / 16,384 entries", xlabel="Spot price S", ylabel="Volatility (%)",
           xlim=(50, 150), ylim=(5, 60))
    fig.colorbar(im, ax=ax, shrink=.75, label="Call price")
    ax = fig.add_subplot(224)
    im = ax.pcolormesh(spots, vols*100, np.abs(a-approximation).T, shading="nearest", cmap="magma", rasterized=True)
    ax.set(title="Absolute error (separate color scale)", xlabel="Spot price S", ylabel="Volatility (%)",
           xlim=(50, 150), ylim=(5, 60))
    fig.colorbar(im, ax=ax, shrink=.75, label="Absolute price error")
    save(fig, "bs1d-cross.png")

    metrics = {"model": "Black-Scholes, European call, no dividends", "strike": STRIKE,
               "rate": RATE, "time_to_maturity_years": MATURITY,
               "spot_range": [50, 150], "volatility_range": [.05, .6],
               "grid": [n, n], "grid_spacing": "uniform, inclusive endpoints",
               "selected_rank": selected_rank, "retained_fraction": float(mask.mean()),
               "selected_rows_zero_based": rows, "selected_columns_zero_based": columns,
               "selected_spots": spots[rows].tolist(), "selected_volatilities": vols[columns].tolist(),
               "singular_values": singular.tolist(), "errors_by_rank": errors,
               "pivot_search": "full residual; all 16384 grid entries evaluated",
               "error_scope": "128 x 128 grid only; no off-grid or Greek accuracy claim"}
    (OUTPUT / "bs1d-results.json").write_text(json.dumps(metrics, indent=2)+"\n")
    print(json.dumps({"selected": errors[selected_rank-1], "retained_fraction": float(mask.mean()),
                      "errors_by_rank": errors}, indent=2))


if __name__ == "__main__":
    main()
