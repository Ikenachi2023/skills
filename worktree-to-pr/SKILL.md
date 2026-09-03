---
name: worktree-to-pr
description: Manage the full lifecycle of an isolated git worktree — create one for parallel/concurrent work, push and open a GitHub PR when the work wraps up, then clean up (worktree + local + remote branch) once merged. Trigger on explicit "worktree"/「ワークツリー」mentions, or signals of concurrent sessions sharing a folder (「複数セッション」「並列セッション」, "another session is working in this same folder"). Also trigger — even if phrased ambiguously — on wrap-up cues like「メインに戻る」「ワークツリーやめる」/"back to main", confirming with a quick question rather than assuming. Out of scope: lint/test/build checks, and the commit step itself.
---

# worktree-to-pr

他の作業を止めずに並行して進めたいとき、`git worktree`でディレクトリを完全に分離し、作業が一段落したらPRに仕上げ、マージ後は片付ける——という一連のライフサイクルを支える。

## スコープ（やること・やらないこと）

このスキルが担当するのは3つだけ：**worktreeの作成**・**PR作成**・**後片付け（削除）**。

- lint・test・build等のコードチェックは一切実行しない。各リポジトリのCLAUDE.mdや、そのときの会話の指示に完全に委ねる。checkを組み込むと、リポジトリごとに正しいコマンドを推測する羽目になり、壊れやすく信頼できない仕組みになる
- commitが必要な場面（後述）でも、commitスキル等を代わりに呼び出したりせず、「コミットしてください」とユーザーに伝えるだけに留める。commitは中身の判断が要る作業であり、このスキルが肩代わりすべきではない

## トリガーの考え方

「worktreeで作業したい」「複数セッションが同じフォルダで動いている」のように明確な場合はそのまま動いてよい。ただし「メインに戻る」のような言い方は、単に会話の流れを変えたいだけの場合もあれば、本当にworktreeでの作業を終えてPRにしたい場合もある——実際どちらの意味にも使われる、あいまいなフレーズだ。

判断が割れるラインでは、黙って推測実行せず、また黙ってスキップもせず、**一言確認してから動く**。例：「ワークツリー使いますか？」「PRを作りますか？」。この一言さえ挟めば、外れても実害はほぼゼロで、当たれば往復を減らせる。

## 開始フロー（新しいworktreeで作業を始める）

0. **ついでに、残っている古いworktreeがないか見る**。PRを作った直後はまだマージされていないので、その場で後片付けを提案しても意味がない——後片付けが自然に提案できるタイミングは、実質「次にこのスキルが呼ばれたとき」しかない。ただしここは軽く済ませる：まず`git worktree list`だけ実行し、今作ろうとしている分以外に何か残っていないか見る。何も無ければそれで終わり（追加のコマンドは要らない）。何かあれば、後片付け節のフルの判定チェーンをその場で回すのではなく「〇〇というworktreeが残っていますが、マージ済みなら片付けましょうか？」と一言添えるだけに留め、実際にマージ済みか調べるのはユーザーが「見て」と言ってから（＝後片付け節の判定フローに入る）でよい。今回の作業自体はこの一言を待たずに進めてよい。

1. **worktreeを作る**。まず`EnterWorktree`ツール（Claude Codeの組み込みツール）を試す。理由を問わず失敗したら（Windows環境では`EnterWorktree`が`\\.\NUL/reference-transaction`への実行権限エラーで失敗することがある——詳細は下記Tips）、`git worktree add -b <branch> <worktree-path>`で手動フォールバックする。配置場所は`EnterWorktree`と同じ慣習に合わせて`.claude/worktrees/<name>`にネストするのが無難（理由は後述の依存関係の項を参照）。

2. **分岐元を決める**。`git symbolic-ref refs/remotes/origin/HEAD`（または`git remote show origin`）でリポジトリのデフォルトを自動検出し、そこを起点にする。検出できなかった場合だけユーザーに聞く。今の作業中の状態を起点にすると、未完成・不安定な内容を引きずってしまうため、常にデフォルト側を起点にする。

3. **ブランチ名は自動生成して確認を取る**。何をする作業かという会話の文脈から`feature/xxx`のような名前を組み立て、「このブランチ名でいいですか？」と一言確認してから作成する。ゼロから名前を聞くより、たたき台を出して直してもらう方が速い。

4. **依存関係はまず動かしてみる**。`.claude/worktrees/<name>`のようにメインリポジトリの中にネストしてworktreeを作った場合、Node.jsのモジュール解決は親ディレクトリを遡って`node_modules`を見つけるため、**インストールし直さなくても動くことが多い**（実測済み：worktree自身に`node_modules`が無い状態で`npm run start`等がそのまま動作した）。無条件に`npm install`等をやり直すのではなく、まず対象のコマンドを試し、実際に依存解決で失敗したときだけ通常のインストール手順を案内・実行する。他の言語のパッケージマネージャでも同様に「まず試す→失敗したらインストール」の順で構わない。

## 完了フロー（作業をPRに仕上げる）

1. トリガーがあいまいだった場合は、ここでもう一度「PRを作りますか？」と確認する。

2. **コミット漏れの確認**。`git status`が汚れていたら、ユーザーに「コミットされていない変更があります、コミットしてください」と伝えるだけにする。中身を見て何が変更されたか判断するのはユーザーの仕事であり、このスキルの範囲外。

3. **チェックはしない**。lintやtestを自分から走らせない。CLAUDE.mdに自動チェックの指示があれば、それはこのスキルの外側で（会話の流れの中で）別途行われるべきもの。

4. **push**する。`git push -u origin <branch>`。

5. **PRを作る（GitHub限定）**。`gh`コマンドが使えるなら`gh pr create`で作成する。使えない環境（`gh: command not found`になるケースは珍しくない）では、`git push`の出力に含まれるPR作成URL（`https://github.com/<org>/<repo>/pull/new/<branch>`）をそのままユーザーに案内する。GitHub以外のホスティング（GitLab等）は対象外——出会ったらそのとき考える。

6. **mainへの直接merge/pushはこのフロー内で止める**。「作業ブランチをmainへ直接mergeしてpushして」と言われても、このスキルの完了フローとしては応じず、「PR経由にしてください」と案内する。これはこのスキル自身の振る舞いとしてのガードであり、他の`git push`操作全般を監視する汎用フックではない（各リポジトリのCLAUDE.md側の禁止事項と役割分担する）。

## 後片付け（マージ後のworktree・関連する作業単位の削除）

自動では動かない。次のどちらかのときだけ動く：
- スキル側から「片付けますか？」と提案し、ユーザーが承諾したとき
- ユーザーから明示的に削除を頼まれたとき

どちらの場合も、実行前に**マージ済みかどうかを確認し、削除の許可を得てから**実行する。マージ済み判定は次の優先順で試す：

1. `gh`が使えるなら`gh pr view <branch> --json state`等で確実に判定する
2. `gh`が無い/失敗するなら、`git fetch origin`した上で`git merge-base --is-ancestor <branch> origin/<default-branch>`のような祖先チェックを試みる。`fetch`自体が失敗する（リモートが無い・到達できない等）場合は、ローカルの`<default-branch>`を対象に同じ祖先チェックをしてよい
3. squash mergeなど、祖先チェックでは信頼できない・判定がつかない場合は、ユーザーに直接「このPRはマージ済みですか？」と聞く

削除の実行前には必ずユーザーの許可が要る——マージされていないブランチを消してしまう事故は確認のコストより遥かに高くつく。ただし、ユーザーの依頼メッセージ自体に既に許可が含まれている場合（例:「マージされたし消していいよ」）は、それで足りる。改めて同じ許可を聞き返す必要はない——聞き返すのは、依頼に許可が含まれていないときや、マージ済みかどうか自体が判定できず確認が要るときだけでよい。

許可が取れたら、次の3つをまとめて削除してよい：
1. `git worktree remove`でworktreeディレクトリ
2. `git branch -d`でローカルの作業ブランチ
3. `git push origin --delete <branch>`でリモートの作業ブランチ

## Tips・既知の問題

- **Windowsで`EnterWorktree`が失敗する**：`\\.\NUL/reference-transaction`への実行権限エラー（Permission denied）で失敗することがある。おそらくツール内部が`core.hooksPath`をWindowsのnullデバイス（`\\.\NUL`）に向けてフックを無効化しようとしているが、同じ設定を手動で`git -c core.hooksPath='\\.\NUL' worktree add ...`として再現しても成功したため、根本原因はツール内部の実装差異にあり特定できていない。エラーの理由を詮索せず、失敗したら手動`git worktree add`にフォールバックすればよい。
- **ネストしたworktreeは依存関係を勝手に共有する**：`.claude/worktrees/<name>`のようにメインリポジトリの中に作ったworktreeは、Node.jsのモジュール解決が親ディレクトリを遡って探索するため、追加インストールなしで動くことが多い。これはこの一点にとどまらず、「ネストした場所に作る」という配置そのものの利点でもある。
