# SO-101 ロボット開発環境テンプレート

**SO-101を使ったロボット研究を始めるための、研究室共通の開発環境です。**

MuJoCoでのSO-101シミュレーション、ROS 2による関節制御、カメラ画像の取得、Foxgloveによる可視化をまとめています。研究室のLinuxサーバー（cicero）で計算を実行し、手元のMacから操作・確認できます。

> **現在の対象はシミュレーションです。** SO-101実機へのROS 2動作指令は未対応です。実機接続機能は別ブランチで検証中であり、このREADMEの起動手順で実機のモーターは動きません。

## この環境でできること

| 機能 | 状態 |
| --- | --- |
| SO-101（6関節）のMuJoCoシミュレーション | 利用可能 |
| ROS 2 Jazzyからのシミュレーション関節指令 | 利用可能 |
| 関節状態・Topカメラ・Wristカメラの配信 | 利用可能 |
| MacのFoxgloveで3Dモデルとカメラ画像を表示 | 利用可能 |
| ROS Domain IDとポートを分けたシミュレーションの同時起動 | 動作確認済み（同一Linuxアカウント内） |
| 異なるLinuxアカウント間での同時利用 | 未検証 |
| SO-101実機の関節状態取得・動作制御 | 開発・検証中（mainには未統合） |

### 構成

```text
Mac（Foxglove）
     │ SSHトンネル
     ▼
Linuxサーバー（cicero）
     ├─ ROS 2 Jazzy / Foxglove Bridge
     ├─ MuJoCo（SO-101のシミュレーション）
     ├─ 関節状態・カメラ画像の配信
     └─ ROS 2によるシミュレーション関節指令
```

Mac側にはROS 2やMuJoCoをインストールする必要はありません。

## 対応環境・事前準備

- **実行側：** Ubuntu Linux（x86_64）、EGLによるMuJoCo描画が利用できる環境。ciceroで動作確認しています。
- **開発環境：** [Pixi](https://pixi.sh/)でPython 3.12とROS 2 Jazzyなどの依存関係を管理します。
- **表示側：** macOS、SSH接続、[Foxglove](https://foxglove.dev/)。
- **研究室内利用：** GitHubのリポジトリ閲覧権限と、ciceroへのSSH接続権限が必要です。

**利用者ごとに自分のLinuxアカウント・作業ディレクトリを使用してください。** 以下のコマンドは、Linux側の配置先が `~/so101-robotics-env` であることを前提とします。Mac用起動スクリプトもこのパスを参照します。

## 1. GitHubから開発環境を取得する（Linux）

研究を新しく始める場合は、GitHubの **「Use this template」→「Create a new repository」** から自分用のリポジトリを作成してください。そのリポジトリをciceroにクローンします。

テンプレート自体を試す場合の例：

```bash
git clone git@github.com:m-ochilab/so101-robotics-env-template.git ~/so101-robotics-env
cd ~/so101-robotics-env
```

自分用リポジトリを作成した場合は、`git clone` のURLをそのリポジトリのURLに置き換えます。**研究室共通のテンプレートへ個人の実験コードを直接pushしないでください。**

## 2. ROS 2・MuJoCo環境を準備する（Linux）

Pixiが未導入の場合のみ、インストールします。

```bash
curl -fsSL https://pixi.sh/install.sh | sh
~/.pixi/bin/pixi --version
```

次に、依存関係を導入し、ROS 2パッケージをビルドします。

```bash
cd ~/so101-robotics-env/ros2_ws

~/.pixi/bin/pixi install --locked

~/.pixi/bin/pixi run colcon build \
  --packages-select so_arm101_description so101_bringup \
  --symlink-install
```

成功すると、`Summary: 2 packages finished` などと表示されます。依存関係の初回導入では時間やディスク容量が必要です。

詳しい導入手順・確認方法は [セットアップガイド](docs/SO101_SETUP.md) を参照してください。

## 3. シミュレーションを起動する（Linux）

**注意：** 以下の `73`（ROS Domain ID）と `18765`（Foxgloveポート）は**動作確認用の例**です。共有サーバーで利用する際は、他の利用者と重複しない値に変更してください。

```bash
cd ~/so101-robotics-env/ros2_ws

~/.pixi/bin/pixi run bash -c '
source install/setup.bash
export ROS_DOMAIN_ID=73
export ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST
ros2 launch so101_bringup simulation_multi.launch.py foxglove_port:=18765
'
```

起動中はこのターミナルを開いたままにします。停止するには `Ctrl+C` を押します。

ROS 2で配信される主なトピック：

| トピック | 内容 |
| --- | --- |
| `/joint_states` | シミュレーションの関節角度・速度 |
| `/camera/top/image_raw` | 上方カメラ画像 |
| `/camera/wrist/image_raw` | 手首カメラ画像 |
| `/robot_description` | SO-101のロボットモデル |
| `/so101_controller/joint_trajectory` | **シミュレーション専用**の関節軌道指令入力 |

別のLinuxターミナルから関節状態を確認する例：

```bash
cd ~/so101-robotics-env/ros2_ws

ROS_DOMAIN_ID=73 ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST \
  ~/.pixi/bin/pixi run ros2 topic echo /joint_states --once
```

## 4. Macから起動・可視化する

MacからSSHでciceroに接続し、シミュレーションの起動とFoxgloveへの転送をまとめて行えます。

1. Macにもこのリポジトリをクローンするか、`scripts/mac/start-so101-multi.sh` と設定例を取得する。
2. 研究室の接続方法に沿って `~/.ssh/config-so101` を準備する（踏み台・鍵などは個人で設定）。
3. Macのリポジトリ直下で、設定ファイルを作成する。

```bash
mkdir -p ~/.config/so101
cp config/mac/sim.env.example ~/.config/so101/sim.env
nano ~/.config/so101/sim.env
```

設定する主な項目：

| 項目 | 説明 | 設定例 |
| --- | --- | --- |
| `SO101_DOMAIN_ID` | 自分専用のROS Domain ID | `73` |
| `SO101_REMOTE_PORT` | cicero側のFoxgloveポート | `18765` |
| `SO101_LOCAL_PORT` | Mac側の接続ポート | `18766` |
| `SO101_SSH_HOST` | SSH接続先の名前 | `cicero` |
| `SO101_SSH_CONFIG` | SSH設定ファイル | `~/.ssh/config-so101` 相当 |

設定後、Macのリポジトリ直下で起動します。

```bash
./scripts/mac/start-so101-multi.sh
```

Foxgloveで **`ws://localhost:18766`**（ローカルポートを18766にした場合）へ接続します。3Dパネルで `/robot_description` と `/joint_states` を設定し、画像パネルでTop/Wristカメラを表示できます。メッシュの向きがずれる場合は、3DパネルのMesh up-axisを **Z-up** に設定してください。

**Linuxで手動起動する方法（手順3）とMacから一括起動する方法（手順4）は、同じシミュレーションを対象にする場合どちらか一方を使用してください。** 両方実行するとポート重複などが起こる可能性があります。

## 複数人で使う場合

1. 各利用者が自分のLinuxアカウントと `~/so101-robotics-env` を使用する。
2. **`ROS_DOMAIN_ID` とcicero側のFoxgloveポートを利用者ごとに分ける。**
3. 同じMacで同時表示する場合はMac側のローカルポートも分ける。
4. 実験結果・録画・個人設定はGitHubのテンプレートにコミットしない。

設定例は [`config/multi_user_allocations.example.csv`](config/multi_user_allocations.example.csv)、運用方法は [複数人利用ガイド](docs/SO101_MULTI_USER.md) にあります。

`ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST` はネットワーク上のROS自動発見範囲を制限する設定で、同じLinux上の利用者同士を隔離するものではありません。ROS Domain IDもアクセス制御・セキュリティ機構ではありません。

## SO-101実機への対応状況

現在の `main` は**MuJoCo用**です。実機のUSB接続、校正JSONの照合、実機からの関節状態取得、動作指令については段階的に検証しています。

- シミュレーション用の関節指令を、実機のモーターに流用しないでください。
- 実機とUSBの接続先・アクセス権限・LeRobotの校正情報は、現地で確認する必要があります。
- 実機は複数人が同時に制御せず、管理者の許可と安全確認の下で使用してください。

## よくあるトラブル

| 症状 | 最初に確認すること |
| --- | --- |
| `pixi: command not found` | `~/.pixi/bin/pixi` を使っているか |
| ROS 2パッケージが見つからない | `colcon build` が完了したか、`install/setup.bash` を読み込んだか |
| Foxgloveにつながらない | シミュレーションが起動中か、SSHトンネルとポート番号が合っているか |
| `Address already in use` | 他の利用者・SSH設定とポートが重複していないか |
| 3Dモデルの表示が崩れる | FoxgloveのMesh up-axisをZ-upにしているか |
| カメラ画像が表示されない | `/camera/top/image_raw` / `/camera/wrist/image_raw` が配信されているか |

その他の対処方法は [セットアップガイド](docs/SO101_SETUP.md) を参照してください。

## 主なファイル・資料

```text
so101-robotics-env/
├── ros2_ws/
│   ├── pixi.toml / pixi.lock          # ROS 2とMuJoCoの依存関係
│   └── src/
│       ├── so_arm101_description/     # URDF・MJCF・メッシュ
│       └── so101_bringup/            # ROS 2ノード・Launch
├── scripts/mac/                       # Macからの起動スクリプト
├── config/                            # 個人設定のサンプル
├── docs/                              # セットアップ・運用ガイド
├── third_party_licenses/             # 第三者ライセンス
└── tools/check-share-ready.sh        # 共有前の簡易確認
```

- [詳しいセットアップ・起動手順](docs/SO101_SETUP.md)
- [複数人・複数シミュレーションの運用](docs/SO101_MULTI_USER.md)
- [第三者素材の出典とライセンス](docs/SO101_THIRD_PARTY.md)
- [公開前チェックリスト](docs/SO101_RELEASE_CHECKLIST.md)

## ライセンス・公開に関する注意

ROS 2の説明パッケージやロボットモデルには第三者由来の素材が含まれます。ライセンス表示は `third_party_licenses/` に収録していますが、**衝突判定用STLの出典・再配布条件と独自コードのライセンスは未確定**です。

これらの確認と、新しいLinuxアカウントでのクリーンクローン動作検証が完了するまで、リポジトリは **Private** のまま運用してください。詳しくは [公開前チェックリスト](docs/SO101_RELEASE_CHECKLIST.md) を参照してください。
