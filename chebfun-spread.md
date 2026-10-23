@def title = "A spread option with Chebfun3"
@def page_language = "en"
@def hasmath = true
@def description = "Reproducing Chebfun's 2017 spread-option example: a three-parameter Tucker approximation, fast evaluation, and an independent check of quadrature error."

@@explainer

[← Research notes](/research/)

# A spread option with Chebfun3

@@article-lead
Two assets. Three parameters. A compact price approximation.
@@

[Glau, Hashemi, Mahlstedt and Poetz (2017)](https://www.chebfun.org/examples/applics/BlackScholes2D.html) use Chebfun3 to approximate a spread-option price as maturity $T$, strike $K$, and correlation $\rho$ vary. The reproduction below recovers the article's reported ranks and interpolation error, then checks the underlying numerical integral independently.

~~~
<figure>
  <a href="/assets/chebfun-spread/analysis/spread-slices.png">
    <img src="/assets/chebfun-spread/analysis/spread-slices.png" alt="Three slices of the reproduced spread-option price over maturity, strike, and correlation, at T=2, K=0.3, and rho=-0.9." width="2340" height="737" fetchpriority="high">
  </a>
  <figcaption>Slices of the reproduced classic Chebfun3 approximation. Both initial asset prices are 1, both volatilities are 0.3, and the risk-free rate is zero.</figcaption>
</figure>
~~~

## From an expectation to a function of parameters

The model and payoff are

$$
\frac{dS_i}{S_i}=r\,dt+\sigma_i\,dW_i,\qquad
dW_1\,dW_2=\rho\,dt,
$$

$$
V(T,K,\rho)=e^{-rT}\mathbb{E}\!\left[(S_1(T)-S_2(T)-K)_+\right].
$$

The log return $X_i=\log(S_i(T)/S_i(0))$ has mean $(r-\sigma_i^2/2)T$. The article's opening SDE appears to place this log-price drift in the equation for $dS_i/S_i$; its integration code uses the appropriate log-return distribution.

Each price evaluation uses **150 × 150 Clenshaw–Curtis nodes** on $[-10,10]^2$ in log-return coordinates. Chebfun3 then approximates the resulting function on

$$
[0.3,2]\times[0.3,2]\times[-0.9,0.9]
$$

in $(T,K,\rho)$. The two integration dimensions and the three interpolation dimensions have different meanings.

## A Tucker representation

Chebfun3 represents the function as

$$
\widetilde V(T,K,\rho)=
\sum_{i=1}^{r_T}\sum_{j=1}^{r_K}\sum_{\ell=1}^{r_\rho}
G_{ij\ell}\,a_i(T)b_j(K)c_\ell(\rho).
$$

The core couples three families of one-dimensional functions. Their Chebyshev lengths control resolution within each parameter; the core dimensions describe the Tucker ranks. See the [Chebfun3 guide](https://www.chebfun.org/docs/guide/guide18.html).

The guide identifies `classic` as the original construction algorithm. Using it with `eps = 1e-5` reproduces the 2017 example:

| Quantity | Article | Local reproduction |
| --- | --- | --- |
| Tucker ranks | 5, 10, 7 | 5, 10, 7 |
| Chebyshev lengths | 10, 42, 13 | 10, 42, 13 |
| Maximum error against the 150-point price routine | $2.5650\times10^{-4}$ | $2.56498685\times10^{-4}$ |

The lengths correspond to maximum degrees 9, 41, and 12. Errors are measured at the same $15^3=3375$ uniformly spaced parameter combinations.

In this Octave run, construction took **78.95 seconds**, direct evaluation at the test grid took **3.72 seconds**, and evaluation of the approximation took **0.00592 seconds** (median of five warmed evaluations). Construction called the scalar price routine 62,667 times, including repeated calls; this is not a count of unique parameter points. These timings depend on the machine, runtime, and measurement procedure.

## Interpolation error and pricing error

An accurate approximation to a numerical integral can still inherit the integral's error. We independently condition on the second asset, evaluate the conditional call expectation analytically, and integrate only one standard normal variable.

~~~
<figure>
  <a href="/assets/chebfun-spread/analysis/spread-errors.png">
    <img src="/assets/chebfun-spread/analysis/spread-errors.png" alt="The 150-point quadrature error is larger than the interpolation error. A separate refinement check at 27 parameter points reduces quadrature error as the nodes per axis increase from 150 to 1200." width="1980" height="774" loading="lazy">
  </a>
  <figcaption>Left: the article's 3,375-point test grid. Right: a separate 27-point quadrature study; its maximum is over a different set of points.</figcaption>
</figure>
~~~

| Comparison on the 3,375-point grid | Maximum absolute error |
| --- | ---: |
| Classic Chebfun3 vs. 150-point quadrature | $2.5650\times10^{-4}$ |
| 150-point quadrature vs. conditional reference | $5.5339\times10^{-3}$ |
| Classic Chebfun3 vs. conditional reference | $5.5689\times10^{-3}$ |

The largest quadrature discrepancy occurs at $(T,K,\rho)=(0.3,0.42142857,-0.9)$: the original quadrature gives **0.01986727**, while the conditional reference gives **0.01433340**. Tightening the approximation alone does not resolve this discrepancy. Increasing quadrature resolution improves the separate 27-point check.

An additional 500 random parameter points give a maximum interpolation error of $2.281\times10^{-4}$ and a maximum total discrepancy of $1.015\times10^{-3}$ for the classic construction. All these checks are sampled comparisons, not error bounds over the parameter box.

## Reproduce the calculation

Download the [complete bundle](/assets/chebfun-spread/reproduction.zip), containing code, numerical outputs, figures, and checks. It uses Chebfun revision [`7574c77680d7e82b79626300bf255498271a72df`](https://github.com/chebfun/chebfun/tree/7574c77680d7e82b79626300bf255498271a72df).

```matlab
run_chebfun_spread('/path/to/chebfun', 'new_results')
```

```bash
python3 -B test_reference.py
python3 -B analyse_spread.py new_results new_analysis
```

The saved run used GNU Octave 11.3.0. A small, tested adapter supplies the two-input page-matrix multiplication used by this Chebfun revision; the library itself was not edited. This verifies the exercised example, not general Octave compatibility or a MATLAB timing result.

~~~
<details>
  <summary>Independent reference and validation details</summary>
  <p>For a standard normal value z of the second asset, let m = −σ₁²T/2 + ρσ₁√T z, v = σ₁²T(1−ρ²), and L = exp(−σ₂²T/2 + σ₂√T z) + K. The conditional payoff expectation is exp(m + v/2) Φ((m + v − log L)/√v) − L Φ((m − log L)/√v). Integrating this expression against the standard normal density gives the reference for the zero-rate, unit-spot setting used here.</p>
  <p>The one-dimensional integration uses SciPy quad_vec on [−12,12] with absolute and relative tolerance 10⁻¹². A separate [−10,10] calculation with tolerance 10⁻¹¹ changes the grid prices by at most 1.39 × 10⁻¹⁶. These are numerical consistency checks, not certified tail or roundoff bounds. At zero strike, the reference also agrees with the exchange-option formula at nine maturity/correlation combinations.</p>
  <p>We independently reproduce the Clenshaw–Curtis nodes, weights, and selected prices in Python. Exported Tucker factors reproduce all saved Chebfun grid and random evaluations within 3.4 × 10⁻¹⁶. The export includes the endpoint values that Chebfun stores separately from its polynomial coefficients.</p>
  <p>The current default constructor at the pinned revision is also recorded: ranks (5,10,7), lengths (10,29,12), and maximum grid discrepancy 6.0012 × 10⁻⁴ against the same quadrature. The constructor's tolerance is not an absolute price-error guarantee.</p>
  <p>Download <a href="/assets/chebfun-spread/run_chebfun_spread.m">the MATLAB/Octave driver</a>, <a href="/assets/chebfun-spread/analyse_spread.py">the independent analysis</a>, <a href="/assets/chebfun-spread/analysis/summary.json">the full numerical summary</a>, <a href="/assets/chebfun-spread/analysis/grid_comparison.csv">grid prices</a>, <a href="/assets/chebfun-spread/analysis/random_comparison.csv">random-point prices</a>, or <a href="/assets/chebfun-spread/provenance.json">source hashes</a>.</p>
</details>
~~~

Related: [Gaß et al. (2018), parametric option pricing](/chebyshev-pricing/) · [Low rank and low polynomial degree](/compression/) · [Piecewise approximation at a kink](/chebyshev-spline/).

[Back to research notes](/research/)

@@
