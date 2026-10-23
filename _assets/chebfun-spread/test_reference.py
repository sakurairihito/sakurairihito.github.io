"""Independent analytic checks for the conditional-integration reference."""
import unittest

import numpy as np
from scipy.special import ndtr

from analyse_spread import reference_prices


class ReferenceTests(unittest.TestCase):
    def test_zero_strike_agrees_with_exchange_option_formula(self):
        # For equal initial spots and volatilities, the exchange price is
        # 2*Phi(sigma*sqrt(2*T*(1-rho))/2)-1.
        t, rho = np.meshgrid([.3, 1., 2.], [-.9, 0., .9], indexing="ij")
        points = np.column_stack([t.ravel(), np.zeros(t.size), rho.ravel()])
        actual, _ = reference_prices(points)
        expected = 2*ndtr(.3*np.sqrt(2*t.ravel()*(1-rho.ravel()))/2)-1
        np.testing.assert_allclose(actual, expected, rtol=0, atol=3e-12)

    def test_prices_are_positive_and_decrease_with_strike(self):
        points = np.array([[1., k, .2] for k in [0., .3, 1., 2.]])
        prices, _ = reference_prices(points)
        self.assertTrue(np.all(prices > 0))
        self.assertTrue(np.all(np.diff(prices) < 0))
        self.assertTrue(np.all(prices <= 1))


if __name__ == "__main__":
    unittest.main()
