"""Figures and checks for /fourier-pricing/.

Run: python3 -B _assets/scripts/fourier_pricing_demo.py
Requires numpy, scipy, matplotlib, and adjacent bs1d_demo.py.
Carr-Madan inversion is normalized by spot and evaluated by adaptive quadrature,
not an FFT. All errors below compare with closed-form Black-Scholes prices.
"""
from pathlib import Path
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import quad

from bs1d_demo import call_price, GREEN, ORANGE, INK

OUTPUT = Path(__file__).resolve().parents[1] / "fourier-pricing"
SPOT, RATE, MATURITY, VOLATILITY = 100., .03, 1., .20


def characteristic(u, volatility=VOLATILITY, maturity=MATURITY, rate=RATE):
    """Risk-neutral characteristic function of X = log(S_T / S_0)."""
    return np.exp(1j*u*(rate-volatility**2/2)*maturity - volatility**2*maturity*u*u/2)


def fourier_call(strike, cutoff=80., alpha=1.5, volatility=VOLATILITY,
                 maturity=MATURITY, rate=RATE, spot=SPOT):
    """Damped Fourier inversion, with k = log(K / S_0)."""
    k = np.log(strike/spot)
    def integrand(u):
        denominator = alpha**2 + alpha - u*u + 1j*(2*alpha+1)*u
        transform = (np.exp(-rate*maturity)
                     * characteristic(u-1j*(alpha+1), volatility, maturity, rate)
                     / denominator)
        return (np.exp(-1j*u*k)*transform).real
    integral, _ = quad(integrand, 0, cutoff, epsabs=1e-12, epsrel=1e-12, limit=200)
    return float(spot*np.exp(-alpha*k)*integral/np.pi)


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    assert characteristic(0) == 1
    assert np.isclose(characteristic(-1j), np.exp(RATE*MATURITY))
    # Check the characteristic function against direct density integration.
    mu = (RATE-VOLATILITY**2/2)*MATURITY
    std = VOLATILITY*np.sqrt(MATURITY)
    for frequency in [0., 1., 5., 15.]:
        def density(z):
            return np.exp(-.5*((z-mu)/std)**2)/(std*np.sqrt(2*np.pi))
        re = quad(lambda z: np.cos(frequency*z)*density(z), mu-12*std, mu+12*std, epsabs=1e-12)[0]
        im = quad(lambda z: np.sin(frequency*z)*density(z), mu-12*std, mu+12*std, epsabs=1e-12)[0]
        assert abs(re+1j*im-characteristic(frequency)) < 1e-11
    # Check inversion across strikes, volatilities, maturities, and damping choices.
    checked_errors = []
    for vol in [.1, .2, .4]:
        for maturity in [.5, 1., 2.]:
            for strike in [60., 100., 140.]:
                exact = call_price(SPOT, vol, strike=strike, maturity=maturity, rate=RATE)
                for alpha in [.75, 1.5, 2.]:
                    error = abs(fourier_call(strike, cutoff=200., alpha=alpha,
                                            volatility=vol, maturity=maturity)-exact)
                    assert error < 1e-9
                    checked_errors.append(float(error))

    strikes = np.linspace(60, 140, 81)
    exact = call_price(SPOT, VOLATILITY, strike=strikes)
    prices = np.array([fourier_call(k) for k in strikes])
    assert np.max(np.abs(prices-exact)) < 1e-10
    assert np.max(np.abs(prices-[fourier_call(k, cutoff=160.) for k in strikes])) < 1e-10
    cutoffs = [2, 4, 6, 8, 12, 16, 24, 32, 40, 60, 80]
    errors = [float(np.max(np.abs([fourier_call(k, cutoff=u) for k in strikes]-exact)))
              for u in cutoffs]

    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11,
                         "text.color": INK, "axes.labelcolor": INK,
                         "axes.spines.top": False, "axes.spines.right": False})
    def save(fig, name):
        fig.savefig(OUTPUT/name, dpi=180, bbox_inches="tight", facecolor="white")
        plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.7), layout="constrained")
    x = np.linspace(-1.2, 1.2, 1000)
    u = np.linspace(0, 40, 500)
    for vol, color in zip([.1, .2, .4], ["#4273a3", GREEN, ORANGE]):
        mean, std = (RATE-vol**2/2)*MATURITY, vol*np.sqrt(MATURITY)
        density = np.exp(-.5*((x-mean)/std)**2)/(std*np.sqrt(2*np.pi))
        axes[0].plot(x, density, color=color, label=f"Volatility {vol:.0%}")
        axes[1].semilogy(u, np.abs(characteristic(u, volatility=vol)), color=color)
    axes[0].set(title="Distribution of future log returns", xlabel="Log return X = log(S_T / S_0)",
                ylabel="Risk-neutral density", xlim=(-1.2, 1.2), ylim=(0, 4.2))
    axes[1].set(title="The same distribution in frequency space", xlabel="Frequency u",
                ylabel="Characteristic-function magnitude |φ(u)|", xlim=(0, 40), ylim=(1e-12, 1.5))
    axes[0].legend(fontsize=9)
    for ax in axes:
        ax.grid(alpha=.18)
    save(fig, "distribution-and-spectrum.png")

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.7), layout="constrained")
    axes[0].plot(strikes, exact, color=GREEN, linewidth=2, label="Black–Scholes formula")
    axes[0].plot(strikes[::4], prices[::4], "o", markerfacecolor="none", color=ORANGE,
                 markersize=5, label="Fourier inversion (cutoff 80)")
    axes[0].set(title="Recovering the option price", xlabel="Strike K", ylabel="Call price", xlim=(60, 140))
    axes[0].legend(fontsize=9)
    axes[1].semilogy(cutoffs, errors, "o-", color=GREEN, markersize=4)
    axes[1].set(title="Including a wider frequency range", xlabel="Frequency cutoff U",
                ylabel="Maximum absolute price error", xticks=[0, 20, 40, 60, 80])
    for ax in axes:
        ax.grid(alpha=.18)
    save(fig, "prices-and-convergence.png")

    metrics = {"model": "Black-Scholes European calls, no dividends", "spot": SPOT,
               "rate": RATE, "time_to_maturity_years": MATURITY,
               "pricing_volatility": VOLATILITY, "distribution_volatilities": [.1, .2, .4],
               "log_variable": "X=log(S_T/S_0)", "log_strike": "k=log(K/S_0)",
               "damping_alpha": 1.5, "method": "adaptive quadrature, not FFT",
               "quadrature_tolerances": {"absolute": 1e-12, "relative": 1e-12},
               "pricing_cutoff": 80., "strikes": strikes.tolist(),
               "fourier_prices": prices.tolist(), "reference_prices": exact.tolist(),
               "maximum_absolute_price_error": float(np.max(np.abs(prices-exact))),
               "cutoff_convergence": [{"cutoff": cutoff, "maximum_absolute_price_error": error}
                                      for cutoff, error in zip(cutoffs, errors)],
               "cross_parameter_checks": len(checked_errors),
               "cross_parameter_maximum_error": max(checked_errors),
               "scope": "errors on tested strikes and parameters; no speed or low-rank claim"}
    (OUTPUT/"results.json").write_text(json.dumps(metrics, indent=2)+"\n")
    print(json.dumps({key: metrics[key] for key in ["maximum_absolute_price_error",
                      "cross_parameter_checks", "cross_parameter_maximum_error", "cutoff_convergence"]}, indent=2))


if __name__ == "__main__":
    main()
