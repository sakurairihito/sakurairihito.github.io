"""Run the supplied demo unchanged, export tables, check it, and draw two figures.

Usage: python3 -B reproduce_cheb_spline.py NEW_OUTPUT_DIRECTORY
Keep cheb_spline_demo.py beside this file. Requires numpy, scipy, matplotlib.
"""
from pathlib import Path
import argparse
import hashlib
import json
import platform
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import scipy
from scipy.interpolate import BarycentricInterpolator

import cheb_spline_demo as demo


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    counts, single_abs, split_abs = demo.ex1()
    boundary, rows = demo.ex2()
    root_residual = abs(demo.K-boundary-demo.bs_put(boundary))
    assert root_residual < 1e-11
    assert np.max(split_abs) < 1e-12
    # Independent barycentric evaluation checks the fitted polynomial away
    # from its nodes. Standard Lobatto weights avoid any random initialization.
    test_spots = np.linspace(50.,150.,1003)
    degree = 32
    nodes = demo.lobatto_nodes(50.,150.,degree)
    weights = (-1.)**np.arange(degree+1)
    weights[[0,-1]] *= .5
    independent = BarycentricInterpolator(nodes, demo.V(nodes), wi=weights)
    poly = demo.cheb_interp(demo.V,50.,150.,degree)
    barycentric_difference = float(np.max(np.abs(independent(test_spots)-poly(test_spots))))
    assert barycentric_difference < 1e-10
    spline = demo.ChebSpline(demo.V, [50.,boundary,150.], degree//2)
    node_residual = 0.
    for piece, lo, hi in zip(spline.pieces, [50.,boundary], [boundary,150.]):
        local_nodes = demo.lobatto_nodes(lo,hi,degree//2)
        node_residual = max(node_residual, float(np.max(np.abs(piece(local_nodes)-demo.V(local_nodes)))))
    assert node_residual < 1e-10
    join_gap = float(abs(spline.pieces[0](boundary)-spline.pieces[1](boundary)))
    assert join_gap < 1e-10

    np.savetxt(args.output/"absolute_value.csv",
               np.column_stack([counts,single_abs,split_abs]), delimiter=",",
               header="unique_nodes,single_value_max_error,piecewise_value_max_error", comments="")
    np.savetxt(args.output/"exercise_value.csv", rows, delimiter=",",
               header="unique_nodes,single_price_max_error,piecewise_price_max_error,single_delta_max_error,piecewise_delta_max_error",
               comments="")
    # This second, denser grid checks how much the sampled maximum depends
    # on the display resolution. The kink itself has no Delta.
    refined = np.linspace(50.,150.,16001)
    mask = np.abs(refined-boundary)>1e-6
    refined_errors = {
        "single_price": float(np.max(np.abs(poly(refined)-demo.V(refined)))),
        "piecewise_price": float(np.max(np.abs(spline(refined)-demo.V(refined)))),
        "single_delta": float(np.max(np.abs(poly.deriv()(refined[mask])-demo.V_delta(refined[mask])))),
        "piecewise_delta": float(np.max(np.abs(spline(refined[mask],deriv=1)-demo.V_delta(refined[mask]))))}
    summary = {
        "source_sha256": hashlib.sha256(Path(demo.__file__).read_bytes()).hexdigest(),
        "environment": {"python": sys.version, "numpy": np.__version__, "scipy": scipy.__version__,
                        "matplotlib": matplotlib.__version__, "platform": platform.platform()},
        "parameters": {"K": demo.K,"r":demo.r,"sigma":demo.sig,"T":demo.T,"spot_domain":[50,150]},
        "exercise_boundary": float(boundary), "boundary_residual": float(root_residual),
        "left_delta_at_boundary": -1., "right_delta_at_boundary": float(demo.bs_put_delta(boundary)),
        "validation_points": 4001, "delta_exclusion_radius": 1e-6,
        "counts": {"single_unique_nodes":"N+1", "piecewise_unique_nodes":"N+1",
                   "single_sample_evaluations":"N+1", "piecewise_sample_evaluations":"N+2",
                   "boundary_search_cost_included":False},
        "checks": {"barycentric_vs_fitted_degree32": barycentric_difference,
                   "piecewise_node_residual_degree16": node_residual,
                   "piecewise_join_gap_degree16": join_gap},
        "degree32_refined_grid_16001": refined_errors,
        "selected_rows": [dict(zip(["unique_nodes","single_price","piecewise_price","single_delta","piecewise_delta"],row))
                          for row in rows if int(row[0]) in [9,17,33,65,129]]}
    (args.output/"summary.json").write_text(json.dumps(summary,indent=2)+"\n")
    plt.rcParams.update({"font.size":11,"font.family":"DejaVu Sans",
                         "axes.spines.top":False,"axes.spines.right":False})
    green, orange = "#197868", "#c48240"
    fig, axes = plt.subplots(1,3,figsize=(13,4.3),layout="constrained")
    for ax,x,y1,y2,title in [
        (axes[0],counts,single_abs,split_abs,r"$|x-0.3|$: value"),
        (axes[1],rows[:,0],rows[:,1],rows[:,2],"Exercise decision: value"),
        (axes[2],rows[:,0],rows[:,3],rows[:,4],"Exercise decision: Delta")]:
        ax.semilogy(x,y1,"o-",ms=3,color=orange,label="One polynomial")
        ax.semilogy(x,y2,"s-",ms=3,color=green,label="Split at the kink")
        ax.set(xlabel="Distinct interpolation nodes",ylabel="Sampled maximum absolute error",title=title)
        ax.grid(alpha=.2,which="both")
    axes[0].legend(fontsize=9)
    fig.savefig(args.output/"spline-convergence.png",dpi=180,facecolor="white")
    plt.close(fig)

    fig,axes=plt.subplots(1,2,figsize=(11,4.3),layout="constrained")
    x=np.linspace(boundary-12,boundary+12,1201)
    axes[0].plot(x,demo.V(x),color="#283c3b",lw=2,label="Exact decision value")
    axes[0].plot(x,poly(x),"--",color=orange,label="One polynomial, degree 32")
    axes[0].plot(x,spline(x),":",color=green,lw=2,label="Two pieces, degree 16 each")
    # Draw the analytic one-sided limits separately; no value is assigned at
    # the point where the mathematical derivative is undefined.
    for m in [x<boundary,x>boundary]:
        axes[1].plot(x[m],demo.V_delta(x[m]),color="#283c3b",lw=2)
        axes[1].plot(x[m],spline(x[m],deriv=1),":",color=green,lw=2)
    axes[1].plot(x,poly.deriv()(x),"--",color=orange)
    axes[0].set(ylabel="Value",title="The exercise boundary introduces a kink")
    axes[1].set(ylabel="Delta",title="A single polynomial smooths the jump")
    for ax in axes:
        ax.axvline(boundary,color="#8b9290",ls=":",lw=1)
        ax.set_xlabel("Spot S")
        ax.grid(alpha=.2)
    axes[0].legend(fontsize=8)
    fig.savefig(args.output/"spline-boundary.png",dpi=180,facecolor="white")
    plt.close(fig)
    print(json.dumps(summary,indent=2))


if __name__ == "__main__":
    main()
