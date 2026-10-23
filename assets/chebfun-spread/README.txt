Spread option with Chebfun3: reproduction

Source example:
https://www.chebfun.org/examples/applics/BlackScholes2D.html
Chebfun revision: 7574c77680d7e82b79626300bf255498271a72df
https://github.com/chebfun/chebfun

1. Obtain Chebfun at the revision above (the library is not bundled).
2. From this directory, run in MATLAB:
     run_chebfun_spread('/absolute/path/to/chebfun', 'new_results')
   Or in GNU Octave:
     octave --no-gui --quiet --no-init-file --eval "run_chebfun_spread('/absolute/path/to/chebfun', 'new_results')"
3. With the Python dependencies installed:
     python3 -B test_reference.py
     python3 -B analyse_spread.py new_results new_analysis

Use new output directories: the scripts preserve existing results.
To check the bundled outputs without rerunning Chebfun:
     python3 -B analyse_spread.py results new_analysis

The recorded environment is GNU Octave 11.3.0, Python 3.10.0,
NumPy 1.26.4, SciPy 1.15.3, and Matplotlib 3.10.8 on macOS arm64.
Octave uses octave_compat/pagemtimes.m, a deliberately limited adapter
for the one two-input, at-most-3D call used by Chebfun3 evaluation.
It is not a complete MATLAB pagemtimes implementation. The driver
checks the adapter and an analytic polynomial before the price experiment.
Library source files were not edited.

results/: direct quadrature, native Chebfun evaluations, coefficients,
          endpoint values, timings, construction-call counts.
analysis/: independent reference, comparison tables, refinement, figures.
provenance.json: revision and hashes of relevant library and driver files.

The raw Octave CSV files have no headers; price tables contain
T,K,rho,price. Some zero-imaginary outputs use the literal "+0i".
The analysis reader verifies negligible imaginary parts before conversion.
Analysis CSV files have headers and contain real values.

The classic mode reproduces the 2017 algorithm. The default mode uses
the algorithm at the pinned revision. Timing measurements include
counting scalar price calls and are machine/runtime dependent.
Grid evaluation is the median of five calls after one warm-up.
Construction calls include repeats, not only unique parameter points.

The original 150x150 numerical integral is not the exact reference.
The independent conditional integral is validated against the
zero-strike exchange-option formula and an alternate integration limit.
No certified whole-domain error or tail bound is claimed.
