@def title = "Can a smooth price surface be compressed?"
@def page_language = "en"
@def hasmath = true
@def description = "A visual experiment: compress a Black–Scholes price surface using low rank and low-degree Chebyshev polynomials."

@@explainer

[← Research notes](/research/)

# Can a smooth price surface be compressed?

@@article-lead
One price surface. Two ways to make it smaller.
@@

Change the stock price and volatility, and a Black–Scholes call price traces out a smooth surface. Looking at it, can you tell how much information we need to describe it?

~~~
<figure>
  <a href="/assets/compression/bs1d-surface.png">
    <img src="/assets/compression/bs1d-surface.png" alt="Three-dimensional Black–Scholes call price surface over stock price and volatility. The price rises smoothly along both axes." width="1238" height="1316" fetchpriority="high">
  </a>
  <figcaption>Stock price: 50–150. Volatility: 5–60%. Strike: 100. Time to maturity: 1 year. Interest rate: 3%. No dividends. Click any figure to enlarge it.</figcaption>
</figure>
~~~

## How many components?

Sample the surface on a 128 × 128 grid. Low rank means approximating this table by a few products of one-variable functions:

$$
C(S,\sigma)\approx\sum_{\alpha=1}^{r}u_\alpha(S)v_\alpha(\sigma).
$$

The singular values fall quickly. **Only a few components carry most of the information.**

~~~
<figure>
  <a href="/assets/compression/bs1d-rank.png">
    <img src="/assets/compression/bs1d-rank.png" alt="Rapid singular-value decay and decreasing approximation error as the rank increases, comparing SVD and matrix cross interpolation." width="2000" height="866" loading="lazy">
  </a>
  <figcaption>SVD gives the best approximation of each rank on this grid. Cross interpolation follows a similar error trend.</figcaption>
</figure>
~~~

## Rebuild the surface from a few slices

Matrix cross interpolation (MCI) combines selected rows and columns. Here, **8 rows and 8 columns** reconstruct the surface with a relative error of about **0.0010%**.

~~~
<figure>
  <a href="/assets/compression/bs1d-cross.png">
    <img src="/assets/compression/bs1d-cross.png" alt="Original and rank-8 reconstructed surfaces look nearly identical. Below are the selected rows and columns and the absolute error." width="1999" height="1710" loading="lazy">
  </a>
  <figcaption>The selected slices contain 1,984 of the 16,384 entries. The maximum absolute price error is about 0.0017. The error panel uses its own color scale.</figcaption>
</figure>
~~~

## How much detail along each axis?

Now expand each direction in Chebyshev polynomials. Higher degrees describe finer detail. **Their coefficients get small quickly**, so we can drop the high-degree terms.

~~~
<figure>
  <a href="/assets/compression/bs1d-chebyshev-spectrum.png">
    <img src="/assets/compression/bs1d-chebyshev-spectrum.png" alt="Chebyshev coefficients decay in both directions, faster for volatility in this example. A heatmap shows the two-dimensional coefficients and the retained low-degree block." width="1999" height="902" loading="lazy">
  </a>
  <figcaption>Left: coefficient norms grouped by degree in each direction. Right: individual coefficients. Both are normalized by the full coefficient norm; the dashed box retains degrees 0–32 in stock price and 0–24 in volatility.</figcaption>
</figure>
~~~

## Low rank + low degree

Rank counts the products we add together. Degree controls the detail within each one-variable function. **This example allows both to stay modest.**

Keep degree **32 in stock price**, degree **24 in volatility**, and compress the coefficient matrix to **rank 8**. The result needs **464 coefficients**, with relative error **$3.9\times10^{-6}$** at new test points.

~~~
<figure>
  <a href="/assets/compression/bs1d-chebyshev-convergence.png">
    <img src="/assets/compression/bs1d-chebyshev-convergence.png" alt="Error decreases as the polynomial degree grows. Increasing rank at fixed degrees eventually reaches the error floor from degree truncation." width="2000" height="884" loading="lazy">
  </a>
  <figcaption>Increasing rank eventually stops helping if the polynomial degrees stay fixed. Both choices matter.</figcaption>
</figure>
~~~

A smooth appearance is a starting point. Here, the spectra and reconstruction errors show which structure we can actually use.

~~~
<details>
  <summary>Methods, accuracy, and reproducibility</summary>
  <p>The first experiment uses the <a href="https://www.columbia.edu/~mh2078/FoundationsFE/BlackScholes.pdf">Black–Scholes formula</a> on a uniform 128 × 128 grid. All relative errors are Frobenius errors, not pointwise relative errors. The teaching MCI implementation searches the full residual: 1,984 counts retained entries, not function evaluations. Its reconstruction solves a linear system with the selected intersection matrix.</p>
  <p>The Chebyshev experiment separately evaluates a full 129 × 129 Chebyshev–Lobatto grid. Coordinates are mapped as S = 100 + 50x and σ = 0.325 + 0.275y. A type-I discrete cosine transform gives standard, unnormalized Chebyshev coefficients through degree 128 in both directions. Coefficients are checked against a 193 × 193 construction.</p>
  <p>Truncation to degrees 32 and 24 leaves 33 × 25 = 825 coefficients. Its relative error is 3.94 × 10⁻⁷. A separate SVD of this coefficient matrix gives rank-8 factors with 8(33 + 25) = 464 stored coefficients, including singular values absorbed into one factor. This coefficient-space SVD is not the optimal SVD for a uniform price grid.</p>
  <p>Both polynomial errors are measured against exact prices at a disjoint 192 × 190 uniform midpoint grid. The combined degree/rank approximation has relative error 3.91 × 10⁻⁶ and maximum absolute error 5.46 × 10⁻⁴. Storage counts exclude metadata and do not describe construction costs. These are sampled checks, not bounds over the entire domain or guarantees for Greeks.</p>
  <p>Low degree bounds the possible separation rank, but the two measures are different: a degree-32/24 coefficient matrix has rank at most 25, and here rank 8 suffices at the reported accuracy. Conversely, a product of two degree-100 polynomials can have rank 1. Results depend on the domain, model parameters, and requested accuracy.</p>
  <p>Reproduce the figures: <a href="/assets/scripts/bs1d_demo.py">price surface and MCI code</a> · <a href="/assets/scripts/bs1d_chebyshev.py">Chebyshev code</a>. Keep both scripts in the same folder. Download <a href="/assets/compression/bs1d-results.json">grid results</a> or <a href="/assets/compression/bs1d-chebyshev-results.json">Chebyshev spectra, errors, and factor coefficients</a>.</p>
  <p>Further reading: <a href="https://scipost.org/10.21468/SciPostPhys.18.3.104">Núñez Fernández et al., tensor cross interpolation (2025)</a>; <a href="https://www.chebfun.org/publications/Chebfun2paper.pdf">Townsend &amp; Trefethen, Chebfun2 (2013)</a>; <a href="https://docs.scipy.org/doc/scipy/reference/generated/scipy.fft.dct.html">SciPy’s DCT definition</a>. For the connection to parameter-dependent option pricing: <a href="https://www.mdpi.com/2227-7390/13/11/1828">Sakurai, Takahashi &amp; Miyamoto (2025)</a>.</p>
</details>
~~~

[Back to research notes](/research/)

@@
