@def title = "Kinks in option prices"
@def page_language = "en"
@def hasmath = true
@def description = "Where an Asian barrier option price bends sharply, what this does to a Chebyshev tensor train, and where the kinks of a Monte Carlo estimate come from."

@@explainer

[← Research notes](/research/)

# Kinks in option prices

An Asian barrier call over moneyness $m=S_0/K$ and volatility $\sigma$, with the barrier at $m=B/K\approx0.909$. This time the tensor train is built on $m\in[0.8,1.2]$, so the barrier is inside the domain.

## Barrier inside the domain

~~~
<figure>
  <a href="/assets/option-kink/barrier-inside-surface.png">
    <img src="/assets/option-kink/barrier-inside-surface.png" alt="Price and Gamma surfaces of an Asian barrier option for m up to 1. The price rises steeply just above the barrier. Gamma has a sharp peak there without truncation and with Chebyshev degree 56 in m, but becomes a smooth wave with degree 13." width="1950" height="1170" fetchpriority="high">
  </a>
  <figcaption>Price (top) and Gamma (bottom) for $m\le1$. Left: no degree truncation. Middle and right: degrees in $m$ chosen by the truncation rule for two Monte Carlo seeds. The red line is the barrier.</figcaption>
</figure>
~~~

The price goes up steeply just above the barrier, and Gamma has a sharp peak there. With degree 13 in $m$ the peak gets smeared into a wave. With the barrier inside the domain, the truncation rule picks a degree this low for some seeds.

~~~
<figure>
  <a href="/assets/option-kink/barrier-inside-slice.png">
    <img src="/assets/option-kink/barrier-inside-slice.png" alt="Delta and Gamma along m at sigma 0.20. A single domain with low degree misses the Gamma peak near the barrier; splitting the domain at the barrier follows the reference." width="1560" height="546" decoding="async">
  </a>
  <figcaption>Delta and Gamma at $\sigma=0.20$. Splitting the domain at the barrier follows the reference.</figcaption>
</figure>
~~~

If I split the domain at the barrier, the steep part sits at the edge of each piece and the peak comes back.

## Where the kinks come from

In a Monte Carlo estimate, each path pays $mA-1$ once $m$ is above its own threshold $\max(b/L,\,1/A)$. Here $A$ is the path's average, $L$ its lowest running average, and $b=B/K$. At $m=1/A$ the path starts finishing in the money, which gives a kink. At $m=b/L$ the path stops being knocked out and pays right away, which gives a small jump.

~~~
<figure>
  <a href="/assets/option-kink/mc-kinks.png">
    <img src="/assets/option-kink/mc-kinks.png" alt="Left: a fixed-seed Monte Carlo price with 2 thousand pairs is jagged near the barrier, while one million pairs give a smooth line. Right: histogram of path thresholds; barrier jumps cluster just above the barrier and exercise kinks spread over the whole domain." width="1785" height="714" decoding="async">
  </a>
  <figcaption>(a) Fixed-seed Monte Carlo prices near the barrier. (b) Where the exercise kinks and barrier jumps of $2\times10^4$ paths are.</figcaption>
</figure>
~~~

The barrier jumps pile up just above the barrier, and the exercise kinks are spread over the whole domain. With few samples the price is visibly jagged. With many, the kinks average out into a smooth curve.

See also: [Option prices near expiry](/option-maturity/) · [Chebyshev interpolation across a kink](/chebyshev-spline/) · [Where does TCI sample a noisy price surface?](/tci-sampling/)

[Back to research notes](/research/)

@@
