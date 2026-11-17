# GitHub公開前チェックリスト

- [ ] GitHub共有対象が `so101-robotics-env` であり、卒業研究の別リポジトリを操作していない
- [ ] 動作確認済みコミットまでGitに保存した
- [ ] `.pixi/`、`build/`、`install/`、`log/`、`__pycache__/`、`*.pyc`、認証鍵、個人情報、実機の校正ファイル、録画データを含まない
- [ ] `git remote -v` の接続先・公開先アカウントを確認した
- [ ] Git履歴全体に秘密情報・個人情報・未許諾素材が入っていない（現在の`.gitignore`だけでは履歴を消せない）
- [ ] 依存関係の`pixi.toml`と`pixi.lock`が整合し、新規Linuxアカウントで`pixi install --locked`が成功
- [ ] 新規クローンから`colcon build`が成功し、MuJoCoモデル読み込みとFoxglove表示ができる
- [ ] 個別Linuxアカウント2名で、ドメインとFoxgloveポートを分離して同時起動できる
- [ ] 複数人利用時のCPU/GPU使用量を確認
- [ ] 上流 `ros2_so_arm` のBSD 3-Clause表示・ライセンス全文を含む
- [ ] 必要に応じてTheRobotStudio SO-ARM100のApache 2.0表示・NOTICE・変更履歴を含む
- [ ] 衝突ハルSTLの生成元・再配布条件を確認済み
- [ ] 独自コードの公開ライセンス、`so101_bringup/package.xml` のライセンス表示を決定
- [ ] READMEと`docs/`内の説明を実際の起動手順で検証
- [ ] 検査が終わるまでGitHubリポジトリはPrivateに設定

## 簡易監査

```bash
cd ~/so101-robotics-env
bash tools/check-share-ready.sh

git status --short
git remote -v
git ls-files | grep -Ei '(\.pem$|\.key$|^\.env$|/\.env$|id_(rsa|ed25519)|calibrat|\.bag$|\.db3$|\.mcap$)' || true
```

この簡易監査だけでは情報漏えいやライセンス問題の不存在は証明できません。コミット履歴も確認してください。

## GitHubへ保存する

`gh` が使用できる場合、**Private**リポジトリで最初に保存します。

```bash
cd ~/so101-robotics-env
gh auth status
gh repo create OWNER/so101-robotics-env --private --source=. --remote=origin --push
```

`OWNER`は自分のGitHubユーザー名に置き換えてください。`gh`がない場合はGitHubの画面で**空のPrivateリポジトリ**を作り、GitHubで表示されるURLを使って以下を実行します。

```bash
cd ~/so101-robotics-env
git remote add origin git@github.com:OWNER/so101-robotics-env.git
git push -u origin main
```

既存の`origin`がある場合は上書きせず、接続先を確認してください。一般公開はチェックリストを完了した後にGitHubのRepository Settingsから行います。
