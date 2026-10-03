@def title = "Fourier pricing"
@def page_language = "en"
@def hasmath = true
@def description = "A short visual introduction to option pricing in Fourier space, checked against the Black–Scholes formula."

@@explainer

[← Research notes](/research/)

# Fourier pricing

@@article-lead
From a distribution of future prices to an option price—in frequency space.
@@

An option price is a discounted average of its future payoff under the risk-neutral distribution. Fourier pricing evaluates that average using the distribution's **characteristic function**.

## A different view of the same distribution

For the log return $X=\log(S_T/S_0)$, the characteristic function is

$$
\phi(u)=\mathbb E^{\mathbb Q}[e^{\mathrm{i}uX}].
$$

It describes the distribution through its response to waves of different frequencies. In Black–Scholes, log returns are Gaussian: a broader distribution has a faster-decaying frequency spectrum.

~~~
<figure>
  <a href="/assets/fourier-pricing/distribution-and-spectrum.png">
    <img src="/assets/fourier-pricing/distribution-and-spectrum.png" alt="Risk-neutral log-return densities at three volatilities and the magnitudes of their characteristic functions. Broader Gaussian distributions have faster-decaying spectra." width="2000" height="866" fetchpriority="high">
  </a>
  <figcaption>Two views of the same model. Colors match across panels. Time to maturity: 1 year. Interest rate: 3%. The frequency plot shows magnitude only; the characteristic function also has a phase.</figcaption>
</figure>
~~~

## Recover the price

The characteristic function carries the model information. A known weight accounts for the call payoff. Combine them and integrate in frequency space to recover the price, using damping to make the transform well defined.

~~~
<figure>
  <a href="/assets/fourier-pricing/prices-and-convergence.png">
    <img src="/assets/fourier-pricing/prices-and-convergence.png" alt="Fourier prices agree with the Black–Scholes curve across strikes. The maximum absolute error decreases as the frequency cutoff grows, then reaches floating-point precision." width="2000" height="866" loading="lazy">
  </a>
  <figcaption>Spot price 100, volatility 20%, maturity 1 year, rate 3%, no dividends. Prices are checked at 81 strikes from 60 to 140. At cutoff 80, the maximum absolute error is below 10⁻¹⁰.</figcaption>
</figure>
~~~

Black–Scholes gives us an exact reference. Fourier methods are also useful for models with a tractable characteristic function but no simple option-pricing formula.

## Where compression comes in

Fourier pricing supplies an integral to compute. Low-rank methods can exploit additional structure in that integrand or its parameter dependence. The [price-surface note](/compression/) illustrates what low rank and low polynomial degree look like in a simple example.

~~~
<details>
  <summary>Methods, formula, and reproducibility</summary>
  <p>We use the <a href="https://wwwf.imperial.ac.uk/~ajacquie/IC_Num_Methods/IC_Num_Methods_Docs/Literature/CarrMadan.pdf">Carr–Madan damped Fourier formula</a>, with log strike k = log(K/S₀) and the characteristic function of X = log(S_T/S₀). The transformed quantity is the normalized call price multiplied by exp(αk), with α = 1.5. The integrand uses the characteristic function at the shifted argument u − i(α + 1). After inversion we remove the damping and multiply by S₀.</p>
  <p>The computation uses adaptive quadrature over 0 ≤ u ≤ U, with absolute and relative integration tolerances of 10⁻¹². It does not use an FFT. The convergence plot shows the maximum absolute price error over the 81 tested strikes. At large cutoffs, numerical roundoff dominates. Frequency decay and the required cutoff depend on the model and parameters; this example does not establish a speedup or a low-rank bound.</p>
  <p>The code checks the characteristic function against direct integration of the density, verifies its normalization and risk-neutral first moment, and compares prices across several strikes, volatilities, maturities, and damping choices with the Black–Scholes formula.</p>
  <p><a href="/assets/scripts/fourier_pricing_demo.py">Reproduction code</a> · <a href="/assets/fourier-pricing/results.json">Prices and convergence data</a>. Keep <a href="/assets/scripts/bs1d_demo.py">bs1d_demo.py</a> beside the reproduction script.</p>
  <p>Related research: <a href="https://www.mdpi.com/2227-7390/13/11/1828">Learning parameter dependence for Fourier-based option pricing with tensor trains</a>, Sakurai, Takahashi &amp; Miyamoto (2025).</p>
</details>
~~~

[Back to research notes](/research/)

@@
