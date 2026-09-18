# watsonx Orchestrate の Agent Skills を試してみる（2）— references と scripts 編

前回の記事（[watsonx Orchestrate の Agent Skills を試してみる](https://qiita.com/yuka_nm/items/c557e0c940f04dabb263)）では、`SKILL.md` 1ファイルだけで出張精算チェックのエージェントを作りました。

今回は Skill ディレクトリに置ける `references/` と `scripts/` を使って、同じユースケースをもう少し実用的な構成に拡張してみます。

## Skill ディレクトリの構成おさらい

Skill ディレクトリには `SKILL.md` 以外に 2 種類のサブディレクトリを置けます。

```
my-skill/
├── SKILL.md          # 必須: frontmatter + 手順
├── references/       # 任意: エージェントが参照するドキュメント (.md / .txt / .json)
└── scripts/          # 任意: エージェントが実行する Python スクリプト
```

それぞれ何のためにあるかというと、

- **`references/`** — 社内規程・ポリシー・ルックアップテーブルなど、**エージェントに読ませたい知識ドキュメント**を置く場所。SKILL.md の本文に直接書いてもよいですが、規程が変わったときに `references/` のファイルだけ差し替えれば済むのが利点です。
- **`scripts/`** — **エージェントが実行する Python スクリプト**を置く場所。LLM に計算や検証をさせるのではなく、確実に処理したいロジックをスクリプト化できます。

重要なのは「**どちらも自動では使われない**」という点です。SKILL.md の本文に「このファイルを参照せよ」「このスクリプトを実行せよ」と明示的に書いて初めてエージェントが使います。

## 今回作るもの

前回の `travel-expense-review` Skill に以下を追加します。

```
skills/travel-expense-review/
├── SKILL.md                    # 手順（references/scripts の使い方を追記）
├── references/
│   └── expense-policy.md       # 出張経費規程（宿泊費上限・日当・領収書ルール）
└── scripts/
    └── validate_total.py       # 経費明細の合計金額を検証するスクリプト
```

前回の agent.yaml はそのまま使います（[サンプルコード](https://github.com/yukanm/wxo-samples)）。

```yaml
spec_version: v1
kind: native
name: travel_expense_agent
description: 出張精算の申請内容をチェックするエージェント。
llm: groq/openai/gpt-oss-120b
style: react_intrinsic
instructions: |
  あなたは出張精算のサポートアシスタントです。
  ユーザーが出張精算の申請内容を提示したら、travel-expense-review スキルを使ってレビューを実施してください。
  日本語で丁寧に回答してください。
skills:
  - travel-expense-review
```

## references/ — 社内経費規程を参照させる

まず `references/expense-policy.md` を作ります。

```markdown
# 出張経費規程（サンプル）

## 宿泊費上限（1泊あたり）

| 出張先区分 | 上限金額 |
|---|---|
| 東京・大阪・名古屋 | 15,000円 |
| その他国内 | 12,000円 |

## 日当（1日あたり）

| 区分 | 金額 |
|---|---|
| 国内出張 | 2,000円 |

## 領収書の要否

- 1件 5,000円以上：領収書必須
- 1件 5,000円未満：領収書不要（日当など）
```

次に `SKILL.md` の手順に「規程を参照する」ステップを追加します。

```markdown
---
name: travel-expense-review
description: 出張精算の申請内容をレビューし、必須情報の不足・金額の矛盾・申請内容の不備を確認して結果を報告する。ユーザーが「出張精算をチェックしてほしい」「経費申請を確認してほしい」などと依頼したときに使用する。
---

# 出張精算レビュー手順

...（ステップ 1〜2 は前回と同様）

## ステップ 3: 規程との照合

社内経費規程を参照してください: expense-policy.md

以下の観点で規程との乖離がないか確認する。

- 宿泊費が出張先区分の上限金額を超えていないか
- 日当の金額が規程と一致しているか
- 5,000円以上の経費項目に領収書の記載があるか

規程を超過している項目がある場合は、規程上の上限金額とあわせて指摘する。
```

ポイントは `expense-policy.md` という**ファイル名を本文中に明示する**ことです。エージェントはこの記述を見てファイルを読みに行きます。

### import

```bash
orchestrate skills import --dir skills/travel-expense-review/
```

`--dir` を使うと `references/` 配下のファイルも自動でアップロードされます。

<!-- スクショ: references 追加後の import 結果ターミナル -->

### 動かしてみる

宿泊費が上限を超えているパターンを試します。

```
以下の出張精算をチェックしてください。

出張期間: 2025年7月1日〜2日（1泊2日）
出張先: 名古屋
出張目的: 社内研修
経費内訳:
  - 新幹線往復: 11,000円（領収書あり）
  - 宿泊費（1泊）: 18,000円（領収書あり）
  - 日当（2日分）: 4,000円
合計: 33,000円
```

<!-- スクショ: references 使用時の応答（規程超過が指摘されているところ） -->

名古屋出張の宿泊費上限は 12,000円なので、18,000円は規程超過です。`expense-policy.md` を参照した上で「上限 12,000円を 6,000円超過しています」と指摘されました。

**なぜ SKILL.md に直接書かないのか**

規程の上限金額は変わることがあります。`SKILL.md` 本文にハードコードすると改定のたびに Skill ごと更新が必要になりますが、`references/expense-policy.md` に切り出しておけばファイルの差し替えだけで済みます。

```bash
# 規程改定時はこれだけ
orchestrate skills upload-reference --skill-name travel-expense-review \
  --file references/expense-policy.md
```

## scripts/ — 合計金額の検証を Python に任せる

次に `scripts/validate_total.py` を作ります。

```python
def run(items: list, declared_total: int) -> dict:
    """
    経費明細の合計金額を検証する。

    Args:
        items: [{"name": "新幹線往復", "amount": 28000}, ...]
        declared_total: 申請者が記載した合計金額
    """
    calculated = sum(item["amount"] for item in items)
    matched = calculated == declared_total
    return {
        "calculated_total": calculated,
        "declared_total": declared_total,
        "matched": matched,
        "diff": declared_total - calculated,
    }
```

`scripts/` に置けるのは Python スクリプトのみで、関数名は `run` が規約です。なお、`os` / `sys` / `requests` などのシステム・ネットワーク系モジュールはセキュリティ上ブロックされているため、**純粋な計算処理に限られます**。

`SKILL.md` に実行の指示を追加します。

```markdown
## ステップ 3（金額検証）

合計金額を検証するために validate_total.py を実行してください。
args={"items": [<経費明細リスト（name と amount を持つオブジェクトの配列）>], "declared_total": <申請合計金額（整数）>}

matched が false の場合は計算誤りとして、calculated_total と diff をあわせてユーザーに報告し、修正を促してください。
```

### import

```bash
orchestrate skills import --dir skills/travel-expense-review/
```

`scripts/` 配下の `.py` ファイルも `--dir` で自動アップロードされます。

<!-- スクショ: scripts 追加後の import 結果ターミナル（0 script(s) → 1 script(s) になっているところ） -->

### 動かしてみる

合計金額に誤りがあるパターンを試します。

```
以下の出張精算をチェックしてください。

出張期間: 2025年7月10日〜11日（1泊2日）
出張先: 大阪
出張目的: 顧客打ち合わせ
経費内訳:
  - 新幹線往復: 28,000円（領収書あり）
  - 宿泊費（1泊）: 12,000円（領収書あり）
  - 日当（2日分）: 4,000円
合計: 45,000円
```

実際の合計は 44,000円ですが、申請書には 45,000円と記載しています。

<!-- スクショ: scripts 使用時の応答（スクリプトが実行されて計算誤りが指摘されているところ） -->

`validate_total.py` が実行され、`calculated_total: 44000` / `declared_total: 45000` / `diff: 1000` が返ってきて、「合計金額に 1,000円の誤りがあります」と指摘されました。

**なぜ LLM に計算させないのか**

LLM は足し算を間違えることがあります。金額の検証のような「正確さが求められる処理」はスクリプトに任せることで確実性が上がります。スクリプトの実行結果は決定的（deterministic）なので、LLM の計算揺れに左右されません。

## import とファイル管理のまとめ

| 操作 | コマンド |
|---|---|
| Skill 全体（初回・更新） | `orchestrate skills import --dir skills/travel-expense-review/` |
| references だけ差し替え | `orchestrate skills upload-reference --skill-name travel-expense-review --file references/expense-policy.md` |
| scripts だけ差し替え | `orchestrate skills upload-script --skill-name travel-expense-review --file scripts/validate_total.py` |

規程改定などで `references/` だけ更新したいときは `upload-reference` で個別に差し替えられます。Skill 全体を再 import する必要はありません。

## まとめ

`references/` と `scripts/` を使うことで、「知識の更新しやすさ」と「計算の確実性」を SKILL.md 本文から分離できます。前回の記事と合わせて、Agent Skills の基本的な使い方は一通り試せた形です。

今回追加したファイルのサンプルコードは近日中にリポジトリに追加予定です（[yukanm/wxo-samples](https://github.com/yukanm/wxo-samples)）。

## 参考

- [Agent skills — IBM watsonx Orchestrate ADK](https://developer.watson-orchestrate.ibm.com/agent_skills/overview)
- [Managing agent skills](https://developer.watson-orchestrate.ibm.com/agent_skills/manage_skills)
- [前回の記事: watsonx Orchestrate の Agent Skills を試してみる](https://qiita.com/yuka_nm/items/c557e0c940f04dabb263)
