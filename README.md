# skills

自作の [Claude Code](https://docs.claude.com/claude-code) スキル集です。

## スキル一覧

| スキル | 概要 |
| --- | --- |
| [commit](./commit) | 【実装内容】【決定事項】【対話履歴】の3セクション構成でgitコミットメッセージを作成する |
| [worktree-to-pr](./worktree-to-pr) | git worktreeの作成〜PR化〜後片付けまでのライフサイクルを支援する |
| [skill-help](./skill-help) | 利用可能なClaude Codeスキル一覧を表示する |

## 各スキルの説明

### commit

gitコミットメッセージを、【実装内容】【決定事項】【対話履歴】の3セクション構成で作成するスキル。コードの差分だけでなく、会話の中で交わされた決定事項やその経緯まで残すことで、後から見た人が「なぜそうしたか」を追えるようにする。

### skill-help

skill-creatorを試すために適当に作ったスキル。`~/.claude/skills/`と`<project>/.claude/skills/`の両方から使えるスキル一覧（名前と説明）を表示する。

### worktree-to-pr

並列セッションでの開発におすすめのスキル。

- 「ワークツリーを作る」のように言えば、`git worktree`で作業用のディレクトリを作ってくれる
- メイン側の会話で「PRしたい」のように言えば、push〜PR作成までやってくれる
- 次回このスキルを使ったとき、前回のPRがマージ済みかを確認し、不要になった古いworktreeを消すか提案してくれる（もちろん、指示して即座に消すことも可能）
- lint・test等のコードチェックやpush前に立ち止まる判断はこのスキル自身では行わない。CLAUDE.mdやその場の会話でそうした指示をしておけば、このスキルの外側で（通常の会話の流れの中で）対応してくれる

## インストール

使いたいスキルのディレクトリだけを `~/.claude/skills/`（個人用）または `<project>/.claude/skills/`（プロジェクト用）にコピーしてください。

```bash
# commit
cp -r commit ~/.claude/skills/

# skill-help
cp -r skill-help ~/.claude/skills/

# worktree-to-pr
cp -r worktree-to-pr ~/.claude/skills/
```

## ライセンス

[GPLv3](./LICENSE)
