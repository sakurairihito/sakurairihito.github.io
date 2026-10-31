@def title = "What does low rank mean?"
@def page_language = "en"
@def hasmath = true
@def description = "Low rank for matrices, functions and tensor trains: exact examples, what smoothness guarantees, and the quantics rank of sin x on uniform and Chebyshev grids."

@@explainer

[← Research notes](/research/)

# What does low rank mean?

@@article-lead
Few products of one-variable functions are enough.
@@

A function $f(x,y)$ is low rank if $f(x,y)\approx\sum_{k=1}^{r} g_k(x)\,h_k(y)$ with small $r$. On a grid this is a matrix whose singular values drop quickly. A tensor train (TT) applies the same idea at every cut between the variables.

~~~
<figure>
  <a href="/assets/low-rank/results/low-rank.png">
    <img src="/assets/low-rank/results/low-rank.png" alt="Left: normalized singular values on a 129 by 129 Chebyshev grid. exp(x+y) drops after 1, sin(x+y) after 2, sin(xy) after 4, sin(10xy) after 10, and noise stays flat. Right: the largest quantics rank of sin(omega x) on 4096 points is exactly 2 on a uniform grid and grows from 7 to 16 on a Chebyshev grid as omega goes from 1 to 100." width="1990" height="863" fetchpriority="high">
  </a>
  <figcaption>Left: singular values of 2D functions. Right: quantics TT rank of $\sin(\omega x)$. Ranks are counted at $s_k/s_1>10^{-10}$.</figcaption>
</figure>
~~~

$\sin(x+y)=\sin x\cos y+\cos x\sin y$ has rank exactly 2. Smooth functions such as $\sin(xy)$ are low rank up to a small error. Noise is full rank.

For one variable, write the grid index in binary digits. On a uniform grid $\sin x$ then has rank exactly 2.

[Details (Japanese, PDF)](/assets/low-rank/low-rank-note-ja.pdf) · [Data](/assets/low-rank/results/summary.json) · [Script](/assets/low-rank/low_rank.py)

[Back to research notes](/research/)

@@
