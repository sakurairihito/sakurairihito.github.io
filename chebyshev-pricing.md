@def title = "Chebyshev interpolation for option pricing"
@def page_language = "en"
@def hasmath = true
@def description = "A short reading note on Gaß et al. (2018): precompute option prices, interpolate across parameters, and reuse the approximation for fast evaluation."

@@explainer

[← Research notes](/research/)

# Chebyshev interpolation for option pricing

@@article-lead
Precompute a price surface for fast repeated evaluation.
@@

Calibration and risk calculations require prices at many parameter settings. **Gaß, Glau, Mahlstedt and Mair (2018)** approximate the dependence of the price on those parameters with Chebyshev polynomials, so the expensive pricing calculation can be reused. [Original paper](https://link.springer.com/article/10.1007/s00780-018-0361-y).

## Offline and online

1. **Offline:** choose a parameter box, evaluate prices at Chebyshev nodes, and construct the interpolating polynomial. The node values can come from Monte Carlo, Fourier integration, or a PDE solver.
2. **Online:** evaluate this polynomial at new parameters inside the box.

After rescaling the parameters to $p\in[-1,1]^D$, the approximation is

$$
V(p)\approx\sum_{j_1=0}^{n_1}\cdots\sum_{j_D=0}^{n_D}
c_{j_1,\ldots,j_D}\prod_{i=1}^{D}T_{j_i}(p_i),
$$

where $T_j$ is a Chebyshev polynomial and $D$ counts the varying parameters.

## Why it works

A payoff may have kinks even when its expected value is analytic in the parameters. The paper gives sufficient conditions for this analyticity: interpolation errors then decrease exponentially with polynomial degree. In terms of the total number of nodes $N$, the tensor construction gives an error of order $\rho^{-N^{1/D}}$ for some $\rho>1$. It also establishes convergence results for price sensitivities. [Sections 2–3](https://link.springer.com/article/10.1007/s00780-018-0361-y#Sec2).

Errors in the precomputed prices also propagate through the interpolation. Increasing the degree alone cannot remove Monte Carlo noise; node accuracy and interpolation accuracy must be balanced. [Section 2.3](https://link.springer.com/article/10.1007/s00780-018-0361-y#Sec5).

## What Section 4 demonstrates

The experiments include basket and path-dependent options under Black–Scholes, Heston and Merton models, and an American put priced by finite differences. These extend beyond the scope of the analyticity results.

For a **five-asset Heston lookback option**, the efficiency study varies **two model parameters**, using $7\times7=49$ interpolation nodes. At roughly comparable accuracy, the reported cost for **10,000 parameter pairs** is:

| Method | Time |
| --- | --- |
| Monte Carlo at every pair | About 39 days, extrapolated from a single evaluation |
| Chebyshev interpolation, including offline construction | About 23 hours |
| Online evaluation alone | About 7 seconds |

Including construction, the methods break even at roughly 225 price evaluations in this implementation. These timings describe the paper's particular benchmark. [Section 4.2](https://link.springer.com/article/10.1007/s00780-018-0361-y#Sec14).

## Connection to compression

The full grid still needs $\prod_i(n_i+1)$ nodes: **five assets do not mean five interpolated parameters**. More varying parameters make tensor compression or sparse grids attractive, as discussed in the paper's outlook. Analyticity alone does not establish a small tensor rank.

The [price-surface compression example](/compression/) illustrates the complementary roles: low polynomial degree limits detail along each axis, while low rank compresses the coupling between axes.

Two reproduced numerical notes make the distinction concrete: [a spread option with Chebfun3](/chebfun-spread/) builds a three-parameter Tucker approximation, while [interpolation across a kink](/chebyshev-spline/) compares one polynomial with two pieces joined at a known exercise boundary.

[Option prices near expiry](/option-maturity/) shows how a smooth Black–Scholes price approaches a kinked payoff, and why a domain extending to zero remaining maturity needs separate treatment.

~~~
<details>
  <summary>Paper</summary>
  <p>Maximilian Gaß, Kathrin Glau, Mirco Mahlstedt and Maximilian Mair, <a href="https://doi.org/10.1007/s00780-018-0361-y">Chebyshev interpolation for parametric option pricing</a>, <em>Finance and Stochastics</em> 22, 701–731 (2018).</p>
  <p>The article is available under <a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a>. This note summarizes its ideas and reported experiments.</p>
</details>
~~~

[Back to research notes](/research/)

@@
