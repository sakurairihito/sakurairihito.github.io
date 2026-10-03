"""Chebyshev degree and separation rank for the BS price surface.

Run: python3 -B _assets/scripts/bs1d_chebyshev.py
Requires numpy/scipy/matplotlib and the adjacent bs1d_demo.py.
Fits on a full 129 x 129 Chebyshev-Lobatto grid and checks a distinct
192 x 190 uniform midpoint grid. Representation sizes are not evaluation costs.
"""
from pathlib import Path
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from numpy.polynomial.chebyshev import chebvander
from scipy.fft import dctn

from bs1d_demo import call_price, GREEN, ORANGE, INK

OUTPUT = Path(__file__).resolve().parents[1] / "compression"


def coefficients(values):
    """Standard T_p(x) T_q(y) coefficients of the Lobatto interpolant.

    Input axis coordinates descend as cos(pi*j/N). DCT-I is unnormalized;
    both endpoint coefficients on each axis receive half weight.
    """
    ns, nv = np.array(values.shape) - 1
    b = dctn(values, type=1, norm="backward", orthogonalize=False) / (ns * nv)
    b[[0, -1], :] *= .5
    b[:, [0, -1]] *= .5
    return b


def price_coefficients(degree):
    nodes = np.cos(np.pi * np.arange(degree + 1) / degree)
    values = call_price((100 + 50*nodes)[:, None], (.325 + .275*nodes)[None, :])
    return nodes, values, coefficients(values)


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    degree, ds, dv, rank = 128, 32, 24, 8
    nodes, values, b = price_coefficients(degree)
    # All validation coordinates are distinct from the construction coordinates.
    x = -1 + 2*(np.arange(192) + .5)/192
    y = -1 + 2*(np.arange(190) + .5)/190
    assert np.min(np.abs(x[:, None] - nodes)) > 1e-12
    assert np.min(np.abs(y[:, None] - nodes)) > 1e-12
    tx, ty = chebvander(x, degree), chebvander(y, degree)
    truth = call_price((100+50*x)[:, None], (.325+.275*y)[None, :])
    scale = np.linalg.norm(truth)

    def evaluate(c):
        return tx[:, :c.shape[0]] @ c @ ty[:, :c.shape[1]].T

    def errors(c):
        difference = evaluate(c) - truth
        return {"relative_frobenius": float(np.linalg.norm(difference)/scale),
                "maximum_absolute": float(np.max(np.abs(difference)))}

    # Normalization tests exercise constants, endpoints, and mixed modes.
    test_nodes = np.cos(np.pi*np.arange(9)/8)
    basis = chebvander(test_nodes, 8)
    known = np.zeros((9, 9))
    known[0, 0], known[2, 3], known[8, 8] = 2., -.7, .4
    assert np.allclose(coefficients(basis @ known @ basis.T), known, atol=1e-14)
    tnodes = chebvander(nodes, degree)
    assert np.max(np.abs(tnodes @ b @ tnodes.T - values)) < 1e-10
    assert errors(b)["maximum_absolute"] < 1e-10
    # Independently increase the construction resolution to guard against aliasing.
    _, _, b_finer = price_coefficients(192)
    assert np.max(np.abs(b-b_finer[:degree+1, :degree+1])) < 1e-11
    assert np.linalg.norm(b_finer[degree+1:, :]) < 1e-11
    assert np.linalg.norm(b_finer[:, degree+1:]) < 1e-11

    degrees = [2, 4, 8, 12, 16, 24, 32, 48, 64]
    degree_errors = [
        {"degree": d, "spot_only_truncated": errors(b[:d+1, :]),
         "volatility_only_truncated": errors(b[:, :d+1])} for d in degrees]
    block = b[:ds+1, :dv+1]
    u, s, vt = np.linalg.svd(block, full_matrices=False)
    left, right = u[:, :rank]*s[:rank], vt[:rank, :]
    joint = left @ right
    assert np.allclose((tx[:, :ds+1] @ left) @ (right @ ty[:, :dv+1].T),
                       evaluate(joint), atol=1e-11)
    assert np.count_nonzero(np.linalg.svd(joint, compute_uv=False) > s[0]*1e-12) == rank
    full_u, full_s, full_vt = np.linalg.svd(b, full_matrices=False)
    rank_errors = []
    for r in range(1, 17):
        rank_errors.append({"rank": r,
                           "full_degree": errors((full_u[:, :r]*full_s[:r]) @ full_vt[:r]),
                           "truncated_degree": errors((u[:, :r]*s[:r]) @ vt[:r])})
    bnorm = np.linalg.norm(b)
    spectrum_s, spectrum_v = np.linalg.norm(b, axis=1)/bnorm, np.linalg.norm(b, axis=0)/bnorm

    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11,
                         "text.color": INK, "axes.labelcolor": INK,
                         "axes.spines.top": False, "axes.spines.right": False})
    def save(fig, name):
        fig.savefig(OUTPUT / name, dpi=180, bbox_inches="tight", facecolor="white")
        plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.9), layout="constrained")
    modes = np.arange(65)
    axes[0].semilogy(modes, np.maximum(spectrum_s[:65], 1e-16), color=GREEN, label="Spot direction")
    axes[0].semilogy(modes, np.maximum(spectrum_v[:65], 1e-16), color=ORANGE, label="Volatility direction")
    axes[0].set(title="High-degree coefficients become small", xlabel="Chebyshev degree",
                ylabel="Coefficient-slice norm / total norm", ylim=(1e-16, 2), xlim=(0, 64))
    axes[0].legend(fontsize=9)
    axes[0].grid(alpha=.2)
    im = axes[1].imshow(np.log10(np.maximum(np.abs(b[:65, :65].T)/bnorm, 1e-16)),
                        origin="lower", extent=(-.5, 64.5, -.5, 64.5), cmap="magma", vmin=-16, vmax=0,
                        interpolation="nearest", aspect="auto")
    axes[1].plot([-.5, ds+.5, ds+.5], [dv+.5, dv+.5, -.5], "--", color="#50d5d0", linewidth=1.5,
                 label="Retain degrees 0–32 and 0–24")
    axes[1].set(title="Two-dimensional coefficient spectrum", xlabel="Spot degree p", ylabel="Volatility degree q")
    axes[1].legend(fontsize=8, loc="upper right", facecolor="white", framealpha=.95)
    fig.colorbar(im, ax=axes[1], label="log10 (|coefficient| / total norm)", shrink=.82)
    save(fig, "bs1d-chebyshev-spectrum.png")

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.8), layout="constrained")
    axes[0].semilogy(degrees, [d["spot_only_truncated"]["relative_frobenius"] for d in degree_errors],
                     "o-", color=GREEN, label="Limit spot degree; volatility degree = 128")
    axes[0].semilogy(degrees, [d["volatility_only_truncated"]["relative_frobenius"] for d in degree_errors],
                     "s-", color=ORANGE, label="Limit volatility degree; spot degree = 128")
    axes[0].set(title="Approximation degree", xlabel="Retained degree in one direction",
                ylabel="Relative error on validation grid")
    axes[0].legend(fontsize=8)
    ranks = np.arange(1, 17)
    axes[1].semilogy(ranks, [d["full_degree"]["relative_frobenius"] for d in rank_errors],
                     "o-", color=GREEN, label="Degrees 128 / 128")
    axes[1].semilogy(ranks, [d["truncated_degree"]["relative_frobenius"] for d in rank_errors],
                     "s--", color=ORANGE, label="Degrees 32 / 24")
    axes[1].axhline(errors(block)["relative_frobenius"], color="#8b9290", linestyle=":",
                    label="Degree truncation only (32 / 24)")
    axes[1].set(title="Separation rank", xlabel="Rank of coefficient matrix",
                ylabel="Relative error on validation grid", xticks=[1, 4, 8, 12, 16])
    axes[1].legend(fontsize=8)
    for ax in axes:
        ax.grid(alpha=.2)
    save(fig, "bs1d-chebyshev-convergence.png")

    metrics = {"model": "same Black-Scholes parameters as bs1d_demo.py",
               "coordinate_maps": {"S": "100 + 50*x", "sigma": "0.325 + 0.275*y"},
               "coefficient_convention": "standard unnormalized T_p(x) T_q(y)",
               "construction": {"degree_each_axis": degree, "grid": [129, 129],
                                "nodes": "cos(pi*j/128), j=0,...,128",
                                "resolution_check_degree": 192},
               "validation": {"grid": [192, 190], "nodes": "uniform midpoints in each [-1,1] axis",
                              "disjoint_from_construction": True,
                              "scope": "sampled errors; no uniform-domain or Greek guarantee"},
               "selected": {"spot_degree": ds, "volatility_degree": dv, "rank": rank,
                            "dense_coefficients": block.size, "factor_coefficients": left.size+right.size,
                            "reference_grid_values": 128**2,
                            "full_interpolant_error": errors(b), "degree_only_error": errors(block),
                            "degree_and_rank_error": errors(joint)},
               "spot_spectrum": spectrum_s.tolist(), "volatility_spectrum": spectrum_v.tolist(),
               "errors_by_degree": degree_errors, "errors_by_rank": rank_errors,
               "factor_convention": {"reconstruction": "B_approx = left @ right",
                                     "left_axes": ["spot_degree", "rank_component"],
                                     "right_axes": ["rank_component", "volatility_degree"],
                                     "singular_values": "absorbed into left"},
               "left_factor_coefficients": left.tolist(), "right_factor_coefficients": right.tolist(),
               "cost_note": "dense construction plus resolution/validation checks; counts are representation sizes"}
    (OUTPUT / "bs1d-chebyshev-results.json").write_text(json.dumps(metrics, indent=2)+"\n")
    print(json.dumps(metrics["selected"], indent=2))


if __name__ == "__main__":
    main()
