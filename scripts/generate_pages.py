"""Generate LP / support / privacy / tips / journal pages for tariru-site.

Source of truth for copy:
- TARIRU/fastlane/metadata/ja/*.txt (App Store description / subtitle)
- TARIRU/docs (positioning: 記録しない「足りる？」判定)
- TARIRU/Utils/ModernCardDesign.swift (color tokens)

Output:
- /index.html, /support/index.html, /tips/index.html, /privacy/index.html
- /journal/index.html, /journal/<slug>/index.html
- /sitemap.xml, /robots.txt

ja-only for now. The LOCALES structure mirrors kuu-site so more locales can be
added later; single-locale mode hides the language switcher.
"""

import html as html_mod
import json
import re
from pathlib import Path

import markdown as md_lib
import yaml

ROOT = Path(__file__).resolve().parent.parent
APP_STORE_ID = "6752897442"
# installUrl(構造化データ)は国コードなし canonical。CTA リンクは国コード付き。
APP_STORE_URL = f"https://apps.apple.com/app/id{APP_STORE_ID}"
APP_STORE_COUNTRY = {"ja": "jp"}


def app_store_cta_url(code):
    country = APP_STORE_COUNTRY[code]
    return f"https://apps.apple.com/{country}/app/id{APP_STORE_ID}"


BASE_URL = "https://tariru.app"
OG_IMAGE = f"{BASE_URL}/assets/og.png"
# App Store の実評価 (社会的証明として journal 記事の CTA に表示)。
# 取得元: https://itunes.apple.com/lookup?id=6752897442&country=jp — 定期的に手動で更新する。
APP_RATING = {"score": "4.6", "count": 21}
# assets のキャッシュ回避クエリ。画像を差し替えたら日付を上げる。
ASSET_VERSION = "20260705"
# GA4 web stream measurement ID (G-XXXXXXXXXX). Empty = no analytics tag emitted.
# Stream: properties/506107058/dataStreams/15202507699 (tariru.app)
GA4_MEASUREMENT_ID = "G-5V8HE6R7MC"
PRIVACY_LOCALES = ("ja",)
TIPS_LOCALES = ("ja",)
JOURNAL_LOCALES = ("ja",)
SCREENSHOT_COUNT = 10

LOCALES = {
    "ja": {
        "subdir": "",
        "html_lang": "ja",
        "og_locale": "ja_JP",
        "label": "日本語",
        "title": "TARIRU — 今月の支払い、足りる？をひと目で判定",
        "description": "TARIRU は、口座残高と支払い予定から「今月、足りる？」だけをシンプルに判定する iOS アプリ。銀行連携なし、1円単位の記録も不要。家計簿が続かなくても大丈夫。",
        # Hero
        "hero_headline": "今月の支払い、足りる？",
        "hero_sub": "口座残高と支払い予定を入れるだけ。1円単位の家計簿は、もうつけなくていい。",
        "cta": "App Store で入手",
        "scroll_cue": "下へ",
        # Hero verdict card (the TARIRU signature)
        "verdict_label_suffix": "の支払いに",
        "verdict_answer": "足りる",
        "verdict_amount": "余裕 +¥23,456",
        "verdict_caption": "残高 ¥186,240 ・ 支払い予定 ¥162,784",
        # Why
        "why_eyebrow": "なぜ TARIRU か",
        "why_headline": "給料日前、口座残高を何度も確認していませんか。",
        "why_scenario": "引き落とし日が近づくと、なんとなくソワソワする。残高を見ても、このあといくら出ていくのかまでは分からない。",
        "why_lead": "それは、あなたがだらしないからではありません。1円単位の家計簿を毎日つけ続けるほうが、ずっと大変なこと。",
        "thoughts": [
            "月末の引き落としが気になって、つい口座を見てしまう",
            "口座もカードも複数あって、全体像がつかめない",
            "家計簿アプリは何度も入れたけど、続かなかった",
            "レシートを撮るのも、つけ忘れを埋めるのも疲れた",
            "完璧な記録より「足りるかどうか」だけ知りたい",
        ],
        "why_note": "本当に知りたいのは、たったひとつ。「今月の支払い、足りる？」——TARIRU は、その答えだけをシンプルに出します。",
        # How
        "steps_eyebrow": "使い方",
        "steps_headline": "やることは、3つだけ。",
        "steps": [
            ("残高を入れる", "口座の残高をそのまま入力。銀行連携も、ID・パスワードの入力も要りません。"),
            ("予定を登録する", "家賃やカードの引き落とし、給料などの予定を登録。毎月の分は一度設定すれば自動で作られます。"),
            ("足りるか、見る", "残高と予定から自動計算。余裕があるか、足りないかが、ひと目でわかります。"),
        ],
        # App showcase
        "app_eyebrow": "アプリ",
        "app_headline": "これが、TARIRU。",
        "screen_alt": "TARIRU の画面",
        # Features (4-up grid)
        "features_eyebrow": "できること",
        "features_headline": "がんばらないのに、ちゃんと見える。",
        "features_lead": "記録が目的のアプリではありません。「足りるか」に必要なものだけ。",
        "features": [
            ("足りるかの判定", "残高と予定収支から自動計算。余裕額・不足額がひと目でわかります。"),
            ("口座もカードも、ひとつに", "銀行口座・現金・クレジットカード・口座振替をまとめて一画面で。"),
            ("毎月の収支は自動で", "給与・家賃・サブスクは一度設定すれば、毎月自動で登録されます。"),
            ("iCloud で安心", "データは自動でバックアップ・同期。機種変更しても、そのまま使えます。"),
        ],
        "features_aria": "TARIRU の主な機能",
        # Privacy
        "privacy_eyebrow": "プライバシー",
        "privacy_headline": "あなたのお金の情報は、外に出ない。",
        "privacy_body": "銀行やカード会社との連携はありません。あなたが入力した情報は、あなたの iPhone と、あなただけがアクセスできる iCloud にだけ保存されます。開発者のサーバーはありません。",
        # Closing
        "closing_headline": "月末のソワソワを、「今月も大丈夫」に。",
        "closing_sub": "毎日開かなくていい。給料日と引き落とし日の前に、確認するだけ。",
        # Footer
        "support_label": "サポート",
        "privacy_label": "プライバシー",
        "lang_switcher_aria": "言語",
        # Support page
        "support_title": "サポート — TARIRU",
        "support_description": "TARIRU のサポートに関するお問い合わせ先と FAQ。",
        "support_h1": "サポート",
        "support_intro": "TARIRU をご利用いただきありがとうございます。ご不明な点や不具合のご報告は、下記までご連絡ください。",
        "contact_h2": "お問い合わせ",
        "contact_body": "サポート窓口は近日公開予定です。",
        "faq_h2": "よくある質問",
        "faqs": [
            (
                "銀行口座やクレジットカードと連携しますか？",
                "いいえ。外部サービスとの連携は一切ありません。口座やカードの情報はあなた自身が入力するもので、ID・パスワードを預けることもありません。だからこそ、初期設定は数分で終わります。",
            ),
            (
                "データはどこに保存されますか？",
                "あなたの iPhone の中と、あなただけがアクセスできる iCloud（プライベートデータベース）です。開発者が運営するサーバーはなく、入力した金額が外部に送信されることはありません。",
            ),
            (
                "機種変更したらデータは引き継げますか？",
                "はい。同じ Apple ID で iCloud にサインインすれば、新しい iPhone に自動で同期されます。",
            ),
            (
                "無料でどこまで使えますか？",
                "口座 2 つ・カード 1 枚・定期取引 3 件まで無料で使えます。それ以上使いたい場合は、買い切りのフルアクセス（サブスクリプションではありません）を一度だけ購入すれば、すべて無制限になります。",
            ),
            (
                "家計簿アプリと何が違いますか？",
                "TARIRU は支出の記録が目的ではなく、「今月の支払いに足りるか」の判定が目的です。1円単位でつけ続けなくても、残高と予定さえ入っていれば機能します。数日サボっても、残高を入れ直すだけで元に戻ります。",
            ),
        ],
        # Tips / usage page
        "tips_title": "使い方のコツ — TARIRU",
        "tips_description": "TARIRU を「ざっくりでも回る」ように使うコツ。残高のリセット、クレジットカードの締め日設定、ウィジェットなどをまとめました。",
        "tips_eyebrow": "使い方のコツ",
        "tips_h1": "ざっくりでも、ちゃんと回る。",
        "tips_lead": "TARIRU は毎日つけなくても崩れないように作っています。知っておくと便利な操作と、よくある質問をまとめました。",
        "tips_screens": [
            {
                "heading": "ホームで",
                "lead": "「足りる？」の答えが出る画面。確認は数秒で終わります。",
                "groups": [
                    {
                        "items": [
                            ("タップ", "口座カードから残高を入れ直す", "実際の残高とズレてきたら、口座カードをタップして今の残高を上書きするだけ。数日サボっても、これだけでまた正しく判定できます。"),
                            ("ウィジェット", "ホーム画面に「足りる？」を置く", "ウィジェットを追加すると、アプリを開かずに今期の資金状態を確認できます。"),
                        ],
                    },
                ],
            },
            {
                "heading": "入力で",
                "lead": "支払いや収入の登録は、なるべく手数が少なく。",
                "groups": [
                    {
                        "items": [
                            ("電卓", "金額欄でそのまま計算する", "金額の入力中に + − × ÷ が使えます。「家賃と駐車場を合わせて」も、電卓アプリに切り替えずその場で計算できます。"),
                            ("メモ", "支払いや収入にメモを残す", "あとで見返して「これ何の支払いだっけ？」とならないよう、ひとことメモを添えられます。"),
                            ("定期取引", "毎月の分は一度だけ設定する", "給与・家賃・サブスクなど毎月決まった収支は、定期取引にすると自動で登録されます。毎月手で入れるのは、変動する分だけ。"),
                        ],
                    },
                ],
            },
            {
                "heading": "設定で",
                "lead": "自分の生活に合わせて、静かに調整。",
                "groups": [
                    {
                        "items": [
                            ("カレンダー", "週の始まりを日曜 / 月曜で切り替える", "カレンダーの週の始まりを、使い慣れたほうに合わせられます。"),
                            ("Face ID", "アプリにロックをかける", "Face ID / Touch ID でアプリをロックできます。お金の情報を、のぞき見から守ります。"),
                            ("計算除外", "貯金用の口座を判定から外す", "「使わないと決めている口座」は足りるかの計算から除外できます。判定は、生活に使う口座だけで。"),
                        ],
                    },
                ],
            },
        ],
        "tips_note": "TARIRU は「完璧に記録すること」を求めません。ズレたら残高を入れ直す——それだけで回るように作っています。",
        "tips_closing_sub": "まだ TARIRU を試していなければ、こちらから。",
        "tips_label": "使い方のコツ",
        # 不満ベースのよくある問い合わせ（可視セクション + FAQPage 構造化データで共用）
        "tips_faq_heading": "よくある問い合わせ",
        # answer は「文（。）ごとの行」リスト。可視は 1 行 = 1 段落で余白を出し、
        # FAQPage 構造化データは "".join で 1 文に戻す。
        "tips_faqs": [
            (
                "残高が実際とズレてきた。",
                [
                    "TARIRU はざっくり運用が前提なので、ズレるのは想定内です。",
                    "口座カードをタップして、今の残高を入れ直すだけでリセットできます。",
                    "つけ忘れた支出を遡って埋める必要はありません。",
                ],
            ),
            (
                "クレジットカードの扱いがよく分からない。",
                [
                    "カードに「締め日」と「引き落とし日」を設定すると、利用分が引き落とし日の支払いとしてまとまります。",
                    "口座からお金が出ていく日ベースで見るので、「その日に足りるか」の判定に直結します。",
                ],
            ),
            (
                "毎日開くのが面倒。",
                [
                    "毎日開かなくて大丈夫です。",
                    "給料日と引き落とし日の前に、残高と予定を確認するだけで機能します。",
                    "ウィジェットを置けば、開く回数はさらに減らせます。",
                ],
            ),
        ],
        "tips_support_before": "残高のリセットやクレジットカードの設定など、つまずきやすいポイントは",
        "tips_support_after": "にまとめています。",
        "back": "← トップへ",
        # Journal (content SEO articles): 悩み起点、TARIRU-first にしない。
        "journal_eyebrow": "読みもの",
        "journal_hub_title": "読みもの — TARIRU",
        "journal_hub_description": "給料日前の不安や、続かない家計簿との付き合い方。お金の「見える化」をがんばらずに済ませるヒント。",
        "journal_hub_lead": "お金の不安を、がんばらずに軽くするためのヒント。",
        "journal_updated_label": "更新:",
        "journal_pitch_headline": "「今月、足りる？」だけ分かればいい。",
        "journal_pitch_body": "TARIRU は、口座残高と支払い予定から「足りるか」だけをシンプルに判定する iOS アプリです。記録はざっくりでいい。銀行連携もありません。",
        "journal_pitch_note": "無料でダウンロードできます。",
        "journal_rating_suffix": "件の評価",
        "journal_related_label": "あわせて読みたい",
        "journal_back_label": "読みものへ戻る",
    },
}

# TARIRU palette — sourced from TARIRU/Utils/ModernCardDesign.swift (the app's design tokens).
BASE_CSS = """\
:root {
  color-scheme: light;
  --bg: #faf8f8;
  --surface: #ffffff;
  --surface-quiet: #f2f2f4;
  --ink: #282a26;
  --ink-soft: #828480;
  --ink-faint: #adadab;
  --primary: #347255;
  --primary-bright: #2e9e63;
  --primary-soft: #d4e8db;
  --coral: #cb5b51;
  --coral-soft: #f5dad6;
  --line: #eaeaed;
  --f-green: #347255;
  --f-blue: #405c8c;
  --f-mustard: #b9a03c;
  --f-purple: #8c59a6;
}
* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
  margin: 0;
  padding: 0;
  background: var(--bg);
  color: var(--ink);
  font-family: -apple-system, BlinkMacSystemFont, "Hiragino Sans", "Helvetica Neue", Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  text-rendering: optimizeLegibility;
  line-height: 1.7;
  /* CJK 句読点 (、。) を proportional alternate で詰め組み。 */
  font-feature-settings: "palt" 1, "kern" 1;
  font-kerning: normal;
}
.wrap { max-width: 660px; margin: 0 auto; padding: 0 24px; }
section { padding: clamp(64px, 13vw, 132px) 0; }

/* ---- hero ---- */
.hero {
  min-height: 100svh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: clamp(48px, 10vw, 96px) 24px clamp(40px, 8vw, 72px);
  position: relative;
}
.wordmark {
  font-size: 15px;
  font-weight: 700;
  letter-spacing: 0.42em;
  color: var(--primary);
  margin: 0 0 clamp(24px, 5vw, 40px) 0.42em;
}
.hero h1 {
  font-size: clamp(30px, 7vw, 46px);
  font-weight: 700;
  letter-spacing: 0.01em;
  line-height: 1.35;
  margin: 0;
}
.hero .sub {
  color: var(--ink-soft);
  font-size: clamp(15px, 4vw, 17px);
  max-width: 30em;
  margin: clamp(16px, 4vw, 22px) auto 0;
}

/* ---- verdict card (the TARIRU signature) ---- */
.verdict {
  width: min(88vw, 340px);
  margin: clamp(36px, 8vw, 60px) auto 0;
  padding: 26px 28px 24px;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 24px;
  box-shadow: 0 30px 64px -30px rgba(52, 114, 85, 0.45), inset 0 1px 0 rgba(255, 255, 255, 0.9);
  text-align: left;
}
.verdict-label { margin: 0; font-size: 13px; font-weight: 600; color: var(--ink-soft); }
.verdict-answer {
  margin: 6px 0 0;
  font-size: 34px;
  font-weight: 700;
  line-height: 1.2;
  color: var(--primary);
  display: flex;
  align-items: center;
  gap: 10px;
}
.verdict-answer::before {
  content: "";
  flex: none;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: var(--primary-soft);
  /* チェックマーク */
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23347255' stroke-width='3.2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M5 12.5l4.5 4.5L19 7.5'/%3E%3C/svg%3E");
  background-size: 16px;
  background-position: center;
  background-repeat: no-repeat;
}
.verdict-amount {
  margin: 4px 0 0;
  font-family: ui-monospace, "SF Mono", SFMono-Regular, Menlo, monospace;
  font-size: 15px;
  font-weight: 600;
  color: var(--primary-bright);
}
.verdict-bar {
  margin-top: 18px;
  height: 8px;
  border-radius: 999px;
  background: var(--surface-quiet);
  overflow: hidden;
}
.verdict-fill {
  display: block;
  height: 100%;
  width: 87.4%;
  border-radius: 999px;
  background: linear-gradient(90deg, var(--primary), var(--primary-bright));
}
.js .verdict-fill { width: 0; transition: width 1.1s 0.7s cubic-bezier(0.22, 0.61, 0.36, 1); }
.js .verdict.in .verdict-fill { width: 87.4%; }
.verdict-caption {
  margin: 10px 0 0;
  font-family: ui-monospace, "SF Mono", SFMono-Regular, Menlo, monospace;
  font-size: 11.5px;
  color: var(--ink-faint);
}

/* ---- cta ---- */
.cta {
  display: inline-block;
  margin-top: clamp(28px, 6vw, 40px);
  padding: 15px 30px;
  background: var(--primary);
  color: #fff;
  border-radius: 999px;
  text-decoration: none;
  font-weight: 600;
  font-size: 15px;
  letter-spacing: 0.02em;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.cta:hover { transform: translateY(-1px); box-shadow: 0 10px 24px -12px rgba(52, 114, 85, 0.6); }
.scroll-cue {
  margin-top: clamp(36px, 8vw, 64px);
  font-size: 11px;
  letter-spacing: 0.3em;
  color: var(--ink-faint);
  writing-mode: vertical-rl;
  animation: cue 2.4s ease-in-out infinite;
}
@keyframes cue {
  0%, 100% { transform: translateY(0); opacity: 0.5; }
  50% { transform: translateY(6px); opacity: 1; }
}

/* ---- shared section type ---- */
.eyebrow {
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.24em;
  color: var(--primary);
  text-transform: uppercase;
  margin: 0 0 14px;
}
h2 {
  font-size: clamp(22px, 5.2vw, 30px);
  font-weight: 700;
  line-height: 1.45;
  letter-spacing: 0.01em;
  margin: 0;
}
.lead { color: var(--ink-soft); font-size: clamp(15px, 4vw, 16px); margin: 16px 0 0; }
.scenario { color: var(--ink); font-size: clamp(16px, 4.4vw, 18px); line-height: 1.7; margin: 18px 0 0; }

/* ---- why: thought list ---- */
.thoughts { list-style: none; padding: 0; margin: 32px 0 0; }
.thoughts li {
  position: relative;
  padding: 14px 0 14px 26px;
  color: var(--ink);
  font-size: clamp(15px, 4vw, 16px);
  border-top: 1px solid var(--line);
}
.thoughts li:last-child { border-bottom: 1px solid var(--line); }
.thoughts li::before {
  content: "";
  position: absolute;
  left: 2px;
  top: 50%;
  width: 8px;
  height: 8px;
  margin-top: -4px;
  border-radius: 50%;
  background: var(--primary-soft);
}
.note {
  margin: 30px 0 0;
  padding: 22px 24px;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 18px;
  color: var(--ink-soft);
  font-size: clamp(15px, 4vw, 16px);
}

/* ---- steps ---- */
.steps { display: grid; gap: 16px; margin-top: 36px; }
.step {
  display: flex;
  gap: 18px;
  align-items: flex-start;
  padding: 22px 24px;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 18px;
}
.step .n {
  flex: none;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: var(--primary-soft);
  color: var(--primary);
  font-weight: 700;
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.step h3 { margin: 0 0 4px; font-size: 17px; font-weight: 600; }
.step p { margin: 0; color: var(--ink-soft); font-size: 15px; }

/* ---- app showcase (App Store style gallery) ---- */
.app .wrap { margin-bottom: 4px; }
.showcase {
  display: flex;
  gap: 18px;
  margin-top: 28px;
  overflow-x: auto;
  scroll-snap-type: x mandatory;
  padding: 6px max(24px, calc((100vw - 660px) / 2)) 10px;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none;
  cursor: grab;
}
.showcase::-webkit-scrollbar { display: none; }
.shot {
  flex: 0 0 auto;
  width: min(64vw, 272px);
  height: auto;
  display: block;
  border-radius: 28px;
  border: 1px solid var(--line);
  box-shadow: 0 26px 54px -30px rgba(40, 42, 38, 0.4);
  background: var(--surface);
  scroll-snap-align: center;
}

/* ---- features (4-up grid) ---- */
.features {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
  margin-top: 36px;
}
@media (max-width: 480px) { .features { grid-template-columns: 1fr; } }
.f {
  padding: 22px 20px;
  border-radius: 20px;
  background:
    linear-gradient(180deg,
      color-mix(in srgb, var(--f, var(--primary)) 8%, #fff),
      color-mix(in srgb, var(--f, var(--primary)) 18%, #fff));
  border: 1px solid color-mix(in srgb, var(--f, var(--primary)) 20%, var(--line));
}
.f strong { display: block; color: color-mix(in srgb, var(--f, var(--primary)) 85%, #000); font-size: 16px; font-weight: 700; margin-bottom: 6px; }
.f span { color: var(--ink-soft); font-size: 13.5px; line-height: 1.6; }

/* ---- privacy ---- */
.privacy { text-align: center; }
.privacy .lead { max-width: 30em; margin-left: auto; margin-right: auto; }

/* ---- closing ---- */
.closing { text-align: center; padding-bottom: clamp(40px, 9vw, 80px); }
.closing h2 { font-size: clamp(24px, 6vw, 34px); }
.closing .sub { color: var(--ink-soft); margin: 14px 0 0; font-size: clamp(15px, 4vw, 17px); }

/* ---- footer ---- */
footer {
  border-top: 1px solid var(--line);
  font-size: 13px;
  color: var(--ink-soft);
  padding: 40px 0 56px;
}
.footer-row { display: flex; gap: 20px; flex-wrap: wrap; align-items: center; }
.footer-row a { color: var(--ink-soft); text-decoration: none; }
.footer-row a:hover { text-decoration: underline; }

/* ---- scroll reveal (progressive enhancement) ---- */
.js .reveal { opacity: 0; transform: translateY(22px); transition: opacity 0.8s cubic-bezier(0.22, 0.61, 0.36, 1), transform 0.8s cubic-bezier(0.22, 0.61, 0.36, 1); }
.js .reveal.in { opacity: 1; transform: none; }

/* staggered reveal: children settle in one after another */
.js .reveal .stagger > * { opacity: 0; transform: translateY(14px); transition: opacity 0.6s cubic-bezier(0.22, 0.61, 0.36, 1), transform 0.6s cubic-bezier(0.22, 0.61, 0.36, 1); }
.js .reveal.in .stagger > * { opacity: 1; transform: none; }
.js .reveal.in .stagger > *:nth-child(2) { transition-delay: 0.07s; }
.js .reveal.in .stagger > *:nth-child(3) { transition-delay: 0.14s; }
.js .reveal.in .stagger > *:nth-child(4) { transition-delay: 0.21s; }
.js .reveal.in .stagger > *:nth-child(5) { transition-delay: 0.28s; }
.js .reveal.in .stagger > *:nth-child(6) { transition-delay: 0.35s; }

/* hero entrance on first load */
.js .hero .wordmark { animation: enter 0.8s 0.05s both cubic-bezier(0.22, 0.61, 0.36, 1); }
.js .hero h1 { animation: enter 0.8s 0.16s both cubic-bezier(0.22, 0.61, 0.36, 1); }
.js .hero .sub { animation: enter 0.8s 0.28s both cubic-bezier(0.22, 0.61, 0.36, 1); }
.js .hero .verdict { animation: enter 1s 0.4s both cubic-bezier(0.22, 0.61, 0.36, 1); }
.js .hero .cta { animation: enter 0.8s 0.58s both cubic-bezier(0.22, 0.61, 0.36, 1); }
@keyframes enter { from { opacity: 0; transform: translateY(18px); } to { opacity: 1; transform: none; } }

@media (prefers-reduced-motion: reduce) {
  html { scroll-behavior: auto; }
  .scroll-cue { animation: none; }
  .js .hero .wordmark, .js .hero h1, .js .hero .sub, .js .hero .verdict, .js .hero .cta { animation: none; }
  .js .reveal, .js .reveal .stagger > * { opacity: 1; transform: none; transition: none; }
  .js .verdict-fill { width: 87.4%; transition: none; }
}
"""

REVEAL_SCRIPT = """\
<script>
  document.documentElement.classList.add('js');
  addEventListener('DOMContentLoaded', function () {
    // 判定カードの「今月」を実際の月に差し替え（静的サイトの鮮度演出）
    var month = document.querySelector('.verdict-month');
    if (month) month.textContent = (new Date().getMonth() + 1) + '月';
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
      });
    }, { threshold: 0.16 });
    document.querySelectorAll('.reveal, .verdict').forEach(function (el) { io.observe(el); });
  });
</script>
"""

# Tips page reveal: sections are tall, so a 16% threshold never fires for the first
# section within the initial viewport → it stayed hidden until scroll (blank first view).
# threshold 0 + slight bottom rootMargin: reveal as soon as any part enters.
TIPS_REVEAL_SCRIPT = """\
<script>
  document.documentElement.classList.add('js');
  addEventListener('DOMContentLoaded', function () {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
      });
    }, { threshold: 0, rootMargin: '0px 0px -8% 0px' });
    document.querySelectorAll('.reveal').forEach(function (el) { io.observe(el); });
  });
</script>
"""

# Horizontal shot galleries (.showcase / .pitch-shots) scroll natively via touch/trackpad,
# but a plain mouse has no way to drag them — this adds click-and-drag for mouse only.
# Uses classic mouse events (not Pointer Events): a scrollable + scroll-snap element makes
# Chromium hijack the pointer capture as a native pan gesture and fire pointercancel instead
# of pointerup mid-drag, snapping the scroll back to 0. Plain mousemove/mouseup on document
# isn't subject to that native takeover and keeps tracking past the element's edge.
DRAG_SCROLL_SCRIPT = """\
<script>
  document.querySelectorAll('.showcase, .pitch-shots').forEach(function (el) {
    var down = false, startX = 0, startScroll = 0, raf = null, lastX = 0;
    function apply() {
      raf = null;
      el.scrollLeft = startScroll - (lastX - startX);
    }
    el.addEventListener('mousedown', function (e) {
      down = true;
      startX = lastX = e.clientX;
      startScroll = el.scrollLeft;
      el.style.scrollSnapType = 'none';
      el.style.cursor = 'grabbing';
      e.preventDefault();
    });
    document.addEventListener('mousemove', function (e) {
      if (!down) return;
      lastX = e.clientX;
      if (raf == null) raf = requestAnimationFrame(apply);
    });
    document.addEventListener('mouseup', function () {
      if (!down) return;
      down = false;
      el.style.cursor = '';
      el.style.scrollSnapType = '';
    });
  });
</script>
"""

SUPPORT_CSS = """\
:root {
  color-scheme: light;
  --bg: #faf8f8;
  --ink: #282a26;
  --ink-soft: #828480;
  --line: #eaeaed;
}
body {
  margin: 0;
  background: var(--bg);
  color: var(--ink);
  font-family: -apple-system, BlinkMacSystemFont, "Hiragino Sans", "Helvetica Neue", Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
}
main {
  max-width: 640px;
  margin: 0 auto;
  padding: clamp(48px, 10vw, 96px) 24px 80px;
}
h1 { font-size: 28px; font-weight: 700; margin: 0 0 24px; }
h2 { font-size: 18px; font-weight: 600; margin: 32px 0 8px; }
p { line-height: 1.7; color: var(--ink-soft); margin: 0 0 12px; }
a { color: var(--ink); }
.back {
  display: inline-block;
  margin-top: 48px;
  padding-top: 24px;
  border-top: 1px solid var(--line);
  color: var(--ink-soft);
  text-decoration: none;
  font-size: 14px;
}
"""

# Journal (content SEO article + hub) pages: long-form reading layout on top of SUPPORT_CSS,
# plus the LP's pill CTA and a card grid for the /journal/ hub listing.
JOURNAL_CSS = SUPPORT_CSS + """\
:root {
  --primary: #347255;
  --primary-bright: #2e9e63;
  --primary-soft: #d4e8db;
}
main { max-width: 680px; }
.eyebrow {
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.2em;
  color: var(--primary);
  text-transform: uppercase;
  margin: 0 0 14px;
}
h1 { line-height: 1.4; }
.updated { font-size: 13px; color: var(--ink-soft); margin: 0 0 32px; }
article h2 { font-size: 20px; margin: 40px 0 12px; }
article h3 { font-size: 16px; margin: 24px 0 8px; }
article p { line-height: 1.9; }
article ul, article ol { line-height: 1.9; color: var(--ink-soft); padding-left: 1.4em; margin: 0 0 16px; }
article li { margin: 4px 0; }
.cta {
  display: inline-block;
  margin-top: 18px;
  padding: 15px 34px;
  background: var(--primary);
  color: #fff;
  border-radius: 999px;
  text-decoration: none;
  font-weight: 600;
  font-size: 16px;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.cta:hover { transform: translateY(-1px); box-shadow: 0 10px 24px -12px rgba(52, 114, 85, 0.6); }
.app-pitch {
  margin-top: 48px;
  padding: 32px 28px;
  background: #fff;
  border: 1px solid var(--line);
  border-radius: 18px;
  text-align: center;
}
.app-pitch h2 { margin-top: 0; font-size: 19px; }
.app-pitch p { color: var(--ink-soft); }
.pitch-shots {
  display: flex;
  gap: 14px;
  margin: 0 0 16px;
  overflow-x: auto;
  scroll-snap-type: x mandatory;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none;
  cursor: grab;
}
.pitch-shots::-webkit-scrollbar { display: none; }
.pitch-shot {
  flex: 0 0 auto;
  width: min(48vw, 180px);
  height: auto;
  display: block;
  border-radius: 20px;
  border: 1px solid var(--line);
  box-shadow: 0 16px 32px -20px rgba(40, 42, 38, 0.4);
  scroll-snap-align: start;
}
.rating {
  font-size: 13px;
  font-weight: 600;
  color: var(--primary);
  margin: 0 0 16px;
}
.rating .rating-count { font-weight: 400; color: var(--ink-soft); }
.app-pitch .note { margin: 12px 0 0; font-size: 13px; color: var(--ink-soft); }
.related {
  margin-top: 40px;
  padding-top: 24px;
  border-top: 1px solid var(--line);
}
.related h2 { font-size: 13px; text-transform: uppercase; letter-spacing: 0.08em; color: var(--ink-soft); margin: 0 0 12px; }
.related ul { list-style: none; padding: 0; margin: 0; }
.related li { margin: 8px 0; }
.footer-links { display: flex; gap: 20px; margin-top: 24px; font-size: 13px; }
.footer-links a { color: var(--ink-soft); text-decoration: none; }
.footer-links a:hover { text-decoration: underline; }
.cards { list-style: none; padding: 0; margin: 32px 0 0; display: grid; gap: 16px; }
.card { border: 1px solid var(--line); border-radius: 16px; background: #fff; }
.card a { display: block; padding: 20px 22px; text-decoration: none; color: inherit; }
.card h2 { margin: 0 0 6px; font-size: 17px; }
.card p { margin: 0; font-size: 14px; color: var(--ink-soft); }
"""

# Tips page: lighter than the LP, card-per-tip. Tokens mirror ModernCardDesign.
TIPS_CSS = """\
:root {
  color-scheme: light;
  --bg: #faf8f8;
  --surface: #ffffff;
  --surface-quiet: #f2f2f4;
  --ink: #282a26;
  --ink-soft: #828480;
  --ink-faint: #adadab;
  --primary: #347255;
  --primary-soft: #d4e8db;
  --line: #eaeaed;
}
* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
  margin: 0;
  padding: 0;
  background: var(--bg);
  color: var(--ink);
  font-family: -apple-system, BlinkMacSystemFont, "Hiragino Sans", "Helvetica Neue", Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  text-rendering: optimizeLegibility;
  line-height: 1.7;
  font-feature-settings: "palt" 1, "kern" 1;
  font-kerning: normal;
}
.wrap { max-width: 660px; margin: 0 auto; padding: 0 24px; }

/* ---- header ---- */
.tips-hero { text-align: center; padding: clamp(40px, 8vw, 64px) 24px clamp(4px, 3vw, 14px); }
.wordmark {
  font-size: 15px;
  font-weight: 700;
  letter-spacing: 0.42em;
  color: var(--primary);
  margin: 0 0 clamp(14px, 3vw, 22px) 0.42em;
}
.eyebrow {
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.24em;
  color: var(--primary);
  text-transform: uppercase;
  margin: 0 0 14px;
}
.tips-hero h1 {
  font-size: clamp(26px, 6vw, 38px);
  font-weight: 700;
  line-height: 1.4;
  letter-spacing: 0.01em;
  margin: 0;
}
.tips-hero .lead { color: var(--ink-soft); font-size: clamp(15px, 4vw, 16px); max-width: 32em; margin: 16px auto 0; }

/* ---- screen sections ---- */
.screen { padding: clamp(44px, 9vw, 68px) 0 0; }
.screen h2 { font-size: clamp(20px, 5vw, 25px); font-weight: 700; line-height: 1.45; margin: 0; }
.screen .screen-lead { color: var(--ink-soft); font-size: clamp(14px, 3.8vw, 15px); margin: 10px 0 0; max-width: 32em; }
.subhead {
  font-size: 13px;
  font-weight: 600;
  letter-spacing: 0.04em;
  color: var(--primary);
  margin: 22px 0 0;
}
.tips + .subhead { margin-top: clamp(40px, 8vw, 56px); }

/* ---- tip cards ---- */
.tips { display: grid; gap: 14px; margin-top: 18px; }
.tip {
  padding: 20px 22px;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 18px;
}
.tip .badge {
  display: inline-block;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.02em;
  color: var(--primary);
  background: var(--primary-soft);
  padding: 4px 12px;
  border-radius: 999px;
  margin-bottom: 11px;
}
.tip h3 { margin: 0 0 6px; font-size: 16.5px; font-weight: 600; color: var(--ink); }
.tip p { margin: 0; color: var(--ink-soft); font-size: 14.5px; line-height: 1.72; }

/* ---- note ---- */
.note {
  margin: clamp(40px, 8vw, 64px) 0 0;
  padding: 22px 24px;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 18px;
  color: var(--ink-soft);
  font-size: clamp(15px, 4vw, 16px);
}

/* ---- FAQ (よくある問い合わせ) ---- */
.faq { padding: clamp(44px, 9vw, 68px) 0 0; }
.faq h2 { font-size: clamp(20px, 5vw, 25px); font-weight: 700; line-height: 1.45; margin: 0; }
.faq-list { display: grid; gap: 14px; margin-top: 22px; }
.faq-item {
  padding: 20px 22px;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 18px;
}
.faq-q { margin: 0 0 10px; font-size: 15.5px; font-weight: 600; color: var(--ink); line-height: 1.55; }
.faq-a { margin: 0; font-size: 14.5px; color: var(--ink-soft); line-height: 1.7; }
.faq-a + .faq-a { margin-top: 8px; }

/* ---- closing cta ---- */
.closing { text-align: center; padding: clamp(48px, 10vw, 80px) 0 clamp(8px, 3vw, 24px); }
.closing .sub { color: var(--ink-soft); margin: 0 0 22px; font-size: clamp(15px, 4vw, 16px); }
.cta {
  display: inline-block;
  padding: 15px 30px;
  background: var(--primary);
  color: #fff;
  border-radius: 999px;
  text-decoration: none;
  font-weight: 600;
  font-size: 15px;
  letter-spacing: 0.02em;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.cta:hover { transform: translateY(-1px); box-shadow: 0 10px 24px -12px rgba(52, 114, 85, 0.6); }

/* ---- footer ---- */
footer {
  border-top: 1px solid var(--line);
  font-size: 13px;
  color: var(--ink-soft);
  margin-top: clamp(40px, 8vw, 72px);
  padding: 40px 0 56px;
}
.footer-row { display: flex; gap: 20px; flex-wrap: wrap; align-items: center; }
.footer-row a { color: var(--ink-soft); text-decoration: none; }
.footer-row a:hover { text-decoration: underline; }

/* ---- scroll reveal (progressive enhancement) ---- */
.js .reveal { opacity: 0; transform: translateY(20px); transition: opacity 0.7s cubic-bezier(0.22, 0.61, 0.36, 1), transform 0.7s cubic-bezier(0.22, 0.61, 0.36, 1); }
.js .reveal.in { opacity: 1; transform: none; }
.js .reveal .stagger > * { opacity: 0; transform: translateY(12px); transition: opacity 0.6s cubic-bezier(0.22, 0.61, 0.36, 1), transform 0.6s cubic-bezier(0.22, 0.61, 0.36, 1); }
.js .reveal.in .stagger > * { opacity: 1; transform: none; }
.js .reveal.in .stagger > *:nth-child(2) { transition-delay: 0.06s; }
.js .reveal.in .stagger > *:nth-child(3) { transition-delay: 0.12s; }
@media (prefers-reduced-motion: reduce) {
  html { scroll-behavior: auto; }
  .js .reveal, .js .reveal .stagger > * { opacity: 1; transform: none; transition: none; }
}
"""

FEATURE_VARS = ["--f-green", "--f-blue", "--f-mustard", "--f-purple"]


def url_for(locale_data, page="index"):
    sub = locale_data["subdir"]
    if not sub:
        return f"{BASE_URL}/" if page == "index" else f"{BASE_URL}/{page}/"
    return f"{BASE_URL}/{sub}/" if page == "index" else f"{BASE_URL}/{sub}/{page}/"


# JSON-LD offers requires priceCurrency even for a free app.
CURRENCIES = {"ja": "JPY"}

ICON_LINKS = """\
    <link rel="icon" href="/favicon.ico" sizes="32x32" />
    <link rel="icon" type="image/png" sizes="192x192" href="/assets/favicon-192.png" />
    <link rel="apple-touch-icon" href="/assets/apple-touch-icon.png" />"""

# Safari-only smart banner pointing to the App Store listing.
SMART_BANNER = f'    <meta name="apple-itunes-app" content="app-id={APP_STORE_ID}" />'


def ga4_snippet():
    if not GA4_MEASUREMENT_ID:
        return ""
    return f"""
    <script async src="https://www.googletagmanager.com/gtag/js?id={GA4_MEASUREMENT_ID}"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag() {{ dataLayer.push(arguments); }}
      gtag('js', new Date());
      gtag('config', '{GA4_MEASUREMENT_ID}');
      // LP 唯一のゴール = App Store 遷移を計測。link_location は CTA の ct= (lp_hero/lp_footer/lp_tips)。
      // GA4 は sendBeacon で送るため同一タブ遷移でも欠落しない。capture で stopPropagation 耐性を持たせる。
      document.addEventListener('click', function (e) {{
        var a = e.target.closest && e.target.closest('a[href*="apps.apple.com"]');
        if (!a) return;
        var m = a.href.match(/[?&]ct=([^&]+)/);
        gtag('event', 'app_store_click', {{ link_location: m ? m[1] : 'other' }});
      }}, true);
    </script>"""


def hreflang_links(page="index", locales=None):
    """<link rel=alternate hreflang> cluster. x-default points to ja (site root)."""
    codes = locales or list(LOCALES)
    lines = []
    for code in codes:
        d = LOCALES[code]
        lines.append(
            f'    <link rel="alternate" hreflang="{d["html_lang"]}" href="{url_for(d, page)}" />'
        )
    lines.append(
        f'    <link rel="alternate" hreflang="x-default" href="{url_for(LOCALES["ja"], page)}" />'
    )
    return "\n".join(lines)


def app_jsonld(code, d, url):
    data = {
        "@context": "https://schema.org",
        "@type": "MobileApplication",
        "name": "TARIRU",
        "description": d["description"],
        "url": url,
        "image": OG_IMAGE,
        "operatingSystem": "iOS",
        "applicationCategory": "FinanceApplication",
        "installUrl": APP_STORE_URL,
        "offers": {"@type": "Offer", "price": "0", "priceCurrency": CURRENCIES[code]},
    }
    return (
        '    <script type="application/ld+json">\n'
        + json.dumps(data, ensure_ascii=False, indent=2)
        + "\n    </script>"
    )


def faq_jsonld(d):
    data = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": q,
                "acceptedAnswer": {"@type": "Answer", "text": a},
            }
            for q, a in d["faqs"]
        ],
    }
    return (
        '    <script type="application/ld+json">\n'
        + json.dumps(data, ensure_ascii=False, indent=2)
        + "\n    </script>"
    )


def index_html(code, d):
    url = url_for(d, "index")
    cta_base = app_store_cta_url(code)
    thoughts_html = "\n".join(f"        <li>{t}</li>" for t in d["thoughts"])
    steps_html = "\n".join(
        f'        <div class="step"><div class="n">{i + 1}</div>'
        f'<div><h3>{title}</h3><p>{body}</p></div></div>'
        for i, (title, body) in enumerate(d["steps"])
    )
    features_html = "\n".join(
        f'        <div class="f" style="--f: var({FEATURE_VARS[i]})">'
        f"<strong>{name}</strong><span>{sub}</span></div>"
        for i, (name, sub) in enumerate(d["features"])
    )
    screens_html = "\n".join(
        f'        <img class="shot" src="/assets/store/{code}/{n:02d}.png?v={ASSET_VERSION}" '
        f'width="1320" height="2868" loading="lazy" alt="{d["screen_alt"]} {n}" />'
        for n in range(1, SCREENSHOT_COUNT + 1)
    )
    support_href = "/support/" if not d["subdir"] else f'/{d["subdir"]}/support/'
    privacy_href = "/privacy/"
    tips_link = (
        f'<a href="/tips/">{d["tips_label"]}</a>\n          '
        if code in TIPS_LOCALES
        else ""
    )
    journal_link = (
        f'<a href="/journal/">{d["journal_eyebrow"]}</a>\n          '
        if code in JOURNAL_LOCALES
        else ""
    )
    return f"""<!doctype html>
<html lang="{d["html_lang"]}">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
    <meta name="theme-color" content="#faf8f8" />
    <meta name="robots" content="index,follow" />
    <title>{d["title"]}</title>
    <meta name="description" content="{d["description"]}" />
    <meta property="og:title" content="{d["title"]}" />
    <meta property="og:description" content="{d["description"]}" />
    <meta property="og:type" content="website" />
    <meta property="og:url" content="{url}" />
    <meta property="og:locale" content="{d["og_locale"]}" />
    <meta property="og:image" content="{OG_IMAGE}" />
    <meta property="og:image:width" content="1200" />
    <meta property="og:image:height" content="630" />
    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:title" content="{d["title"]}" />
    <meta name="twitter:description" content="{d["description"]}" />
    <meta name="twitter:image" content="{OG_IMAGE}" />
    <link rel="canonical" href="{url}" />
{hreflang_links("index")}
{ICON_LINKS}
{SMART_BANNER}
{app_jsonld(code, d, url)}{ga4_snippet()}
    <style>
{BASE_CSS}    </style>
  </head>
  <body>
    <header class="hero">
      <p class="wordmark">TARIRU</p>
      <h1>{d["hero_headline"]}</h1>
      <p class="sub">{d["hero_sub"]}</p>
      <div class="verdict" aria-hidden="true">
        <p class="verdict-label"><span class="verdict-month">今月</span>{d["verdict_label_suffix"]}</p>
        <p class="verdict-answer">{d["verdict_answer"]}</p>
        <p class="verdict-amount">{d["verdict_amount"]}</p>
        <div class="verdict-bar"><span class="verdict-fill"></span></div>
        <p class="verdict-caption">{d["verdict_caption"]}</p>
      </div>
      <a class="cta" href="{cta_base}?ct=lp_hero" rel="noopener">{d["cta"]}</a>
      <div class="scroll-cue" aria-hidden="true">{d["scroll_cue"]}</div>
    </header>

    <main>
      <section class="why">
        <div class="wrap reveal">
          <p class="eyebrow">{d["why_eyebrow"]}</p>
          <h2>{d["why_headline"]}</h2>
          <p class="scenario">{d["why_scenario"]}</p>
          <p class="lead">{d["why_lead"]}</p>
          <ul class="thoughts stagger">
{thoughts_html}
          </ul>
          <p class="note">{d["why_note"]}</p>
        </div>
      </section>

      <section class="how">
        <div class="wrap reveal">
          <p class="eyebrow">{d["steps_eyebrow"]}</p>
          <h2>{d["steps_headline"]}</h2>
          <div class="steps stagger">
{steps_html}
          </div>
        </div>
      </section>

      <section class="app reveal">
        <div class="wrap">
          <p class="eyebrow">{d["app_eyebrow"]}</p>
          <h2>{d["app_headline"]}</h2>
        </div>
        <div class="showcase stagger" aria-label="{d["app_eyebrow"]}">
{screens_html}
        </div>
      </section>

      <section class="features-section">
        <div class="wrap reveal">
          <p class="eyebrow">{d["features_eyebrow"]}</p>
          <h2>{d["features_headline"]}</h2>
          <p class="lead">{d["features_lead"]}</p>
          <div class="features stagger" aria-label="{d["features_aria"]}">
{features_html}
          </div>
        </div>
      </section>

      <section class="privacy">
        <div class="wrap reveal">
          <p class="eyebrow">{d["privacy_eyebrow"]}</p>
          <h2>{d["privacy_headline"]}</h2>
          <p class="lead">{d["privacy_body"]}</p>
        </div>
      </section>

      <section class="closing">
        <div class="wrap reveal">
          <h2>{d["closing_headline"]}</h2>
          <p class="sub">{d["closing_sub"]}</p>
          <a class="cta" href="{cta_base}?ct=lp_footer" rel="noopener">{d["cta"]}</a>
        </div>
      </section>
    </main>

    <footer>
      <div class="wrap">
        <div class="footer-row">
          {tips_link}{journal_link}<a href="{support_href}">{d["support_label"]}</a>
          <a href="{privacy_href}">{d["privacy_label"]}</a>
          <span>© TARIRU</span>
        </div>
      </div>
    </footer>
{REVEAL_SCRIPT}{DRAG_SCROLL_SCRIPT}  </body>
</html>
"""


def support_html(code, d):
    url = url_for(d, "support")
    home_href = "/" if not d["subdir"] else f"/{d['subdir']}/"
    faqs_html = "\n".join(
        f'      <p>\n        <strong>{q}</strong><br />\n        {a}\n      </p>'
        for q, a in d["faqs"]
    )
    tips_prompt = (
        f'\n      <p>{d["tips_support_before"]} '
        f'<a href="/tips/">{d["tips_label"]}</a>{d["tips_support_after"]}</p>'
        if code in TIPS_LOCALES
        else ""
    )
    return f"""<!doctype html>
<html lang="{d["html_lang"]}">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
    <title>{d["support_title"]}</title>
    <meta name="description" content="{d["support_description"]}" />
    <link rel="canonical" href="{url}" />
    <meta property="og:locale" content="{d["og_locale"]}" />
{hreflang_links("support")}
{ICON_LINKS}
{SMART_BANNER}
{faq_jsonld(d)}{ga4_snippet()}
    <style>
{SUPPORT_CSS}    </style>
  </head>
  <body>
    <main>
      <h1>{d["support_h1"]}</h1>
      <p>{d["support_intro"]}</p>{tips_prompt}

      <h2>{d["contact_h2"]}</h2>
      <p>{d["contact_body"]}</p>

      <h2>{d["faq_h2"]}</h2>
{faqs_html}

      <a class="back" href="{home_href}">{d["back"]}</a>
    </main>
  </body>
</html>
"""


def tips_jsonld(d):
    data = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": q,
                "acceptedAnswer": {"@type": "Answer", "text": "".join(a)},
            }
            for q, a, *_ in d["tips_faqs"]
        ],
    }
    return (
        '    <script type="application/ld+json">\n'
        + json.dumps(data, ensure_ascii=False, indent=2)
        + "\n    </script>"
    )


def tips_html(code, d):
    url = url_for(d, "tips")
    cta_base = app_store_cta_url(code)
    home_href = "/" if not d["subdir"] else f"/{d['subdir']}/"
    support_href = "/support/" if not d["subdir"] else f"/{d['subdir']}/support/"
    privacy_href = "/privacy/"

    def card(it):
        badge, title, body = it[0], it[1], it[2]
        return (
            f'            <div class="tip"><span class="badge">{badge}</span>'
            f"<h3>{title}</h3><p>{body}</p></div>"
        )

    def render_group(g):
        parts = []
        if g.get("subhead"):
            parts.append(f'          <p class="subhead">{g["subhead"]}</p>')
        cards = "\n".join(card(it) for it in g["items"])
        parts.append(f'          <div class="tips stagger">\n{cards}\n          </div>')
        return "\n".join(parts)

    screens = []
    for s in d["tips_screens"]:
        body = "\n".join(render_group(g) for g in s["groups"])
        screens.append(
            '      <section class="screen reveal">\n'
            "        <div class=\"wrap\">\n"
            f"          <h2>{s['heading']}</h2>\n"
            f"          <p class=\"screen-lead\">{s['lead']}</p>\n"
            f"{body}\n"
            "        </div>\n"
            "      </section>"
        )
    groups_block = "\n\n".join(screens)

    def faq_item(item):
        q, lines = item[0], item[1]
        answer = "".join(f'<p class="faq-a">{line}</p>' for line in lines)
        return (
            f'            <div class="faq-item"><p class="faq-q">{q}</p>'
            f"{answer}</div>"
        )

    faq_items = "\n".join(faq_item(it) for it in d["tips_faqs"])
    faq_block = (
        '      <section class="faq reveal">\n'
        "        <div class=\"wrap\">\n"
        f"          <h2>{d['tips_faq_heading']}</h2>\n"
        f'          <div class="faq-list stagger">\n{faq_items}\n          </div>\n'
        "        </div>\n"
        "      </section>"
    )
    return f"""<!doctype html>
<html lang="{d["html_lang"]}">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
    <meta name="theme-color" content="#faf8f8" />
    <meta name="robots" content="index,follow" />
    <title>{d["tips_title"]}</title>
    <meta name="description" content="{d["tips_description"]}" />
    <meta property="og:title" content="{d["tips_title"]}" />
    <meta property="og:description" content="{d["tips_description"]}" />
    <meta property="og:type" content="article" />
    <meta property="og:url" content="{url}" />
    <meta property="og:locale" content="{d["og_locale"]}" />
    <meta property="og:image" content="{OG_IMAGE}" />
    <meta property="og:image:width" content="1200" />
    <meta property="og:image:height" content="630" />
    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:title" content="{d["tips_title"]}" />
    <meta name="twitter:description" content="{d["tips_description"]}" />
    <meta name="twitter:image" content="{OG_IMAGE}" />
    <link rel="canonical" href="{url}" />
{hreflang_links("tips", locales=TIPS_LOCALES)}
{ICON_LINKS}
{SMART_BANNER}
{tips_jsonld(d)}{ga4_snippet()}
    <style>
{TIPS_CSS}    </style>
  </head>
  <body>
    <header class="tips-hero">
      <p class="wordmark">TARIRU</p>
      <p class="eyebrow">{d["tips_eyebrow"]}</p>
      <h1>{d["tips_h1"]}</h1>
      <p class="lead">{d["tips_lead"]}</p>
    </header>

    <main>
{groups_block}

{faq_block}

      <section class="closing-note reveal">
        <div class="wrap">
          <p class="note">{d["tips_note"]}</p>
        </div>
      </section>

      <section class="closing reveal">
        <div class="wrap">
          <p class="sub">{d["tips_closing_sub"]}</p>
          <a class="cta" href="{cta_base}?ct=lp_tips" rel="noopener">{d["cta"]}</a>
        </div>
      </section>
    </main>

    <footer>
      <div class="wrap">
        <div class="footer-row">
          <a href="{home_href}">{d["back"]}</a>
          <a href="{support_href}">{d["support_label"]}</a>
          <a href="{privacy_href}">{d["privacy_label"]}</a>
          <span>© TARIRU</span>
        </div>
      </div>
    </footer>
{TIPS_REVEAL_SCRIPT}  </body>
</html>
"""


PRIVACY_META = {
    "ja": {
        "title": "プライバシーポリシー — TARIRU",
        "description": "TARIRU のプライバシーポリシー。入力した金融情報は端末とあなたの iCloud にのみ保存され、開発者のサーバーはありません。銀行・カード会社との連携もありません。",
    },
}


def md_inline(s):
    s = html_mod.escape(s, quote=False)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2" rel="noopener">\1</a>', s)
    return s


def md_to_html(md):
    """Minimal converter for content/privacy.md (h1/h2, hr, p, ul/ol with one nest level)."""
    out = []
    para = []
    # stack of open list tags, innermost last; index = nest depth
    lists = []

    def flush_para():
        if para:
            out.append("      <p>" + md_inline(" ".join(para)) + "</p>")
            para.clear()

    def close_lists(depth=0):
        while len(lists) > depth:
            out.append("      " + "</li></%s>" % lists.pop())

    for line in md.splitlines():
        stripped = line.strip()
        if not stripped:
            flush_para()
            close_lists()
            continue
        if stripped == "---":
            flush_para()
            close_lists()
            out.append("      <hr />")
            continue
        if stripped.startswith("## "):
            flush_para()
            close_lists()
            out.append("      <h2>" + md_inline(stripped[3:]) + "</h2>")
            continue
        if stripped.startswith("# "):
            flush_para()
            close_lists()
            out.append("      <h1>" + md_inline(stripped[2:]) + "</h1>")
            continue
        m = re.match(r"^(\s*)(-|\d+\.)\s+(.*)$", line)
        if m:
            flush_para()
            depth = 1 if m.group(1) else 0
            tag = "ul" if m.group(2) == "-" else "ol"
            if len(lists) <= depth:
                out.append("      " + f"<{tag}>")
                lists.append(tag)
            else:
                close_lists(depth + 1)
                out.append("      </li>")
            out.append("      <li>" + md_inline(m.group(3)))
            continue
        para.append(stripped)
    flush_para()
    close_lists()
    return "\n".join(out)


PRIVACY_CSS = SUPPORT_CSS + """\
main { max-width: 720px; }
h1 { font-size: 26px; }
h2 { font-size: 17px; }
li { line-height: 1.7; color: var(--ink-soft); margin: 4px 0; }
hr { border: 0; border-top: 1px solid var(--line); margin: 32px 0; }
code { font-size: 0.9em; background: #f2f2f4; padding: 1px 5px; border-radius: 4px; }
"""


def privacy_html(code, body_html):
    d = LOCALES[code]
    meta = PRIVACY_META[code]
    url = url_for(d, "privacy")
    home_href = "/" if not d["subdir"] else f"/{d['subdir']}/"
    return f"""<!doctype html>
<html lang="{d["html_lang"]}">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
    <title>{meta["title"]}</title>
    <meta name="description" content="{meta["description"]}" />
    <link rel="canonical" href="{url}" />
    <meta property="og:locale" content="{d["og_locale"]}" />
{hreflang_links("privacy", locales=PRIVACY_LOCALES)}
{ICON_LINKS}{ga4_snippet()}
    <style>
{PRIVACY_CSS}    </style>
  </head>
  <body>
    <main>
{body_html}

      <a class="back" href="{home_href}">{d["back"]}</a>
    </main>
  </body>
</html>
"""


# content/<lang>/journal/<slug>.md: YAML front matter + Markdown body.
FRONT_MATTER_RE = re.compile(r"\A---\n(.*?)\n---\n(.*)\Z", re.DOTALL)


def parse_article_md(path):
    raw = path.read_text()
    m = FRONT_MATTER_RE.match(raw)
    if not m:
        raise ValueError(f"{path}: missing YAML front matter (--- ... ---)")
    meta = yaml.safe_load(m.group(1)) or {}
    meta["body_html"] = md_lib.markdown(m.group(2).strip(), extensions=["extra", "sane_lists"])
    return meta


def load_articles():
    """content/<lang>/journal/*.md -> {locale: [article_dict, ...]}, newest first."""
    articles = {}
    for code in JOURNAL_LOCALES:
        journal_dir = ROOT / "content" / code / "journal"
        items = [parse_article_md(p) for p in sorted(journal_dir.glob("*.md"))] if journal_dir.exists() else []
        items.sort(key=lambda a: a["updated"], reverse=True)
        articles[code] = items
    return articles


def article_jsonld(code, d, meta, url):
    home_url = url_for(d, "index")
    hub_url = url_for(d, "journal")
    article = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": meta["title"],
        "description": meta["description"],
        "url": url,
        "image": OG_IMAGE,
        "datePublished": str(meta["updated"]),
        "dateModified": str(meta["updated"]),
        "inLanguage": d["html_lang"],
        "author": {"@type": "Organization", "name": "TARIRU", "url": BASE_URL},
        "publisher": {"@type": "Organization", "name": "TARIRU", "url": BASE_URL},
        "mainEntityOfPage": {"@type": "WebPage", "@id": url},
    }
    breadcrumb = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": d["title"], "item": home_url},
            {"@type": "ListItem", "position": 2, "name": d["journal_hub_title"], "item": hub_url},
            {"@type": "ListItem", "position": 3, "name": meta["title"], "item": url},
        ],
    }
    return (
        '    <script type="application/ld+json">\n'
        + json.dumps(article, ensure_ascii=False, indent=2)
        + "\n    </script>\n"
        '    <script type="application/ld+json">\n'
        + json.dumps(breadcrumb, ensure_ascii=False, indent=2)
        + "\n    </script>"
    )


def article_html(code, meta, articles_by_slug):
    d = LOCALES[code]
    slug = meta["slug"]
    url = url_for(d, f"journal/{slug}")
    cta_base = app_store_cta_url(code)
    home_href = "/" if not d["subdir"] else f"/{d['subdir']}/"
    journal_href = home_href + "journal/"
    support_href = home_href + "support/"
    privacy_href = "/privacy/"

    related = []
    hub_slug = meta.get("hub")
    if hub_slug and hub_slug != slug and hub_slug in articles_by_slug:
        related.append((hub_slug, articles_by_slug[hub_slug]["title"]))
    for s in meta.get("spokes") or []:
        if s in articles_by_slug and s != slug:
            related.append((s, articles_by_slug[s]["title"]))
    related_html = ""
    if related:
        items = "\n".join(
            f'          <li><a href="{journal_href}{s}/">{t}</a></li>' for s, t in related
        )
        related_html = f"""
      <nav class="related" aria-label="{d['journal_related_label']}">
        <h2>{d["journal_related_label"]}</h2>
        <ul>
{items}
        </ul>
      </nav>"""

    pitch_shots_html = "\n".join(
        f'          <img class="pitch-shot" src="/assets/store/{code}/{n:02d}.png?v={ASSET_VERSION}" '
        f'width="1320" height="2868" loading="lazy" alt="{d["screen_alt"]} {n}" />'
        for n in range(1, SCREENSHOT_COUNT + 1)
    )

    return f"""<!doctype html>
<html lang="{d["html_lang"]}">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
    <meta name="theme-color" content="#faf8f8" />
    <meta name="robots" content="index,follow" />
    <title>{meta["title"]} — TARIRU</title>
    <meta name="description" content="{meta["description"]}" />
    <meta property="og:title" content="{meta["title"]}" />
    <meta property="og:description" content="{meta["description"]}" />
    <meta property="og:type" content="article" />
    <meta property="og:url" content="{url}" />
    <meta property="og:locale" content="{d["og_locale"]}" />
    <meta property="og:image" content="{OG_IMAGE}" />
    <meta property="og:image:width" content="1200" />
    <meta property="og:image:height" content="630" />
    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:title" content="{meta["title"]}" />
    <meta name="twitter:description" content="{meta["description"]}" />
    <meta name="twitter:image" content="{OG_IMAGE}" />
    <link rel="canonical" href="{url}" />
{hreflang_links(f"journal/{slug}", locales=list(JOURNAL_LOCALES))}
{ICON_LINKS}
{SMART_BANNER}
{article_jsonld(code, d, meta, url)}{ga4_snippet()}
    <style>
{JOURNAL_CSS}    </style>
  </head>
  <body>
    <main>
      <p class="eyebrow">{d["journal_eyebrow"]}</p>
      <article>
        <h1>{meta["title"]}</h1>
        <p class="updated">{d["journal_updated_label"]} {meta["updated"]}</p>
{meta["body_html"]}
      </article>

      <div class="app-pitch">
        <div class="pitch-shots" aria-label="{d["app_eyebrow"]}">
{pitch_shots_html}
        </div>
        <p class="rating">★ {APP_RATING["score"]}<span class="rating-count"> ・ {APP_RATING["count"]}{d["journal_rating_suffix"]}</span></p>
        <h2>{d["journal_pitch_headline"]}</h2>
        <p>{d["journal_pitch_body"]}</p>
        <a class="cta" href="{cta_base}?ct=journal_{slug}" rel="noopener">{d["cta"]}</a>
        <p class="note">{d["journal_pitch_note"]}</p>
      </div>
{related_html}

      <a class="back" href="{journal_href}">{d["journal_back_label"]}</a>

      <nav class="footer-links">
        <a href="{support_href}">{d["support_label"]}</a>
        <a href="{privacy_href}">{d["privacy_label"]}</a>
      </nav>
    </main>
{DRAG_SCROLL_SCRIPT}  </body>
</html>
"""


def journal_index_html(code, items):
    d = LOCALES[code]
    url = url_for(d, "journal")
    home_href = "/" if not d["subdir"] else f"/{d['subdir']}/"
    journal_href = home_href + "journal/"
    cards = "\n".join(
        f'''        <li class="card">
          <a href="{journal_href}{a["slug"]}/">
            <h2>{a["title"]}</h2>
            <p>{a["description"]}</p>
          </a>
        </li>'''
        for a in items
    )
    return f"""<!doctype html>
<html lang="{d["html_lang"]}">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
    <meta name="theme-color" content="#faf8f8" />
    <meta name="robots" content="index,follow" />
    <title>{d["journal_hub_title"]}</title>
    <meta name="description" content="{d["journal_hub_description"]}" />
    <meta property="og:title" content="{d["journal_hub_title"]}" />
    <meta property="og:description" content="{d["journal_hub_description"]}" />
    <meta property="og:type" content="website" />
    <meta property="og:url" content="{url}" />
    <meta property="og:locale" content="{d["og_locale"]}" />
    <meta property="og:image" content="{OG_IMAGE}" />
    <meta property="og:image:width" content="1200" />
    <meta property="og:image:height" content="630" />
    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:title" content="{d["journal_hub_title"]}" />
    <meta name="twitter:description" content="{d["journal_hub_description"]}" />
    <meta name="twitter:image" content="{OG_IMAGE}" />
    <link rel="canonical" href="{url}" />
{hreflang_links("journal", locales=list(JOURNAL_LOCALES))}
{ICON_LINKS}
{SMART_BANNER}{ga4_snippet()}
    <style>
{JOURNAL_CSS}    </style>
  </head>
  <body>
    <main>
      <p class="eyebrow">TARIRU</p>
      <h1>{d["journal_hub_title"]}</h1>
      <p class="lead">{d["journal_hub_lead"]}</p>
      <ul class="cards">
{cards}
      </ul>

      <a class="back" href="{home_href}">{d["back"]}</a>
    </main>
  </body>
</html>
"""


def sitemap_xml(articles_by_locale=None):
    clusters = [
        ("index", list(LOCALES)),
        ("support", list(LOCALES)),
        ("tips", list(TIPS_LOCALES)),
        ("privacy", list(PRIVACY_LOCALES)),
    ]
    urls = []
    for page, codes in clusters:
        alts = "".join(
            f'\n    <xhtml:link rel="alternate" hreflang="{LOCALES[c]["html_lang"]}" href="{url_for(LOCALES[c], page)}" />'
            for c in codes
        )
        alts += f'\n    <xhtml:link rel="alternate" hreflang="x-default" href="{url_for(LOCALES["ja"], page)}" />'
        for c in codes:
            urls.append(f"  <url>\n    <loc>{url_for(LOCALES[c], page)}</loc>{alts}\n  </url>")

    articles_by_locale = articles_by_locale or {}
    if any(articles_by_locale.values()):
        hub_alts = "".join(
            f'\n    <xhtml:link rel="alternate" hreflang="{LOCALES[c]["html_lang"]}" href="{url_for(LOCALES[c], "journal")}" />'
            for c in JOURNAL_LOCALES
        )
        hub_alts += f'\n    <xhtml:link rel="alternate" hreflang="x-default" href="{url_for(LOCALES["ja"], "journal")}" />'
        for c in JOURNAL_LOCALES:
            urls.append(f"  <url>\n    <loc>{url_for(LOCALES[c], 'journal')}</loc>{hub_alts}\n  </url>")
        for c in JOURNAL_LOCALES:
            for a in articles_by_locale[c]:
                page = f"journal/{a['slug']}"
                alts = "".join(
                    f'\n    <xhtml:link rel="alternate" hreflang="{LOCALES[cc]["html_lang"]}" href="{url_for(LOCALES[cc], page)}" />'
                    for cc in JOURNAL_LOCALES
                )
                alts += f'\n    <xhtml:link rel="alternate" hreflang="x-default" href="{url_for(LOCALES["ja"], page)}" />'
                urls.append(
                    f"  <url>\n    <loc>{url_for(LOCALES[c], page)}</loc>{alts}"
                    f"\n    <lastmod>{a['updated']}</lastmod>\n  </url>"
                )

    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
        'xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
        + "\n".join(urls)
        + "\n</urlset>\n"
    )


ROBOTS_TXT = f"""User-agent: *
Allow: /

Sitemap: {BASE_URL}/sitemap.xml
"""


def main():
    written = []
    for code, d in LOCALES.items():
        sub = d["subdir"]
        base = ROOT / sub if sub else ROOT
        (base / "support").mkdir(parents=True, exist_ok=True)
        idx = base / "index.html"
        sup = base / "support" / "index.html"
        idx.write_text(index_html(code, d))
        sup.write_text(support_html(code, d))
        written.append(str(idx.relative_to(ROOT)))
        written.append(str(sup.relative_to(ROOT)))

    for code in TIPS_LOCALES:
        sub = LOCALES[code]["subdir"]
        base = ROOT / sub if sub else ROOT
        (base / "tips").mkdir(parents=True, exist_ok=True)
        page = base / "tips" / "index.html"
        page.write_text(tips_html(code, LOCALES[code]))
        written.append(str(page.relative_to(ROOT)))

    privacy_md = (ROOT / "content" / "privacy.md").read_text()
    for code in PRIVACY_LOCALES:
        sub = LOCALES[code]["subdir"]
        base = ROOT / sub if sub else ROOT
        (base / "privacy").mkdir(parents=True, exist_ok=True)
        page = base / "privacy" / "index.html"
        page.write_text(privacy_html(code, md_to_html(privacy_md)))
        written.append(str(page.relative_to(ROOT)))

    articles_by_locale = load_articles()
    for code in JOURNAL_LOCALES:
        items = articles_by_locale[code]
        by_slug = {a["slug"]: a for a in items}
        sub = LOCALES[code]["subdir"]
        base = ROOT / sub if sub else ROOT
        journal_dir = base / "journal"
        for a in items:
            art_dir = journal_dir / a["slug"]
            art_dir.mkdir(parents=True, exist_ok=True)
            page = art_dir / "index.html"
            page.write_text(article_html(code, a, by_slug))
            written.append(str(page.relative_to(ROOT)))
        journal_dir.mkdir(parents=True, exist_ok=True)
        hub_page = journal_dir / "index.html"
        hub_page.write_text(journal_index_html(code, items))
        written.append(str(hub_page.relative_to(ROOT)))

    (ROOT / "sitemap.xml").write_text(sitemap_xml(articles_by_locale))
    (ROOT / "robots.txt").write_text(ROBOTS_TXT)
    written += ["sitemap.xml", "robots.txt"]

    for path in written:
        print(path)


if __name__ == "__main__":
    main()
