@def title = "Franklin Example"
@def tags = ["syntax", "code"]

<!-- ここで少し CSS を書いて、画像やテキストを整形する例を示します -->
<style>
.card {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 1rem;
  margin: 1rem 0;
  box-shadow: 0 4px 8px rgba(0,0,0,.1);
  max-width: 400px;    /* 適宜調整 */
  margin-left: auto;   /* カードを中央寄せ */
  margin-right: auto;
}

.card img {
  display: block;
  max-width: 100%;
  height: auto;
  margin: 0 auto;
  border-radius: 8px;
}

.card .caption {
  text-align: center;
  font-size: 0.9rem;
  margin-top: 0.5rem;
  color: #555;
}

.links {
  list-style: none;
  padding-left: 0;
  margin: 1rem 0;
}

.links li {
  margin: 0.3rem 0;
}

.links li a {
  text-decoration: none;
  color: #007acc;
}

.links li a:hover {
  text-decoration: underline;
}
</style>

<!-- 画像 + キャプション部分をカード風にまとめた例 -->
<div class="card">
  <img src="frog.jpg" alt="frog">
  <p class="caption">@TSUKUBA🐸 BREWERY</p>
</div>

## Me

<ul class="links">
  <li>
    <a 
      href="https://scholar.google.com/citations?hl=ja&authuser=1&user=IKqeswsAAAAJ" 
      target="_blank">
      Google Scholar
    </a>
  </li>
  <li>Email: sakurairihito(at)gmail.com</li>
  <li>
    <a 
      href="https://zenn.dev/rihitosakurai" 
      target="_blank">
      Tech blog (Zenn)
    </a>
  </li>
  <li>
    <a 
      href="https://sizu.me/sakurai" 
      target="_blank">
      Diary (しずかなインターネット)
    </a>
  </li>
  <li>
    <a
      href="https://github.com/sakurairihito/self-intro"
      target="_blank">
      Me
    </a>
  </li>
</ul>

<!-- もう一つの画像も同様に -->
<div class="card">
  <img src="cafe.jpg" alt="cafe">
  <p class="caption">Memory.</p>
</div>
