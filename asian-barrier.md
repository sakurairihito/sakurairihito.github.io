@def title = "Asian barrier option: a price surface"
@def hasmath = true
@def description = "A saved tensor-train price surface, Gamma, and Chebyshev coefficient spectra."

@@explainer

[← Research notes](/research/)

# Asian barrier option: a price surface

@@article-lead
A smooth price surface, a more delicate Gamma.
@@

A saved tensor train over moneyness $m=S_0/K$ and volatility $\sigma$. **ME** retains degrees **26 and 7**, with **rank 3**.

~~~
<figure>
  <a href="/assets/asian-barrier/asian_price_surface.png">
    <img src="/assets/asian-barrier/asian_price_surface.png" alt="Three-dimensional Asian barrier option price surface over moneyness and volatility, evaluated from the degree-truncated tensor train." width="2106" height="1494" decoding="async">
  </a>
  <figcaption>The degree-truncated price surface.</figcaption>
</figure>
~~~

## Price and Gamma

Truncation changes plotted prices by at most **0.00111** and makes Gamma look smoother. **Accuracy still needs a matched reference.**

~~~
<figure>
  <a href="/assets/asian-barrier/asian_price_gamma_comparison.png">
    <img src="/assets/asian-barrier/asian_price_gamma_comparison.png" alt="Raw and degree-truncated tensor-train predictions: similar price surfaces above, and a visibly smoother Gamma surface after truncation below. Each row uses the same vertical scale." width="2080" height="1680" loading="lazy" decoding="async">
  </a>
  <figcaption>Price above; Gamma below. Each row uses a shared vertical scale.</figcaption>
</figure>
~~~

## Which degrees remain?

Chebyshev amplitudes decay to a small tail. Cutoffs: **26 in moneyness**, **7 in volatility**.

~~~
<figure>
  <a href="/assets/asian-barrier/asian_tt_spectra.png">
    <img src="/assets/asian-barrier/asian_tt_spectra.png" alt="Marginal Chebyshev coefficient spectra for moneyness and volatility, comparing the raw tensor train with truncation at degrees 26 and 7." width="1872" height="1040" loading="lazy" decoding="async">
  </a>
  <figcaption>Saved-TT spectra. Measuring TCI’s effect on noise requires same-sample full-grid Monte Carlo.</figcaption>
</figure>
~~~

## Why so few coefficients?

**365 path steps and a barrier, yet a compact surface.** Averaging can smooth prices and reduce high-degree coefficients. Low rank reflects simple coupling between variables; smoothness alone does not guarantee it.

~~~
<details>
  <summary>Settings &amp; sources</summary>
  <p>Risk-neutral model: μ = r = 0.05, strike K = 110, barrier B = 100, maturity T = 1. There are 365 monitoring steps and 10<sup>6</sup> antithetic pairs, with seed 1.</p>
  <p>Plotted interior domain: m ∈ [0.93, 1.17], σ ∈ [0.16, 0.24]. These are saved TT evaluations; no new sampling or reference comparison was performed for these plots.</p>
  <p>Source: the 3 October 2026 report, <i>Asian barrier: saved TT surfaces</i> (final version).</p>
  <p>Related reading: <a href="https://arxiv.org/abs/1505.04648">Chebyshev Interpolation for Parametric Option Pricing</a> and <a href="https://www.chebfun.org/docs/guide/guide04.html">Chebfun and Approximation Theory</a>.</p>
</details>
~~~

[Download the full PDF](/assets/asian-barrier/asian_barrier_3d.pdf)

@@
