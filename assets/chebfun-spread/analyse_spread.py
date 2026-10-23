"""Check saved Chebfun prices against conditional 1D integration; draw figures.

Usage: python3 -B analyse_spread.py RESULTS NEW_ANALYSIS_DIRECTORY
Requires numpy, scipy, matplotlib. No MATLAB/Octave needed for this stage.
"""
from pathlib import Path
import argparse
import hashlib
import io
import json
import platform
import sys

import numpy as np
import scipy
from numpy.polynomial.chebyshev import chebvander
from scipy.integrate import quad_vec
from scipy.io import loadmat
from scipy.special import ndtr


def read_octave_csv(path):
    # Octave can export real-valued FFT results with a literal "+0i".
    data = np.loadtxt(io.StringIO(path.read_text().replace("i", "j")),
                      delimiter=",", dtype=complex)
    if np.max(np.abs(data.imag)) > 1e-14:
        raise ValueError(f"Unexpected imaginary component in {path.name}")
    return data.real


def reference_prices(points, limit=12., tolerance=1e-12):
    """Condition on asset 2; integrate an analytic conditional call price.

    Both initial spots are 1, both volatilities .3, and the risk-free rate 0.
    Returns prices and QUADPACK-style numerical error estimate (not a bound).
    """
    t, strike, rho = np.asarray(points).T
    variance = .09*t
    mu = -.5*variance
    sd = np.sqrt(variance)
    conditional_sd = sd*np.sqrt(1-rho*rho)

    def integrand(z):
        threshold = np.exp(mu+sd*z)+strike
        mean = mu+rho*sd*z
        d2 = (mean-np.log(threshold))/conditional_sd
        call = np.exp(mean+.5*conditional_sd**2)*ndtr(d2+conditional_sd)-threshold*ndtr(d2)
        return call*np.exp(-.5*z*z)/np.sqrt(2*np.pi)

    return quad_vec(integrand, -limit, limit, epsabs=tolerance, epsrel=tolerance,
                    norm="max", quadrature="gk21")


def clenshaw_curtis(n, halfwidth=10.):
    """Independent cosine-series quadrature weights on [-halfwidth,halfwidth]."""
    degree = n-1
    theta = np.pi*np.arange(n)/degree
    w = np.zeros(n)
    v = np.ones(n-2)
    interior = theta[1:-1]
    if degree % 2 == 0:
        w[[0, -1]] = 1/(degree**2-1)
        for k in range(1, degree//2):
            v -= 2*np.cos(2*k*interior)/(4*k*k-1)
        v -= np.cos(degree*interior)/(degree**2-1)
    else:
        w[[0, -1]] = 1/degree**2
        for k in range(1, (degree+1)//2):
            v -= 2*np.cos(2*k*interior)/(4*k*k-1)
    w[1:-1] = 2*v/degree
    return halfwidth*np.cos(theta), halfwidth*w


def direct_prices(points, n):
    nodes, w = clenshaw_curtis(n)
    x, y = nodes[:, None], nodes[None, :]
    exponential_difference = np.exp(x)-np.exp(y)
    weights = w[:, None]*w[None, :]
    result = []
    for t, strike, rho in points:
        variance = .09*t
        u, v = x+.5*variance, y+.5*variance
        density = np.exp(-(u*u-2*rho*u*v+v*v)/(2*variance*(1-rho*rho)))
        density /= 2*np.pi*variance*np.sqrt(1-rho*rho)
        result.append(np.sum(weights*density*np.maximum(exponential_difference-strike, 0)))
    return np.array(result)


def evaluate_saved_coefficients(path, points):
    """Independently contract exported Chebyshev factors and Tucker core."""
    data = loadmat(path)
    factors = []
    for axis, (key, lo, hi) in enumerate([
        ("t_coeffs", .3, 2.), ("k_coeffs", .3, 2.), ("rho_coeffs", -.9, .9)
    ]):
        c = data[key]
        x = (2*points[:, axis]-lo-hi)/(hi-lo)
        values = chebvander(x, len(c)-1)@c
        endpoints = data[key.replace("_coeffs", "_endpoints")]
        for side, coordinate in enumerate([lo, hi]):
            values[points[:, axis] == coordinate] = endpoints[side]
        factors.append(values)
    return np.einsum("ijk,ni,nj,nk->n", data["core"], *factors, optimize=True)


def errors(actual, expected):
    diff = actual-expected
    i = int(np.argmax(np.abs(diff)))
    return {"max_absolute": float(np.max(np.abs(diff))),
            "rmse": float(np.sqrt(np.mean(diff**2))), "worst_index": i}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("results", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    report = {"chebfun": json.loads((args.results/"chebfun_results.json").read_text()),
              "environment": {"python": sys.version, "numpy": np.__version__,
                              "scipy": scipy.__version__, "platform": platform.platform()},
              "chebfun_commit": "7574c77680d7e82b79626300bf255498271a72df"}
    datasets = {}
    for name in ["grid", "random"]:
        table = read_octave_csv(args.results/f"{name}_direct.csv")
        points, direct = table[:, :3], table[:, 3]
        reference, estimate = reference_prices(points)
        check, check_estimate = reference_prices(points, limit=10., tolerance=1e-11)
        report[name] = {"points": len(points), "reference_error_estimate": float(estimate),
                        "reference_check_error_estimate": float(check_estimate),
                        "reference_limit10_vs12_max": float(np.max(np.abs(check-reference))),
                        "quadrature_vs_reference": errors(direct, reference)}
        columns = [points, direct[:, None], reference[:, None]]
        datasets[name] = (points, direct, reference)
        for mode in ["classic", "default"]:
            saved = read_octave_csv(args.results/f"{mode}_{name}.csv")
            np.testing.assert_array_equal(saved[:, :3], points)
            approx = saved[:, 3]
            rebuilt = evaluate_saved_coefficients(args.results/f"{mode}_coefficients.mat", points)
            np.testing.assert_allclose(approx, rebuilt, rtol=0, atol=2e-13)
            report[name][mode] = {"vs_quadrature": errors(approx, direct),
                                  "vs_reference": errors(approx, reference),
                                  "coefficient_reconstruction_max": float(np.max(np.abs(approx-rebuilt)))}
            columns.append(approx[:, None])
        np.savetxt(args.output/f"{name}_comparison.csv", np.column_stack(columns), delimiter=",",
                   header="T,K,rho,quadrature150,conditional_reference,classic,default", comments="")
        worst = report[name]["quadrature_vs_reference"]["worst_index"]
        report[name]["quadrature_worst_point"] = points[worst].tolist()
        report[name]["quadrature_worst_values"] = [float(direct[worst]), float(reference[worst])]

    nodes, weights = clenshaw_curtis(150)
    exported = read_octave_csv(args.results/"quadrature.csv")
    order = np.argsort(exported[:, 0])
    np.testing.assert_allclose(nodes[::-1], exported[order, 0], rtol=0, atol=2e-14)
    np.testing.assert_allclose(weights[::-1], exported[order, 1], rtol=0, atol=2e-14)
    for power in [0, 2, 4, 8]:
        np.testing.assert_allclose(weights@nodes**power, 2*10.**(power+1)/(power+1), rtol=1e-13)
    points = np.array(np.meshgrid([.3,1.15,2.], [.3,1.15,2.], [-.9,0.,.9],
                                 indexing="ij")).reshape(3,-1).T
    reference, _ = reference_prices(points)
    report["quadrature_refinement"] = []
    for n in [150, 300, 600, 1200]:
        prices = direct_prices(points, n)
        report["quadrature_refinement"].append({"nodes_per_axis": n, **errors(prices, reference)})
        np.savetxt(args.output/f"quadrature{n}_27points.csv",
                   np.column_stack([points, prices, reference]), delimiter=",",
                   header="T,K,rho,quadrature,reference", comments="")
    grid_points, grid_direct, _ = datasets["grid"]
    # The selected 27 points are on the article's 15^3 grid.
    indices = [np.argmin(np.max(np.abs(grid_points-p), axis=1)) for p in points]
    np.testing.assert_allclose(direct_prices(points, 150), grid_direct[indices], rtol=0, atol=3e-14)
    report["input_sha256"] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                              for p in sorted(args.results.iterdir()) if p.is_file()}
    (args.output/"summary.json").write_text(json.dumps(report, indent=2)+"\n")
    draw(args.results, args.output, report, datasets)
    print(json.dumps({k: report[k] for k in ["grid", "random", "quadrature_refinement"]}, indent=2))


def draw(results, output, report, datasets):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.ticker import NullFormatter
    plt.rcParams.update({"font.size": 11, "font.family": "DejaVu Sans",
                         "axes.spines.top": False, "axes.spines.right": False})
    table = np.loadtxt(output/"grid_comparison.csv", delimiter=",", skiprows=1)
    classic = table[:,5].reshape((15,15,15), order="F")
    t, k, rho = np.linspace(.3,2,15), np.linspace(.3,2,15), np.linspace(-.9,.9,15)
    slices = [(k,rho,classic[-1,:,:].T, "Strike K", r"Correlation $\rho$", "Maturity T = 2"),
              (t,rho,classic[:,0,:].T, "Maturity T", r"Correlation $\rho$", "Strike K = 0.3"),
              (t,k,classic[:,:,0].T, "Maturity T", "Strike K", r"Correlation $\rho$ = -0.9")]
    fig, axes = plt.subplots(1,3,figsize=(13,4.1), layout="constrained")
    for ax, (x,y,z,xlabel,ylabel,title) in zip(axes,slices):
        im = ax.pcolormesh(x,y,z, shading="auto", cmap="viridis", vmin=0, vmax=float(classic.max()))
        ax.set(xlabel=xlabel, ylabel=ylabel, title=title)
    fig.colorbar(im, ax=axes, label="Spread option price", shrink=.85)
    fig.savefig(output/"spread-slices.png", dpi=180, facecolor="white")
    plt.close(fig)
    fig, axes = plt.subplots(1,2,figsize=(11,4.3), layout="constrained")
    stats = report["grid"]
    labels = ["Classic vs\n150-point quadrature", "150-point quadrature\nvs conditional reference",
              "Classic vs\nconditional reference"]
    vals = [stats["classic"]["vs_quadrature"]["max_absolute"],
            stats["quadrature_vs_reference"]["max_absolute"], stats["classic"]["vs_reference"]["max_absolute"]]
    axes[0].bar(range(3), vals, color=["#197868","#c48240","#516b93"])
    axes[0].set(xticks=range(3), xticklabels=labels, ylabel="Maximum absolute error",
                yscale="log", title=r"Error on the article's $15^3$ test grid")
    axes[0].tick_params(axis="x", labelsize=8)
    for i, v in enumerate(vals):
        axes[0].text(i, v*1.15, f"{v:.2e}", ha="center", fontsize=9)
    axes[0].set_ylim(min(vals)/2, max(vals)*2)
    convergence = report["quadrature_refinement"]
    axes[1].loglog([d["nodes_per_axis"] for d in convergence],
                   [d["max_absolute"] for d in convergence], "o-", color="#197868")
    axes[1].set(xlabel="Quadrature nodes per log-return axis", ylabel="Maximum absolute error",
                title="Quadrature refinement at 27 fixed points")
    axes[1].set_xticks([150,300,600,1200], labels=["150","300","600","1200"])
    axes[1].xaxis.set_minor_formatter(NullFormatter())
    axes[1].grid(alpha=.2, which="both")
    fig.savefig(output/"spread-errors.png", dpi=180, facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    main()
