# my-claude-skills

自作の [Claude Code](https://docs.claude.com/claude-code) スキル集です。

## スキル一覧

| スキル | 概要 |
| --- | --- |
| [commit](./commit) | 【実装内容】【決定事項】【対話履歴】の3セクション構成でgitコミットメッセージを作成する |
| [worktree-to-pr](./worktree-to-pr) | git worktreeの作成〜PR化〜後片付けまでのライフサイクルを支援する |
| [skill-help](./skill-help) | 利用可能なClaude Codeスキル一覧を表示する |

## インストール

各スキルのディレクトリを `~/.claude/skills/`（個人用）または `<project>/.claude/skills/`（プロジェクト用）にコピーしてください。

```bash
cp -r commit worktree-to-pr skill-help ~/.claude/skills/
```

## ライセンス

[GPLv3](./LICENSE)
