@def title = "Option prices near expiry"
@def page_language = "en"
@def hasmath = true
@def description = "A visual Black-Scholes example showing how a smooth call-price curve approaches a kinked payoff as maturity shrinks, and what this means for polynomial approximation."

@@explainer

[← Research notes](/research/)

# Option prices near expiry

@@article-lead
A smooth price curve can still become difficult to resolve near expiry.
@@

An option payoff and its price before expiry need not have the same smoothness. This note varies the remaining maturity of a European call while keeping all other inputs fixed. The resulting curves show where the smoothing disappears, and why the approximation domain matters when choosing a basis.

~~~
<figure>
  <a href="/assets/option-maturity/results/call-maturity.png">
    <img src="/assets/option-maturity/results/call-maturity.png" alt="Black-Scholes call prices for one year, three months, thirty days and one day of remaining maturity approach the dashed expiry payoff. A close-up shows the shrinking rounded region near strike 100." width="2280" height="1045" fetchpriority="high">
  </a>
  <figcaption>Left: spot prices from 60 to 140. Right: a close-up near the strike. Markers give the price at S = 100. These are theoretical curves at fixed model inputs, not the trajectory of a traded option.</figcaption>
</figure>
~~~

## A controlled maturity comparison

Write $\tau=T-t$ for the time remaining until expiry. We use strike $K=100$, volatility $\sigma=0.2$, and zero interest rate and dividend yield. For $S>0$ and $\tau>0$, the Black–Scholes call price is

$$
C(S,\tau)=S\Phi(d_1)-K\Phi(d_2),\qquad
d_1=\frac{\log(S/K)+\sigma^2\tau/2}{\sigma\sqrt{\tau}},\qquad
d_2=d_1-\sigma\sqrt{\tau},
$$

where $\Phi$ is the standard normal cumulative distribution function. At expiry we evaluate the payoff directly:

$$
C(S,0)=(S-K)_+.
$$

| Remaining maturity | Years | Price at $S=K=100$ |
| --- | ---: | ---: |
| 1 year | 1 | 7.965567 |
| 3 months | 0.25 | 3.987761 |
| 30 days | $30/365$ | 2.287151 |
| 1 day | $1/365$ | 0.417630 |
| Expiry | 0 | 0 |

Days use a 365-day year; three months means exactly 0.25 years. **In this zero-rate, zero-dividend model, holding spot and volatility fixed, the price decreases as the remaining time shrinks.** This is not a claim about every option or about market prices along a changing spot path.

At the strike, the formula simplifies to

$$
C(K,\tau)=K\left[2\Phi\!\left(\frac{\sigma\sqrt{\tau}}{2}\right)-1\right]
\sim\frac{K\sigma\sqrt{\tau}}{\sqrt{2\pi}}
\quad(\tau\downarrow0).
$$

Thus the at-the-money price approaches zero like $\sqrt{\tau}$, rather than linearly in remaining time.

## Smooth prices, concentrated curvature

For every positive $\tau$, the price is smooth in positive spot. Its spot derivatives are

$$
\Delta=\Phi(d_1),\qquad
\Gamma=\frac{\phi(d_1)}{S\sigma\sqrt{\tau}},
$$

where $\phi$ is the standard normal density. Near expiry, Delta changes rapidly from approximately zero to approximately one around the strike. At $S=K$,

$$
\Gamma(K,\tau)\sim\frac{1}{K\sigma\sqrt{2\pi\tau}}.
$$

The region where Delta changes has a characteristic spot width of order $K\sigma\sqrt{\tau}$. This scale follows from the standardized log-moneyness in $d_1$; it is not a sharp boundary. The transition becomes narrower while Gamma grows. At expiry the payoff has a kink, and its ordinary Delta and Gamma are undefined at the strike.

## Implications for an approximation basis

[Gaß, Glau, Mahlstedt and Mair (2018)](https://link.springer.com/article/10.1007/s00780-018-0361-y) give analyticity conditions and error bounds for Chebyshev interpolation of parametric option prices. Their bounds depend on the domain of analytic extension and the size of the function there; the paper also discusses piecewise Chebyshev approximation. See the [paper note](/chebyshev-pricing/) for the offline/online construction.

The present example explains why positive-time smoothness alone is not enough to choose a fixed polynomial degree for all maturities. A joint spot–maturity domain that includes $\tau=0$ contains the payoff kink; at the strike it also contains the square-root dependence on $\tau$. One cannot simply extend a positive-maturity analyticity argument through that boundary.

Two structural choices are relevant. First, local refinement near the strike can resolve a narrow transition without refining the whole spot interval equally. At positive maturity, splitting exactly at the strike does not make either price branch linear: the rounded transition remains. At expiry, however, the two payoff branches are linear, as in the [piecewise interpolation example](/chebyshev-spline/).

Second, remove redundant scales before approximating. In the zero-rate setting here,

$$
x=\frac{S}{K},\qquad w=\sigma\sqrt{\tau},\qquad C=K\,G(x,w),
$$

$$
G(x,w)=x\Phi\!\left(\frac{\log x}{w}+\frac{w}{2}\right)
-\Phi\!\left(\frac{\log x}{w}-\frac{w}{2}\right),\qquad w>0.
$$

At $w=0$, define $G(x,0)=(x-1)_+$. Total volatility $w$ absorbs the separate volatility and maturity inputs, but does not remove the kink at $(x,w)=(1,0)$.

For tensor cross interpolation (TCI), the coordinate domain and its resolution therefore deserve attention alongside the tensor rank. **This figure does not measure interpolation errors, TT ranks, or sampling costs.** Whether a coordinate change or local partition improves those quantities requires a separate comparison at matched accuracy, including Delta and Gamma if they are outputs of interest.

## Reproduce the figure

Download the [Python script](/assets/option-maturity/plot_maturity.py), then run it with NumPy, SciPy and Matplotlib installed:

```bash
python3 -B plot_maturity.py new_results
```

Use a new output-directory name. The script exports both figure formats, all five price curves on 3,201 spot points, and a numerical-check summary.

The saved run checks four prices against independent integration of the terminal payoff over a truncated standard-normal interval; their maximum discrepancy is below $10^{-10}$. It also checks price bounds, maturity monotonicity on the sampled grid, the expiry limit, and centered finite-difference checks of Delta and Gamma. These are numerical consistency checks, not certified error bounds.

Downloads: [PNG](/assets/option-maturity/results/call-maturity.png) · [SVG](/assets/option-maturity/results/call-maturity.svg) · [Price data](/assets/option-maturity/results/call-maturity.csv) · [Checks and package versions](/assets/option-maturity/results/checks.json).

[Back to research notes](/research/)

@@
