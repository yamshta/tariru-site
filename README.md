# tariru-site

TARIRU の公式 LP (`https://tariru.app/`)。GitHub Pages で配信。

主目的:
- App Store の マーケティング / サポート / プライバシー URL のホスト（現状の Notion ページを置き換える）
- 悩み起点のコンテンツ SEO（/journal/）

## 構成

```
.
├── index.html              # LP
├── support/index.html      # サポート + FAQ
├── privacy/index.html      # プライバシーポリシー
├── tips/index.html         # 使い方のコツ + よくある問い合わせ
├── journal/                # コンテンツ SEO 記事（hub: 家計簿続かない）
│   ├── index.html
│   └── <slug>/index.html
├── assets/
│   ├── og.png              # OG 画像（scripts/og_template.html から生成）
│   └── store/ja/*.png      # App Store スクショ（fastlane/screenshots/ja のコピー）
├── content/
│   ├── privacy.md          # プライバシーポリシー本文（SSoT）
│   └── ja/journal/*.md     # 記事本文（front matter + Markdown）
├── CNAME                   # tariru.app
└── scripts/
    ├── generate_pages.py   # 全ページ + sitemap/robots の一括生成（コピーの SSoT）
    └── og_template.html    # OG 画像の元 HTML
```

コピー / FAQ / tips を変更する場合は `scripts/generate_pages.py` の `LOCALES` dict を編集 →
`python3 scripts/generate_pages.py` で再生成。個別 HTML を直接編集しない（次回生成で上書きされる）。

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt   # 初回のみ
.venv/bin/python scripts/generate_pages.py
```

記事の追加は `content/ja/journal/<slug>.md` を置いて再生成（front matter: slug / title /
description / hub / spokes / updated）。

OG 画像の再生成（`scripts/og_template.html` を編集後）:

```bash
.venv/bin/pip install playwright   # 初回のみ
python3 -m http.server 8944 &
.venv/bin/python - <<'EOF'
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1200, "height": 630})
    pg.goto("http://127.0.0.1:8944/scripts/og_template.html")
    pg.wait_for_timeout(300)
    pg.screenshot(path="assets/og.png", clip={"x": 0, "y": 0, "width": 1200, "height": 630})
    b.close()
EOF
```

## App Store Connect URL マッピング（切替後）

| 項目 | URL |
|---|---|
| marketing_url | `https://tariru.app/` |
| support_url | `https://tariru.app/support/` |
| privacy_url | `https://tariru.app/privacy/` |

`TARIRU/fastlane/metadata/ja/{marketing_url,support_url,privacy_url}.txt` も合わせて更新すること。

## デプロイ手順（初回 owner 作業）

### 1. ドメイン

`tariru.app`（Cloudflare Registrar で登録済み）を使う。

### 2. GitHub Pages 設定

リポジトリ Settings → Pages:
- Source: `Deploy from a branch`
- Branch: `main` / root
- Custom domain: `tariru.app`
- **Enforce HTTPS** をオン（DNS 反映後）。`.app` TLD は HSTS preload 対象で
  ブラウザが HTTPS を強制するため、cert 発行前は表示できないのが正常

### 3. DNS 設定（Cloudflare）

Apex (`tariru.app`) を GitHub Pages の 4 つの A レコードに向ける。
**Proxy は OFF（灰色雲 / DNS only）** にすること（GitHub Pages の cert 発行を邪魔しない）:

```
A  185.199.108.153
A  185.199.109.153
A  185.199.110.153
A  185.199.111.153
```

`www` を使う場合は CNAME `yamshta.github.io.` を追加。

### 4. 反映確認

- `https://tariru.app/` が表示される
- `https://tariru.app/sitemap.xml` を Google Search Console に登録

## メンテナンス

- **スクショ更新**: `TARIRU/fastlane/screenshots/ja/*.png` を `assets/store/ja/` にコピー →
  `generate_pages.py` の `ASSET_VERSION` を上げて再生成
- **評価の更新**: `APP_RATING`（journal 記事の CTA に表示）。
  取得: `https://itunes.apple.com/lookup?id=6752897442&country=jp`
- **プライバシーポリシー改定**: `content/privacy.md` を編集 → 再生成。最終更新日も上げる

## TODO

- [x] GA4 web stream 作成済み（`G-5V8HE6R7MC`）
- [ ] サポート窓口（メール等）を決めて `contact_body` を差し替え
- [ ] App Store Connect の marketing / support / privacy URL を差し替え（fastlane metadata も）
- [ ] Google Search Console に sitemap 登録
