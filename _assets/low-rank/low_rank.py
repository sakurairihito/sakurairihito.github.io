"""Low-rank examples: singular values of 2D grid functions and QTT ranks of sin.

Usage: python3 -B _assets/low-rank/low_rank.py <new_output_dir>
"""
import csv
import json
import pathlib
import sys

import numpy as np
from numpy.polynomial import chebyshev
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker

N_2D = 129            # Chebyshev-Lobatto points per axis for the 2D examples
L_QTT = 12            # 2^12 = 4096 grid points for the QTT examples
TOL = 1e-10           # relative singular-value tolerance for the numerical rank
OMEGAS = [1, 2, 5, 10, 20, 50, 100]
SEED = 0


def lobatto(n):
    return np.cos(np.pi * np.arange(n) / (n - 1))


def qtt_ranks(v, L, tol):
    """Ranks of successive SVDs, one cut between each pair of binary digits."""
    rem = v.reshape(2, -1, order="F")
    ranks = []
    for _ in range(L - 1):
        _, s, vt = np.linalg.svd(rem, full_matrices=False)
        r = int(np.sum(s > tol * s[0]))
        ranks.append(r)
        rem = (s[:r, None] * vt[:r]).reshape(2 * r, -1, order="F")
    return ranks


def main(outdir):
    out = pathlib.Path(outdir)
    if out.exists():
        sys.exit(f"{out} exists; choose a new output directory")
    out.mkdir(parents=True)

    x = lobatto(N_2D)
    X, Y = np.meshgrid(x, x, indexing="ij")
    rng = np.random.default_rng(SEED)
    cases = [
        ("exp(x+y)", np.exp(X + Y)),
        ("sin(x+y)", np.sin(X + Y)),
        ("sin(xy)", np.sin(X * Y)),
        ("sin(10xy)", np.sin(10 * X * Y)),
        ("noise", rng.standard_normal((N_2D, N_2D))),
    ]
    sv = {}
    for name, F in cases:
        s = np.linalg.svd(F, compute_uv=False)
        sv[name] = s / s[0]
    with open(out / "singular_values_2d.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["k"] + [n for n, _ in cases])
        for k in range(N_2D):
            w.writerow([k + 1] + [f"{sv[n][k]:.6e}" for n, _ in cases])
    ranks_2d = {n: int(np.sum(sv[n] > TOL)) for n, _ in cases}

    n = 2 ** L_QTT
    i = np.arange(n)
    grids = {"uniform": -1 + 2 * i / (n - 1), "chebyshev": np.cos(np.pi * i / (n - 1))}
    qtt = {g: [max(qtt_ranks(np.sin(w * xg), L_QTT, TOL)) for w in OMEGAS] for g, xg in grids.items()}
    degree = []
    for w in OMEGAS:
        c = chebyshev.chebinterpolate(lambda t: np.sin(w * t), 300)
        degree.append(int(np.nonzero(np.abs(c) > TOL)[0].max()))
    with open(out / "qtt_rank_sin.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["omega", "chebyshev_degree", "uniform_max_rank", "chebyshev_max_rank"])
        for j, om in enumerate(OMEGAS):
            w.writerow([om, degree[j], qtt["uniform"][j], qtt["chebyshev"][j]])

    (out / "summary.json").write_text(json.dumps({
        "n_2d": N_2D, "qtt_bits": L_QTT, "tol": TOL, "seed": SEED,
        "rank_2d": ranks_2d, "qtt_max_rank": qtt, "chebyshev_degree": degree, "omegas": OMEGAS,
        "numpy": np.__version__, "matplotlib": matplotlib.__version__,
    }, indent=2) + "\n")

    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11,
                         "axes.spines.top": False, "axes.spines.right": False,
                         "axes.edgecolor": "#8a8a85", "axes.labelcolor": "#333330",
                         "xtick.color": "#555550", "ytick.color": "#555550"})
    shown = [("sin(x+y)", "#2a78d6"), ("sin(xy)", "#eb6834"), ("noise", "#8a8a85")]
    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    k = np.arange(1, 41)
    for name, c in shown:
        ax.semilogy(k, np.maximum(sv[name][:40], 1e-17), "-o", color=c, lw=2, ms=4,
                    label=f"{name}  (rank {ranks_2d[name]})")
    ax.axhline(TOL, color="#b5b5ae", lw=1, ls="--")
    ax.text(40, TOL / 3, "tolerance $10^{-10}$", ha="right", va="top", fontsize=9, color="#555550")
    ax.set_ylim(1e-17, 3)
    ax.set_xlabel("index $k$")
    ax.set_ylabel(r"singular value $s_k/s_1$")
    ax.set_title("129×129 Chebyshev grid", loc="left", fontsize=12)
    ax.legend(frameon=False, fontsize=9, loc="center right", bbox_to_anchor=(1, 0.66))
    ax.grid(axis="y", color="#e6e6e1", lw=0.8)
    fig.savefig(out / "low-rank.png", dpi=200, bbox_inches="tight")
    print(json.dumps({"rank_2d": ranks_2d, "qtt_max_rank": qtt, "chebyshev_degree": degree}))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
