# Agent Skills 入門 — SKILL.md だけで動かす

> watsonx Orchestrate ADK 2.x 系  
> 関連記事: [watsonx Orchestrate の Agent Skills を試してみる](https://qiita.com/yuka_nm/items/c557e0c940f04dabb263)

## このサンプルについて

`SKILL.md` 1 ファイルだけで Agent Skill を作る最小構成のサンプルです。

「Tool だけでもエージェントは動くのに、なぜ Skill を使うのか？」という問いに答えながら、出張精算チェックのエージェントを例に Skill の基本を体験できます。

## ファイル構成

```
agent-skill-tutorial-qiita1/
├── agent.yaml
└── skills/
    └── travel-expense-review/
        └── SKILL.md
```

## 使い方

```bash
# Skill を登録
orchestrate skills import --dir skills/travel-expense-review/

# Agent を登録
orchestrate agents import -f agent.yaml
```

`agent.yaml` の `llm` はお使いの環境で利用可能なモデルに変更してください。

```bash
orchestrate models list
```

## 参考

- [Agent skills — IBM watsonx Orchestrate ADK](https://developer.watson-orchestrate.ibm.com/agent_skills/overview)
- [Managing agent skills](https://developer.watson-orchestrate.ibm.com/agent_skills/manage_skills)
