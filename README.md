### 概要説明

1. 画像を読み込み、グレースケールに変換して2値化し、細かいセルに分割する<br>
2. 全セルを迷路生成対象として、中央から再帰的バックトラック法（穴掘り法）で通路を掘る<br>
3. 元画像から各壁の中点の色をサンプリングし、白に近い場合は調整して迷路の壁として描画する<br>
4. 最終的に迷路画像として出力する<br>