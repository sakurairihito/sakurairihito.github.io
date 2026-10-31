@def title = "Chebyshev interpolation for option pricing"
@def page_language = "en"
@def hasmath = true
@def description = "Reading note on Gaß et al. (2018): precompute option prices at Chebyshev nodes and interpolate across parameters."

@@explainer

[← Research notes](/research/)

# Chebyshev interpolation for option pricing

Reading note on [Gaß, Glau, Mahlstedt and Mair (2018)](https://link.springer.com/article/10.1007/s00780-018-0361-y). Calibration and risk need prices at many parameter values. The idea is to price once at Chebyshev nodes, interpolate over the parameters, and reuse the polynomial.

## Offline and online

1. Offline: pick a parameter box, compute prices at Chebyshev nodes (by Monte Carlo, Fourier or PDE, whatever you have), and build the interpolating polynomial.
2. Online: evaluate the polynomial at new parameters inside the box.

With the parameters rescaled to $p\in[-1,1]^D$,

$$
V(p)\approx\sum_{j_1=0}^{n_1}\cdots\sum_{j_D=0}^{n_D}
c_{j_1,\ldots,j_D}\prod_{i=1}^{D}T_{j_i}(p_i),
$$

where $T_j$ are Chebyshev polynomials and $D$ is the number of varying parameters.

## Why it works

The payoff can have kinks while the price is still analytic in the parameters. The paper gives sufficient conditions for this, and then the error decays exponentially in the degree. With $N$ nodes in total, the tensor construction gives an error of order $\rho^{-N^{1/D}}$ for some $\rho>1$. There are also convergence results for the sensitivities. [Sections 2–3](https://link.springer.com/article/10.1007/s00780-018-0361-y#Sec2).

Errors in the node prices carry through the interpolation. Raising the degree does not remove Monte Carlo noise, so node accuracy and interpolation accuracy have to be balanced. [Section 2.3](https://link.springer.com/article/10.1007/s00780-018-0361-y#Sec5).

## Experiments (Section 4)

Basket and path-dependent options under Black–Scholes, Heston and Merton, and an American put by finite differences. Some of these are outside what the analyticity results cover.

The timing study is a five-asset Heston lookback option with two varying model parameters and $7\times7=49$ nodes. For 10,000 parameter pairs at roughly the same accuracy:

| Method | Time |
| --- | --- |
| Monte Carlo at every pair | About 39 days, extrapolated from a single evaluation |
| Chebyshev interpolation, including offline construction | About 23 hours |
| Online evaluation alone | About 7 seconds |

Including construction, it breaks even at about 225 price evaluations in their setup. [Section 4.2](https://link.springer.com/article/10.1007/s00780-018-0361-y#Sec10).

## Notes to self

The full grid still needs $\prod_i(n_i+1)$ nodes. Five assets here does not mean five interpolated parameters. With more parameters you would want tensor compression or sparse grids, which the paper mentions in its outlook. Analyticity by itself does not give a small tensor rank.

Related notes: [compressing a price surface](/compression/) (degree vs rank), [a spread option with Chebfun3](/chebfun-spread/) (three-parameter Tucker), [interpolation across a kink](/chebyshev-spline/) (splitting at an exercise boundary), [option prices near expiry](/option-maturity/) (what happens as maturity goes to zero).

~~~
<details>
  <summary>Paper</summary>
  <p>Maximilian Gaß, Kathrin Glau, Mirco Mahlstedt and Maximilian Mair, <a href="https://doi.org/10.1007/s00780-018-0361-y">Chebyshev interpolation for parametric option pricing</a>, <em>Finance and Stochastics</em> 22, 701–731 (2018). Available under <a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a>.</p>
</details>
~~~

[Back to research notes](/research/)

@@
