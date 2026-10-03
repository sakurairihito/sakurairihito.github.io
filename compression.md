@def title = "滑らかな価格曲面は、低ランクで近似できる？"
@def page_language = "ja"
@def hasmath = true
@def description = "Black–Scholesのオプション価格を株価とボラティリティの2変数で立体的に描き、SVDとmatrix cross interpolationで低ランク近似を試します。"

@@explainer

# 滑らかな価格曲面は、低ランクで近似できる？

@@article-lead
Black–Scholesの価格関数を、少数の成分で表してみる
@@

株価とボラティリティを変えると、オプション価格はどう変わるでしょうか。1資産のBlack–Scholesモデルで、ヨーロピアン・コールの価格を計算してみます。横の2軸は**現在の株価 $S$ とボラティリティ $\sigma$**、高さは**オプション価格 $C(S,\sigma)$**です。

~~~
<figure>
  <a href="/assets/compression/bs1d-surface.png">
    <img src="/assets/compression/bs1d-surface.png" alt="株価50から150、ボラティリティ5から60パーセントに対するコール価格の3D曲面。株価とボラティリティが大きくなるにつれて、価格が滑らかに上昇する。" width="1238" height="1316" fetchpriority="high">
  </a>
  <figcaption>図1：Black–Scholesの価格曲面。行使価格100、満期まで1年、年率金利3%、配当なし。図をクリックすると拡大できます。</figcaption>
</figure>
~~~

なめらかな一枚の曲面です。しかし、眺めただけでは、これが少数の成分に分けられるかどうかは分かりません。**この曲面を、少ない情報で近似できるでしょうか？**

## 2変数の関数を、行列として見る

株価を50〜150、ボラティリティを5〜60%の範囲で、それぞれ端点を含む128点の等間隔格子に取ります。全組合せで計算した価格は、次の行列になります。

$$
A_{ij}=C(S_i,\sigma_j),\qquad A\in\mathbb R^{128\times128}.
$$

つまり16,384個の価格です。ここでは、1資産という意味でモデルは「1d」ですが、変化させる入力は株価とボラティリティの2つです。

低ランク近似で探すのは、

$$
C(S_i,\sigma_j)\approx\sum_{\alpha=1}^{r}
 u_\alpha(S_i)v_\alpha(\sigma_j)
$$

という表現です。**株価だけの関数と、ボラティリティだけの関数の積を、少数足し合わせて曲面を表せるか**、という問いになります。これは単に「滑らかかどうか」とは別の性質です。

## 必要な成分数を調べる

まず行列全体を特異値分解（SVD）し、成分の大きさを調べます。大きい特異値に対応する成分から $r$ 個を残すと、この格子上でフロベニウス誤差が最小のランク $r$ 以下の近似が得られます。

~~~
<figure>
  <a href="/assets/compression/bs1d-rank.png">
    <img src="/assets/compression/bs1d-rank.png" alt="左は急速に減衰する価格行列の特異値。右はランクを増やしたときのSVDとMCIの相対誤差で、どちらも小さくなる。" width="2000" height="866" loading="lazy">
  </a>
  <figcaption>図2：左は最大値で規格化した特異値、右は低ランク近似の相対フロベニウス誤差。緑がSVD、橙が次節のMCI。縦軸は対数目盛です。</figcaption>
</figure>
~~~

この条件では、特異値は急速に小さくなっています。**ランク8のSVD近似で、相対誤差は約 $3.5\times10^{-6}$。** 曲面を格子点ごとに保存する代わりに、少数の分離した成分でよく近似できることが分かりました。

ここで相対誤差は、全格子点の誤差をまとめた

$$
\frac{\|A-\widehat A\|_F}{\|A\|_F}
$$

です。各点での相対誤差を保証する指標ではないため、後で最大絶対誤差も確認します。

## 少数の断面から、曲面を再構成する

次に、**matrix cross interpolation（行列クロス補間、MCI）**を使います。選んだボラティリティでの価格曲線と、選んだ株価での価格曲線を組み合わせ、全体を近似する方法です。[2]

選ぶ行・列の添字を $I,J$ とすると、

$$
\widehat A=A_{:,J}\,(A_{I,J})^{-1}\,A_{I,:}
$$

と書けます。交差部分 $A_{I,J}$ が正則であることが必要で、選び方や数値的な安定性が精度に関わります。実装では逆行列を作らず、線形方程式を解きます。

~~~
<figure>
  <a href="/assets/compression/bs1d-cross.png">
    <img src="/assets/compression/bs1d-cross.png" alt="上段は元の価格曲面とランク8のMCI近似を同じ軸で比較。下段は選んだ8行と8列、および全格子点の絶対誤差。最大絶対誤差は約0.0017。" width="1999" height="1710" loading="lazy">
  </a>
  <figcaption>図3：8行・8列から再構成した曲面は、元の曲面と見た目ではほぼ区別できません。左下の灰色部分は再構成に使わない要素です。右下は別の色尺度で誤差を拡大して示しています。</figcaption>
</figure>
~~~

| ランク $r$ | SVDの相対誤差 | MCIの相対誤差 | MCIの最大絶対誤差 |
| --- | --- | --- | --- |
| 1 | $1.10\times10^{-1}$ | $2.38\times10^{-1}$ | $17.4$ |
| 2 | $1.29\times10^{-2}$ | $4.00\times10^{-2}$ | $2.48$ |
| 4 | $6.98\times10^{-4}$ | $2.66\times10^{-3}$ | $0.327$ |
| 8 | $3.48\times10^{-6}$ | $1.04\times10^{-5}$ | $0.00167$ |
| 12 | $1.27\times10^{-8}$ | $6.07\times10^{-8}$ | $0.0000132$ |

ランク8のMCIでは、相対誤差は約 **0.0010%**、最大絶対誤差は価格の単位で約 **0.0017** でした。再構成に必要な行列要素は、交差部分の重複を除くと

$$
8\times(128+128)-8^2=1,984
$$

で、元の16,384要素の**約12.1%**です。添字などの付加情報はこの数に含めていません。

今回の説明用コードは、全格子点を計算し、残差が最大の点を順に探して行・列を選んでいます。1,984は選択後の再構成に使う要素数であり、「1,984回の価格計算だけで構築できた」という意味ではありません。

## この実験から分かること

**この範囲のBlack–Scholes価格曲面は、株価とボラティリティの間で低ランク近似できました。** 滑らかな見た目から予想するだけでなく、特異値と再構成誤差で確認した結果です。

必要なランクは、パラメータの範囲、満期までの時間、要求する精度によって変わります。ここで確かめたのは128×128の格子上の価格です。格子の間の値や、価格の微分であるGreeksの精度は別に検証する必要があります。

フーリエ展開も関数を成分に分ける方法ですが、ここでは株価とボラティリティへの依存性を分離しています。1変数の少数フーリエ成分から導くランクの議論とは区別して、実際の2変数関数で圧縮可能性を調べました。

Black–Scholesのコールには解析式があるため、この例の目的は価格計算の高速化ではなく、関数の圧縮を具体的に見ることです。この考え方を、多資産や多くのパラメータに依存する関数へ広げると、テンソルトレインによる表現につながります。[3]

## 計算式と再現用コード

価格には、配当なしのヨーロピアン・コールのBlack–Scholes式を使いました。[1]

$$
C(S,\sigma)=S\Phi(d_1)-Ke^{-r_f\tau}\Phi(d_2),
$$

$$
d_1=\frac{\log(S/K)+(r_f+\sigma^2/2)\tau}{\sigma\sqrt{\tau}},
\qquad d_2=d_1-\sigma\sqrt{\tau}.
$$

$\Phi$ は標準正規分布の累積分布関数、$K=100$、$r_f=0.03$、$\tau=1$ です。ボラティリティは計算では $0.05\leq\sigma\leq0.60$、図では%で表示しています。

[図を生成するPythonコード](/assets/scripts/bs1d_demo.py)と[特異値・誤差・選択点の数値データ](/assets/compression/bs1d-results.json)を公開しています。計算式は割引ペイオフの数値積分とも照合しています。

## 参考文献

1. M. Haugh, [The Black–Scholes Model](https://www.columbia.edu/~mh2078/FoundationsFE/BlackScholes.pdf), Columbia University, 2016.
2. Y. Núñez Fernández et al., [Learning tensor networks with tensor cross interpolation: New algorithms and libraries](https://scipost.org/10.21468/SciPostPhys.18.3.104), SciPost Phys. 18, 104 (2025). 第3節の行列クロス補間。
3. R. Sakurai, H. Takahashi, K. Miyamoto, [Learning parameter dependence for Fourier-based option pricing with tensor trains](https://www.mdpi.com/2227-7390/13/11/1828), Mathematics 13(11), 1828 (2025).

[ホームへ戻る](/)

@@
