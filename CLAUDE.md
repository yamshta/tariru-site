# CLAUDE.md

## このリポジトリについて

TARIRU 公式 LP（`https://tariru.app/`）。**public リポジトリ**で、GitHub Pages によって
リポジトリ内容がそのまま全世界に配信される。構成・編集方法は [README.md](README.md) を参照。

## 秘匿情報を絶対にコミットしない

このリポジトリは public かつ配信ルート。**コミット = 公開**である。
以下は理由の如何を問わずコミット禁止:

- **API キー・トークン・シークレット**（ASC API key, Firebase の秘密系キー, GA4 の
  Measurement Protocol api_secret 等）。※GA4 の Measurement ID (`G-XXXX`) は公開前提の値なので可
- **個人情報**（メールアドレス・電話番号・住所。サポート窓口を公開する場合も、専用の
  問い合わせフォームか専用アドレスにする）
- **実データのスクリーンショット**（`assets/store/` に置くのは App Store 提出版の
  モックデータのスクショのみ。実機の実残高・実取引が写ったものは不可）
- **売上・ダウンロード数などの非公開の実績値**（コメント内も含む）
- **`.env` / credential ファイル類**（そもそもこのリポジトリに置かない）

コミット前チェック: `git diff --cached` を必ず確認し、`git add -A` ではなく
ファイル名を明示して add する。

## 編集ルール

- 個別 HTML を直接編集しない。`scripts/generate_pages.py`（コピー）と `content/`（本文）が
  SSoT で、`python3 scripts/generate_pages.py` の再生成で上書きされる
- アプリの機能に言及するときは**リリース済みバージョンに含まれる機能のみ**書く
  （未リリース機能の記載は App Store の実物と食い違い、ユーザーを混乱させる）
- プライバシーポリシー（`content/privacy.md`）の記述はアプリの実装と一致させる。
  計測・送信まわりの記述を変えるときは TARIRU 本体の `AnalyticsService.swift` /
  `CrashlyticsService.swift` の実装を確認してから
