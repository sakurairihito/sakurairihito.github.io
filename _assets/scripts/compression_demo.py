"""Reproduce the numerical example and figures for /compression/.

Run: python3 _assets/scripts/compression_demo.py
Requires numpy and matplotlib; not needed for the Franklin site build.
This teaching example uses full-matrix pivot search. Reported element counts
measure the retained cross, not the evaluations required to find that cross.
"""
from pathlib import Path
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

OUTPUT = Path(__file__).resolve().parents[1] / "compression"
GREEN = "#22634e"
ORANGE = "#b56432"
INK = "#24312d"
GRAY = "#b8c1bc"


def sample_function(t):
    return (np.cos(2 * np.pi * 2 * t)
            + 0.35 * np.sin(2 * np.pi * 11 * t)
            + 0.15 * np.cos(2 * np.pi * 23 * t))


def cross_steps(a, max_rank):
    """Full residual pivoting, then C solve(P, R); no explicit inverse."""
    rows, columns = [], []
    residual = a.copy()
    for rank in range(1, max_rank + 1):
        magnitude = np.abs(residual)
        magnitude[rows, :] = -1
        magnitude[:, columns] = -1
        i, j = np.unravel_index(np.argmax(magnitude), a.shape)
        rows.append(int(i))
        columns.append(int(j))
        pivot = a[np.ix_(rows, columns)]
        approximation = a[:, columns] @ np.linalg.solve(pivot, a[rows, :])
        residual = a - approximation
        yield rank, rows.copy(), columns.copy(), approximation


def save(fig, name):
    fig.savefig(OUTPUT / name, dpi=180, facecolor="white", bbox_inches="tight")
    plt.close(fig)


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 11,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.labelcolor": INK, "text.color": INK,
        "xtick.color": INK, "ytick.color": INK,
        "axes.titleweight": "medium", "figure.constrained_layout.use": True,
    })
    n = 64
    t = np.arange(n * n) / (n * n)
    values = sample_function(t)
    a = values.reshape(n, n)
    singular = np.linalg.svd(a, compute_uv=False)
    steps = list(cross_steps(a, 6))
    rank, rows, columns, approximation = steps[-1]
    relative_error = np.linalg.norm(a - approximation) / np.linalg.norm(a)
    retained = rank * (2 * n) - rank * rank

    # Independent numerical checks: Fourier support, exact separation identity,
    # rank bound, reconstruction, and interpolation at selected rows/columns.
    spectrum = np.abs(np.fft.fft(values) / values.size)
    assert set(np.flatnonzero(spectrum > 1e-12)) == {2, 11, 23, values.size-2, values.size-11, values.size-23}
    i, j = np.indices((n, n))
    assert np.allclose(a, sample_function(i / n + j / (n * n)))
    assert np.count_nonzero(singular > singular[0] * 1e-12) == 6
    assert relative_error < 1e-10
    assert np.allclose(approximation[rows, :], a[rows, :], atol=1e-10)
    assert np.allclose(approximation[:, columns], a[:, columns], atol=1e-10)
    mask = np.zeros(a.shape, dtype=bool)
    mask[rows, :] = True
    mask[:, columns] = True
    assert int(mask.sum()) == retained == 732

    terms = [np.cos(2*np.pi*2*t), 0.35*np.sin(2*np.pi*11*t), 0.15*np.cos(2*np.pi*23*t)]
    fig, axes = plt.subplots(3, 1, figsize=(10, 7.2), sharex=True, sharey=True)
    for count, ax in enumerate(axes, 1):
        ax.plot(t, values, color=GRAY, linewidth=2.5, label="Original function")
        ax.plot(t, np.sum(terms[:count], axis=0), color=GREEN, linewidth=1.3,
                linestyle="--" if count == 3 else "-", label=f"{count} real Fourier component(s)")
        ax.set_ylabel("f(t)")
        ax.legend(loc="upper right", fontsize=9, framealpha=0.95)
        ax.set_ylim(-1.65, 1.9)
        ax.grid(alpha=0.15)
    axes[-1].set_xlabel("t")
    axes[-1].set_xlim(0, 1)
    save(fig, "fourier-components.png")

    fig, axes = plt.subplots(1, 2, figsize=(10, 4.6))
    limit = float(np.max(np.abs(a)))
    im = axes[0].imshow(a, cmap="RdBu_r", vmin=-limit, vmax=limit, origin="lower", interpolation="nearest")
    axes[0].set(title="4,096 samples reshaped into 64 × 64", xlabel="Column j", ylabel="Row i")
    fig.colorbar(im, ax=axes[0], shrink=0.8, label="Function value")
    k = np.arange(1, 17)
    axes[1].semilogy(k, singular[:16]/singular[0], color=GRAY, linewidth=1)
    axes[1].semilogy(k[:6], singular[:6]/singular[0], "o", color=GREEN, label="First 6 singular values")
    axes[1].semilogy(k[6:], singular[6:16]/singular[0], "x", color=ORANGE, label="Floating-point residual")
    axes[1].axvline(6.5, color=GRAY, linestyle=":")
    axes[1].set(title="Rank at most 6 in exact arithmetic", xlabel="Singular-value index", ylabel="Singular value / largest")
    axes[1].set_xticks([1, 3, 6, 9, 12, 16])
    axes[1].legend(fontsize=9, loc="upper right")
    axes[1].grid(alpha=0.15)
    save(fig, "matrix-and-rank.png")

    fig, axes = plt.subplots(2, 2, figsize=(10, 8.4))
    data = [a, np.ma.masked_where(~mask, a), approximation]
    titles = ["Original: 4,096 elements", "Cross: 6 rows + 6 columns (732 elements)", "MCI reconstruction from the cross"]
    cmap = plt.colormaps["RdBu_r"].copy()
    cmap.set_bad("#edf0ec")
    for ax, values_to_plot, title in zip(axes.flat, data, titles):
        im = ax.imshow(values_to_plot, cmap=cmap, vmin=-limit, vmax=limit,
                       origin="lower", interpolation="nearest")
        ax.set(title=title, xlabel="Column j", ylabel="Row i")
        fig.colorbar(im, ax=ax, shrink=0.8, label="Function value")
    x, y = np.meshgrid(columns, rows)
    axes[0, 1].scatter(x.ravel(), y.ravel(), s=12, color=INK, marker=".")
    error = np.maximum(np.abs(a - approximation), 1e-16)
    im = axes[1, 1].imshow(np.log10(error), cmap="magma", vmin=-16, vmax=-12,
                           origin="lower", interpolation="nearest")
    axes[1, 1].set(title=f"Relative Frobenius error: {relative_error:.1e}", xlabel="Column j", ylabel="Row i")
    fig.colorbar(im, ax=axes[1, 1], shrink=0.8, label="log10 absolute error (floor: 1e-16)")
    save(fig, "cross-reconstruction.png")

    metrics = {
        "shape": [n, n], "sample_count": n*n, "real_fourier_components": 3,
        "complex_fourier_modes": 6, "cross_rank": rank,
        "selected_rows_zero_based": rows, "selected_columns_zero_based": columns,
        "retained_unique_elements": retained, "retained_fraction": retained/(n*n),
        "relative_frobenius_error": relative_error,
        "pivot_search": "full residual; all matrix entries evaluated",
        "errors_by_rank": {str(r): float(np.linalg.norm(a-b)/np.linalg.norm(a)) for r, _, _, b in steps},
    }
    (OUTPUT / "results.json").write_text(json.dumps(metrics, indent=2)+"\n")
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
