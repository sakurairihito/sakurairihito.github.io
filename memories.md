@def title = "Research memories"
@def description = "Figures, small discoveries, and things I remember from research."

~~~
<section class="memories" aria-labelledby="memories-title">
  <h1 id="memories-title">Research memories</h1>
  <p class="memories-intro">Figures and memories.</p>

  <article class="memory-entry" id="quantum-impurity-2022" aria-labelledby="impurity-memory-title">
    <figure class="memory-figure">
      <a href="/assets/memories/quantum-impurity-model-2022.png" aria-label="Open the quantum impurity model figure at full size">
        <img src="/assets/memories/quantum-impurity-model-2022.png" alt="A strongly correlated material is mapped to impurity sites coupled to bath sites. A solver computes the local Green’s function, which is used to update the bath in a self-consistency loop." width="815" height="329" decoding="async">
      </a>
      <figcaption>A quantum impurity model and the DMFT loop.</figcaption>
    </figure>
    <div class="memory-story">
      <p class="memory-status">2022</p>
      <h2 id="impurity-memory-title">My first paper!</h2>
      <p>A hybrid quantum–classical approach to the imaginary-time Green’s function of a quantum impurity model.</p>
      <p class="memory-reference">R. Sakurai, W. Mizukami, and H. Shinaoka,<br>
        <a href="https://doi.org/10.1103/PhysRevResearch.4.023219">Hybrid quantum-classical algorithm for computing imaginary-time correlation functions</a>.<br>
        <i>Phys. Rev. Research</i> <b>4</b>, 023219 (2022). Figure: <a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a>.
      </p>
    </div>
  </article>
  <article class="memory-entry" id="tensor-train-greeks-2025" aria-labelledby="greeks-memory-title">
    <figure class="memory-figure">
      <a href="/assets/memories/tensor-train-greeks-2025.png" aria-label="Open the option prices and Greeks figure at full size">
        <img src="/assets/memories/tensor-train-greeks-2025.png" alt="Four plots compare tensor-train methods in red and blue with Monte Carlo in green: option price and Vega versus volatility, and Delta and Gamma versus the initial asset price. The curves closely overlap, with visible Monte Carlo fluctuations in Gamma." width="1001" height="868" loading="lazy" decoding="async">
      </a>
      <figcaption>Five-asset min-call with random correlations. Red/blue: tensor trains; green: Monte Carlo.</figcaption>
    </figure>
    <div class="memory-story">
      <p class="memory-status">2025</p>
      <h2 id="greeks-memory-title">Prices and Greeks with tensor trains</h2>
      <p>Tensor trains compress Fourier-based prices and their sensitivities. These slices closely match Monte Carlo.</p>
      <p class="memory-reference">R. Sakurai, K. Miyamoto, and T. Okubo,<br>
        <a href="https://arxiv.org/html/2507.08482v1">Tensor train representations of Greeks for Fourier-based option pricing of multi-asset options</a>.<br>
        arXiv:2507.08482v1 (2025). Figure: <a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a>.
      </p>
    </div>
  </article>
</section>
~~~
