# Agent Skills — references と scripts を使う

> watsonx Orchestrate ADK 2.x 系  
> 関連記事: [watsonx Orchestrate の Agent Skills を試してみる（2）— references と scripts 編](#)（公開後にリンクを差し替え）  
> 前回の記事: [watsonx Orchestrate の Agent Skills を試してみる](https://qiita.com/yuka_nm/items/c557e0c940f04dabb263)

## このサンプルについて

`SKILL.md` に加えて `references/` と `scripts/` を使う構成のサンプルです。

- **`references/expense-policy.md`** — 社内経費規程（宿泊費上限・日当・領収書ルール）。SKILL.md から参照させることで、規程改定時はこのファイルだけ差し替えればよい構成にしています。
- **`scripts/validate_total.py`** — 経費明細の合計金額を検証する Python スクリプト。LLM に計算させるのではなく、スクリプトで確実に検証します。

## ファイル構成

```
agent-skill-tutorial-qiita2/
├── agent.yaml
└── skills/
    └── travel-expense-review/
        ├── SKILL.md
        ├── references/
        │   └── expense-policy.md
        └── scripts/
            └── validate_total.py
```

## 使い方

```bash
# Skill を登録（references/ と scripts/ も自動でアップロードされる）
orchestrate skills import --dir skills/travel-expense-review/

# Agent を登録
orchestrate agents import -f agent.yaml
```

`agent.yaml` の `llm` はお使いの環境で利用可能なモデルに変更してください。

```bash
orchestrate models list
```

### 規程ファイルだけ差し替えたい場合

```bash
orchestrate skills upload-reference --skill-name travel-expense-review \
  --file references/expense-policy.md
```

## 参考

- [Agent skills — IBM watsonx Orchestrate ADK](https://developer.watson-orchestrate.ibm.com/agent_skills/overview)
- [Managing agent skills](https://developer.watson-orchestrate.ibm.com/agent_skills/manage_skills)
