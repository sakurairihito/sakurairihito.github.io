Chebyshev interpolation across a kink

cheb_spline_demo.py is the user-supplied source, preserved unchanged.
Its SHA-256 is recorded in results/summary.json.

Run the original demo:
  python3 -B cheb_spline_demo.py

Run the companion checks, export CSV/JSON tables, and draw the note's figures:
  python3 -B reproduce_cheb_spline.py new_results

Keep both scripts together. Use a new output directory.
The recorded environment is Python 3.10.0, NumPy 1.26.4, SciPy 1.15.3,
and Matplotlib 3.10.8 on macOS arm64.

The comparison uses N+1 DISTINCT nodes for a degree-N global polynomial
and for two degree-N/2 pieces sharing their boundary. The supplied
implementation evaluates that boundary twice, so the piecewise method
uses N+2 sample evaluations, plus the uncounted boundary root search.

"Spline" here means a continuous piecewise Chebyshev polynomial.
No first- or second-derivative continuity is imposed. In the exercise
example the exact Delta has a jump and is undefined at the boundary.
The reference excludes points within 1e-6 of that location.

The exercise example is one exercise decision now versus a European put
at maturity; it is not a multi-date backward-induction solver.
Errors are sampled maxima on 4,001 uniform points. The wrapper also
checks the degree-32 case on 16,001 points, interpolant node residuals,
the boundary root, continuity, and independent barycentric evaluation.

results/absolute_value.csv: first-example errors.
results/exercise_value.csv: second-example price and Delta errors.
results/summary.json: model parameters, source hash, checks, selected rows.
results/*.png: figures used in the website note.
cheb_spline_demo.png: the original demo's figure.
