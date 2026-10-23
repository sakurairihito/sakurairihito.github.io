@def title = "Chebyshev interpolation across a kink"
@def page_language = "en"
@def hasmath = true
@def description = "A reproduced Python experiment comparing one Chebyshev polynomial with two pieces joined at a known kink, including value and Delta errors."

@@explainer

[← Research notes](/research/)

# Chebyshev interpolation across a kink

@@article-lead
Split at the kink, then approximate each smooth piece.
@@

The supplied `cheb_spline_demo.py` compares a single Chebyshev polynomial with two polynomial pieces. Both use Chebyshev–Lobatto nodes. Re-running the script shows how strongly a known kink can affect the accuracy of the value and its derivative.

~~~
<figure>
  <a href="/assets/chebyshev-spline/results/spline-boundary.png">
    <img src="/assets/chebyshev-spline/results/spline-boundary.png" alt="An exercise value has a kink at spot 89.4953. A degree-32 polynomial oscillates around its Delta jump, while two degree-16 pieces follow the one-sided derivatives." width="1980" height="774" fetchpriority="high">
  </a>
  <figcaption>33 distinct interpolation nodes in each representation. The split location is known before interpolation.</figcaption>
</figure>
~~~

## Two examples

For $f(x)=|x-0.3|$ on $[-1,1]$, splitting at $x=0.3$ leaves two linear functions. Each piece can therefore be represented exactly in exact arithmetic; the observed errors are around floating-point roundoff.

The second example makes one exercise decision:

$$
V(S)=\max\{100-S,\;P_{\mathrm{European}}(S)\}.
$$

The continuation value is a Black–Scholes European put with strike 100, rate 5%, volatility 20%, and maturity one year. The spot interval is $[50,150]$. Solving $100-S=P_{\mathrm{European}}(S)$ gives

$$
S^\star=89.4952812319501.
$$

The left Delta is $-1$; its right-hand limit is approximately $-0.581183$. **Delta is undefined at the boundary.** This is a two-date exercise example, with exercise now or at maturity. The script does not perform backward induction over multiple exercise dates.

## Reproduced errors

~~~
<figure>
  <a href="/assets/chebyshev-spline/results/spline-convergence.png">
    <img src="/assets/chebyshev-spline/results/spline-convergence.png" alt="Three convergence plots compare one polynomial with two pieces: absolute-value error, exercise-value error, and Delta error. Splitting sharply reduces all three errors." width="2340" height="774" loading="lazy">
  </a>
  <figcaption>Maximum absolute errors sampled on 4,001 uniform points. Delta excludes points within 10⁻⁶ of the exercise boundary. These are sampled errors, not uniform error bounds.</figcaption>
</figure>
~~~

For the exercise example:

~~~<div style="overflow-x:auto">~~~

| Distinct nodes | Value: one polynomial | Value: two pieces | Delta: one polynomial | Delta: two pieces |
| ---: | ---: | ---: | ---: | ---: |
| 17 | $3.14\times10^{-1}$ | $8.07\times10^{-5}$ | $2.16\times10^{-1}$ | $5.25\times10^{-5}$ |
| 33 | $1.44\times10^{-1}$ | $7.06\times10^{-11}$ | $2.25\times10^{-1}$ | $7.09\times10^{-11}$ |
| 65 | $1.30\times10^{-1}$ | $1.49\times10^{-13}$ | $2.30\times10^{-1}$ | $2.22\times10^{-12}$ |

~~~</div>~~~

A single polynomial must approximate both sides of the kink. Its sampled Delta error remains about 0.2 over the tested degrees. Each split piece instead approximates a smooth branch. Increasing the degree eventually reaches a numerical error floor, especially after differentiation.

## What is counted?

A global degree-$N$ polynomial uses $N+1$ nodes. For even $N$, two degree-$N/2$ pieces have $N+2$ node slots, but share the boundary: **there are also $N+1$ distinct nodes**.

The supplied implementation evaluates the shared boundary twice, so it performs $N+2$ sample evaluations. Finding the boundary with Brent's method is an additional cost, excluded from the plot. The comparison matches distinct-node counts; it is not an equal-runtime experiment.

Here “Chebyshev spline” means a piecewise polynomial joined continuously in value. No continuity of the first or second derivative is imposed. At the exercise boundary, enforcing a continuous Delta would remove a real feature of the function.

The [parametric-pricing note](/chebyshev-pricing/) explains why smooth price dependence supports fast polynomial approximation. This example illustrates the complementary case: when the target retains a kink, the interval partition matters.

~~~
<details>
  <summary>Reproduction, checks &amp; downloads</summary>
  <p>The <a href="/assets/chebyshev-spline/cheb_spline_demo.py">supplied script</a> is preserved unchanged. The <a href="/assets/chebyshev-spline/reproduce_cheb_spline.py">reproduction wrapper</a> exports its tables and draws the figures above. Download the <a href="/assets/chebyshev-spline/reproduction.zip">complete reproduction bundle</a>.</p>
  <p>Run <code>python3 -B cheb_spline_demo.py</code> for the original plot, or <code>python3 -B reproduce_cheb_spline.py new_results</code> for the tables, checks, and revised figures. Keep both scripts together. Dependencies: NumPy, SciPy, and Matplotlib. The saved run used Python 3.10.0, NumPy 1.26.4, SciPy 1.15.3, and Matplotlib 3.10.8.</p>
  <p>Checks include the boundary equation, interpolation at the nodes, continuity of the two pieces, and comparison with an independent barycentric evaluation. A separate 16,001-point grid confirms the displayed degree-32 error scale. The exact derivative at the kink is never used as a reference.</p>
  <p>Data: <a href="/assets/chebyshev-spline/results/absolute_value.csv">absolute-value errors</a> · <a href="/assets/chebyshev-spline/results/exercise_value.csv">exercise-value and Delta errors</a> · <a href="/assets/chebyshev-spline/results/summary.json">parameters, source hash, and validation results</a>.</p>
  <p><a href="https://numpy.org/doc/stable/reference/generated/numpy.polynomial.chebyshev.Chebyshev.fit.html">NumPy's Chebyshev.fit</a> solves a least-squares problem; here the degree and number of distinct nodes make it the square interpolation problem, up to floating-point error. The boundary uses <a href="https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.brentq.html">SciPy's brentq</a>.</p>
</details>
~~~

[Back to research notes](/research/)

@@
