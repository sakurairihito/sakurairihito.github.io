@def title = "Asian barrier option: a price surface"
@def hasmath = true
@def description = "A saved tensor-train price surface, Gamma, and Chebyshev coefficient spectra."

@@explainer

[← Research notes](/research/)

# Asian barrier option: a price surface

@@article-lead
A smooth-looking price surface. More structure in its second derivative.
@@

These plots evaluate a saved tensor train over moneyness $m=S_0/K$ and volatility $\sigma$. The degree-truncated approximation (labelled **ME** in the figures) retains degrees **26 and 7**, with **TT bond dimension 3**.

~~~
<figure>
  <a href="/assets/asian-barrier/asian_price_surface.png">
    <img src="/assets/asian-barrier/asian_price_surface.png" alt="Three-dimensional Asian barrier option price surface over moneyness and volatility, evaluated from the degree-truncated tensor train." width="2106" height="1494" decoding="async">
  </a>
  <figcaption>The saved price surface. Click any figure to enlarge it.</figcaption>
</figure>
~~~

## Price and Gamma

Truncation changes the price by at most **0.00111 on the plotted grid**. The Gamma surface looks smoother after truncation. A matched reference is still needed to assess accuracy.

~~~
<figure>
  <a href="/assets/asian-barrier/asian_price_gamma_comparison.png">
    <img src="/assets/asian-barrier/asian_price_gamma_comparison.png" alt="Raw and degree-truncated tensor-train predictions: similar price surfaces above, and a visibly smoother Gamma surface after truncation below. Each row uses the same vertical scale." width="2080" height="1680" loading="lazy" decoding="async">
  </a>
  <figcaption>Price above; Gamma below. Each row uses a shared vertical scale.</figcaption>
</figure>
~~~

## Which degrees remain?

The marginal Chebyshev coefficient amplitudes decay before reaching a small tail. The cutoffs retain degrees through **26 in moneyness** and **7 in volatility**.

~~~
<figure>
  <a href="/assets/asian-barrier/asian_tt_spectra.png">
    <img src="/assets/asian-barrier/asian_tt_spectra.png" alt="Marginal Chebyshev coefficient spectra for moneyness and volatility, comparing the raw tensor train with truncation at degrees 26 and 7." width="1872" height="1040" loading="lazy" decoding="async">
  </a>
  <figcaption>Both spectra come from the saved TT. Isolating how TCI changes Monte Carlo noise would require full-grid MC values using the same samples.</figcaption>
</figure>
~~~

## Why so few coefficients?

What I find striking is that a calculation involving **365 path steps and a barrier** can end up with such a compact representation. The paths are complicated, yet their average may have a much simpler shape.

Averaging over paths can smooth the price's dependence on its inputs. Smooth variation can make high-degree Chebyshev coefficients small. **Low rank describes something else: a simple coupling between variables.** Smoothness alone does not guarantee low rank. Here, the saved approximation combines modest polynomial degrees with rank 3.

When does this simplicity break down? Near the barrier, close to maturity, or over a wider parameter range? That is something I'd like to explore.

~~~
<details>
  <summary>Calculation settings and source</summary>
  <p>Risk-neutral model: μ = r = 0.05, strike K = 110, barrier B = 100, maturity T = 1. There are 365 monitoring steps and 10<sup>6</sup> antithetic pairs, with seed 1.</p>
  <p>Plotted interior domain: m ∈ [0.93, 1.17], σ ∈ [0.16, 0.24]. These are saved TT evaluations; no new sampling or reference comparison was performed for these plots.</p>
  <p>Source: the 3 October 2026 report, <i>Asian barrier: saved TT surfaces</i> (final version).</p>
  <p>Related reading: <a href="https://arxiv.org/abs/1505.04648">Chebyshev Interpolation for Parametric Option Pricing</a> and <a href="https://www.chebfun.org/docs/guide/guide04.html">Chebfun and Approximation Theory</a>.</p>
</details>
~~~

[Download the full PDF](/assets/asian-barrier/asian_barrier_3d.pdf)

@@
