"""
Chebyshev補間 vs Chebyshevスプライン(区間分割)の比較デモ

- Chebyshev–Lobatto点(第2種点、Gaß et al. 2018 と同じ)で補間
- スプライン = 折れ目の位置で区間を切り、各区間で別々にChebyshev補間してつなぐ
- 比較は「総ノード数をそろえて」行う
"""
import numpy as np
from numpy.polynomial import Chebyshev
from scipy.stats import norm
from scipy.optimize import brentq
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


# ---------- Chebyshev補間(1区間) ----------
def lobatto_nodes(a, b, N):
    """[a,b] 上のChebyshev–Lobatto点 N+1 個"""
    k = np.arange(N + 1)
    x = np.cos(np.pi * k / N)
    return a + (b - a) * (x + 1) / 2


def cheb_interp(f, a, b, N):
    """[a,b] で次数 N のChebyshev補間(Lobatto点で厳密に補間)"""
    x = lobatto_nodes(a, b, N)
    return Chebyshev.fit(x, f(x), deg=N, domain=[a, b])


# ---------- Chebyshevスプライン ----------
class ChebSpline:
    """breaks = [a, c1, ..., b] で区間を切り、各区間を次数 N で補間"""

    def __init__(self, f, breaks, N):
        self.breaks = np.asarray(breaks, dtype=float)
        self.pieces = [cheb_interp(f, lo, hi, N)
                       for lo, hi in zip(self.breaks[:-1], self.breaks[1:])]

    def _which(self, x):
        # x がどの区間に入っているか
        idx = np.searchsorted(self.breaks, x, side="right") - 1
        return np.clip(idx, 0, len(self.pieces) - 1)

    def __call__(self, x, deriv=0):
        x = np.asarray(x, dtype=float)
        out = np.empty_like(x)
        idx = self._which(x)
        for i, p in enumerate(self.pieces):
            m = idx == i
            q = p.deriv(deriv) if deriv > 0 else p
            out[m] = q(x[m])
        return out


# ---------- 例1: |x - 0.3| (折れ目がノード上にない) ----------
def ex1():
    f = lambda x: np.abs(x - 0.3)
    a, b, kink = -1.0, 1.0, 0.3
    xt = np.linspace(a, b, 4001)
    Ns, e_single, e_spline = [], [], []
    for N in range(4, 129, 4):
        single = cheb_interp(f, a, b, N)              # ノード N+1 個
        spline = ChebSpline(f, [a, kink, b], N // 2)  # ノード 2*(N/2+1) ≒ 同数
        Ns.append(N + 1)
        e_single.append(np.max(np.abs(single(xt) - f(xt))))
        e_spline.append(np.max(np.abs(spline(xt) - f(xt))))
    return Ns, e_single, e_spline


# ---------- 例2: バミューダン的な価値関数 max(K-S, P_eu(S)) ----------
K, r, sig, T = 100.0, 0.05, 0.2, 1.0


def bs_put(S):
    d1 = (np.log(S / K) + (r + 0.5 * sig**2) * T) / (sig * np.sqrt(T))
    d2 = d1 - sig * np.sqrt(T)
    return K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)


def bs_put_delta(S):
    d1 = (np.log(S / K) + (r + 0.5 * sig**2) * T) / (sig * np.sqrt(T))
    return norm.cdf(d1) - 1.0


def V(S):
    """即時行使価値と継続価値(ここでは欧州プット)の max → 行使境界で折れる"""
    return np.maximum(K - S, bs_put(S))


def V_delta(S):
    return np.where(K - S > bs_put(S), -1.0, bs_put_delta(S))


def ex2():
    a, b = 50.0, 150.0
    S_star = brentq(lambda s: (K - s) - bs_put(s), 50.0, 99.0)  # 行使境界
    xt = np.linspace(a, b, 4001)
    xt_d = xt[np.abs(xt - S_star) > 1e-6]  # デルタは境界上で定義されないので除外
    rows = []
    for N in range(4, 129, 4):
        single = cheb_interp(V, a, b, N)
        spline = ChebSpline(V, [a, S_star, b], N // 2)
        rows.append((
            N + 1,
            np.max(np.abs(single(xt) - V(xt))),
            np.max(np.abs(spline(xt) - V(xt))),
            np.max(np.abs(single.deriv()(xt_d) - V_delta(xt_d))),
            np.max(np.abs(spline(xt_d, deriv=1) - V_delta(xt_d))),
        ))
    return S_star, np.array(rows)


if __name__ == "__main__":
    Ns, e1s, e1p = ex1()
    S_star, R = ex2()

    print("例1: |x-0.3|  (総ノード数, 1本, スプライン)")
    for n, s, p in list(zip(Ns, e1s, e1p))[::4]:
        print(f"  {n:4d}   {s:.2e}   {p:.2e}")

    print(f"\n例2: max(K-S, P_eu(S)), 行使境界 S* = {S_star:.4f}")
    print("  総ノード  価格:1本   価格:スプライン  デルタ:1本  デルタ:スプライン")
    for row in R[::4]:
        print(f"  {int(row[0]):6d}   {row[1]:.2e}   {row[2]:.2e}      {row[3]:.2e}   {row[4]:.2e}")

    fig, ax = plt.subplots(1, 3, figsize=(15, 4.3))
    ax[0].semilogy(Ns, e1s, "o-", label="single Chebyshev")
    ax[0].semilogy(Ns, e1p, "s-", label="Chebyshev spline (split at kink)")
    ax[0].set_title("Ex.1  f(x)=|x-0.3|")
    ax[1].semilogy(R[:, 0], R[:, 1], "o-", label="single Chebyshev")
    ax[1].semilogy(R[:, 0], R[:, 2], "s-", label="Chebyshev spline")
    ax[1].set_title("Ex.2  value  max(K-S, P_eu(S))")
    ax[2].semilogy(R[:, 0], R[:, 3], "o-", label="single Chebyshev")
    ax[2].semilogy(R[:, 0], R[:, 4], "s-", label="Chebyshev spline")
    ax[2].set_title("Ex.2  delta")
    for a_ in ax:
        a_.set_xlabel("total number of nodes")
        a_.set_ylabel("max error")
        a_.grid(True, which="both", alpha=0.3)
        a_.legend()
    plt.tight_layout()
    plt.savefig("cheb_spline_demo.png", dpi=130)
    print("\nsaved cheb_spline_demo.png")
