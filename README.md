# skills

自作の [Claude Code](https://docs.claude.com/claude-code) スキル集です。

## スキル一覧

| スキル | 概要 |
| --- | --- |
| [commit](./commit) | 【実装内容】【決定事項】【対話履歴】の3セクション構成でgitコミットメッセージを作成する |
| [worktree-to-pr](./worktree-to-pr) | git worktreeの作成〜PR化〜後片付けまでのライフサイクルを支援する |
| [skill-help](./skill-help) | 利用可能なClaude Codeスキル一覧を表示する |
| [nanobananer](./nanobananer) | Antigravity CLI(agy)の画像生成機能に安全に委譲し、プロジェクト内に画像を生成する |

## 各スキルの説明

### commit

gitコミットメッセージを、【実装内容】【決定事項】【対話履歴】の3セクション構成で作成するスキル。コードの差分だけでなく、会話の中で交わされた決定事項やその経緯まで残すことで、後から見た人が「なぜそうしたか」を追えるようにする。

### skill-help

skill-creatorを試すために適当に作ったスキル。`~/.claude/skills/`と`<project>/.claude/skills/`の両方から使えるスキル一覧（名前と説明）を表示する。

### nanobananer

「〇〇の画像を生成して」のように明示的に依頼されたときに使うスキル。Claude Codeが英語の画像生成プロンプトを組み立て、Antigravity CLI(`agy`)の画像生成機能に生成だけを委譲する。

- `agy`は常に`--add-dir`でプロジェクトルートのみに限定し、`--dangerously-skip-permissions`は付けない。範囲外への操作はagy自身の権限機構で自動的に拒否される
- 保存先パスはagyに指定させず、生成だけを依頼して`conversation_id`からagy自身の保存先を特定し、Claude Code側の権限でプロジェクトの素材フォルダへコピーする(保存先を直接指定させるとagyが内部でコマンド実行を試みて権限拒否され失敗するため)
- 保存先フォルダは会話の流れ・CLAUDE.md・既存構成から判断し、不明なら勝手に新規フォルダを作らずユーザーに確認する

### worktree-to-pr

並列セッションでの開発におすすめのスキル。

- 「ワークツリーを作る」のように言えば、`git worktree`で作業用のディレクトリを作ってくれる
- メイン側の会話で「PRしたい」のように言えば、push〜PR作成までやってくれる。PR作成後はベースブランチとのコンフリクトの有無も確認し、あれば自動修正するかどうかを確認してくれる
- 次回このスキルを使ったとき、前回のPRがマージ済みかを確認し、不要になった古いworktreeを消すか提案してくれる（もちろん、指示して即座に消すことも可能）。削除前には、そのworktreeでdevサーバー等のプロセスが動いていないかも確認してくれる
- lint・test等のコードチェックやpush前に立ち止まる判断はこのスキル自身では行わない。CLAUDE.mdやその場の会話でそうした指示をしておけば、このスキルの外側で（通常の会話の流れの中で）対応してくれる

## インストール

このリポジトリをcloneし、リポジトリのルートディレクトリで、使いたいスキルのディレクトリだけを `~/.claude/skills/`（個人用）または `<project>/.claude/skills/`（プロジェクト用）にコピーしてください。

```bash
git clone https://github.com/Ikenachi2023/skills.git
cd skills

# commit
cp -r commit ~/.claude/skills/

# skill-help
cp -r skill-help ~/.claude/skills/

# worktree-to-pr
cp -r worktree-to-pr ~/.claude/skills/

# nanobananer
cp -r nanobananer ~/.claude/skills/
```

## ライセンス

[GPLv3](./LICENSE)
