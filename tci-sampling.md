@def title = "Where does TCI sample a noisy price surface?"
@def page_language = "en"
@def hasmath = true
@def description = "Tensor cross interpolation of a fixed-seed Monte Carlo Asian barrier price grid: how the pivots and rank change with the Monte Carlo sample size."

@@explainer

[← Research notes](/research/)

# Where does TCI sample a noisy price surface?

An Asian barrier call on a $100\times100$ grid in moneyness $m$ and volatility $\sigma$, priced by fixed-seed Monte Carlo (MC). I wanted to see which points tensor cross interpolation (TCI) actually looks at. The tolerance is $\varepsilon_{\rm TCI}=\mathrm{SE}_{\max}/(2\hat V_{\max})$, so with fewer samples the tolerance is looser.

~~~
<figure>
  <a href="/assets/tci-sampling/samples-small-n.png">
    <img src="/assets/tci-sampling/samples-small-n.png" alt="Four price surfaces over moneyness and volatility for 2 thousand, 10 thousand, 100 thousand and one million Monte Carlo pairs. Red dots mark the pivots; the rank grows from 2 to 4." width="2283" height="599" fetchpriority="high">
  </a>
  <figcaption>Pivots (red) and evaluated grid points (dark) for $2\times10^3$ to $10^6$ MC pairs. The rank goes from 2 to 4.</figcaption>
</figure>
~~~

With fewer samples TCI only picks up the rough shape. The main pivots stay near $m\approx0.99$, $1.10$ and $1.20$.

## As a matrix cross

With two variables, TCI is just a matrix cross interpolation, $F\approx F[:,J]\,F[I,J]^{-1}\,F[I,:]$.

~~~
<figure>
  <a href="/assets/tci-sampling/matrix-cross.png">
    <img src="/assets/tci-sampling/matrix-cross.png" alt="The grid-value matrix with four colored pivot columns and rows equals a 100 by 4 matrix of columns, times the inverse of the 4 by 4 pivot matrix, times a 4 by 100 matrix of rows. Below, the reconstruction error and the singular values, which level off after the fourth." width="2368" height="1368" decoding="async">
  </a>
  <figcaption>$10^6$ pairs, rank 4. Same colors mark the same pivot column or row in each factor.</figcaption>
</figure>
~~~

The singular values flatten out after the fourth one, at the MC noise level, and the rank-4 cross stops right there.

[Details (Japanese, PDF)](/assets/tci-sampling/asian-tci-sampling-note-ja.pdf) · [Data](/assets/tci-sampling/data/small_n_summary.csv)

[Back to research notes](/research/)

@@
