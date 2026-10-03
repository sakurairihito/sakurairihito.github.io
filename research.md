@def title = "Research notes"
@def description = "Short visual notes on numerical methods, function compression, and applications in finance."

# Research notes

Short visual notes on research ideas and numerical experiments.

## Ideas to explore

### From tensor trains to tree tensor networks

I'd like to explore extending the function-compression approach to tree tensor networks. Could grouping related variables in a tree make multi-asset pricing problems easier to compress?

A first experiment: compare a tensor train with a few tree structures on the same pricing problem, measuring storage and function evaluations at matched accuracy.

An open question: how should the tree be chosen, and can cross interpolation build it efficiently from function samples?

Still an idea to try, rather than a result.

Related reading: [Compressing multivariate functions with tree tensor networks](https://arxiv.org/abs/2410.03572).

### Building a TensorPricing engine

I'd like to build TensorPricing as a personal research project: a small experimental engine connecting function compression with option pricing.

Start with one pricing example, then explore how a compressed representation can be reused as parameters change. Use it to try different tensor formats and interpolation methods, and compare accuracy and computational cost.

### TCI with point-dependent noise

What changes when uncertainty varies from one function evaluation point to another? I'd like to explore tensor cross interpolation (TCI) with point-dependent noise levels.

Could local uncertainty guide pivot selection, repeated sampling, and stopping criteria? A first experiment: introduce known, nonuniform noise levels into a test function and compare reconstruction accuracy and evaluation cost.

## Numerical notes

- [Asian barrier option: a price surface](/asian-barrier/) — Price, Gamma, and Chebyshev spectra before and after degree truncation.

- [Fourier pricing](/fourier-pricing/) — From a distribution of future prices to option prices in frequency space.

- [Can a smooth price surface be compressed?](/compression/) — Exploring low rank and low-degree Chebyshev approximations through a Black–Scholes price surface.
