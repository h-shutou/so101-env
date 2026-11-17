# SO-101 開発環境：セットアップと起動

## 前提

- **シミュレーション実行側:** Ubuntu Linux x86_64、MuJoCoのEGL描画が利用可能な環境（ciceroで動作確認）
- **可視化側:** macOS、SSHクライアント、Foxgloveアプリ
- **ROS 2:** Jazzy、Pixi/RoboStack環境（`ros2_ws/pixi.toml` と `pixi.lock` で管理）
- **実機:** 不要。ここで説明する内容はMuJoCo専用で、ロボットのモーターを動かしません。

## 1. Linux側に配置する

GitHubへ公開したリポジトリを、自分のLinuxアカウントにクローンします。

```bash
git clone https://github.com/m-ochilab/so101-robotics-env-template.git ~/so101-robotics-env
cd ~/so101-robotics-env/ros2_ws
```

`OWNER` は公開後のGitHubユーザー名／Organization名に置き換えてください。各利用者は**共有ディレクトリではなく、それぞれのホームディレクトリ**にクローンしてください。

### Pixiを導入

すでにPixiを利用できる場合は省略できます。インストール手順は [Pixi公式](https://pixi.sh/latest/installation/) を参照してください。

```bash
curl -fsSL https://pixi.sh/install.sh | sh
~/.pixi/bin/pixi --version
```

### 依存関係の導入とROS 2ビルド

```bash
cd ~/so101-robotics-env/ros2_ws
~/.pixi/bin/pixi install --locked
~/.pixi/bin/pixi run colcon build \
  --packages-select so_arm101_description so101_bringup \
  --symlink-install
```

**注:** `--locked` は追跡中の`pixi.lock`とマニフェストの整合性を検査します。利用OS／アーキテクチャが `pixi.toml` の対応対象外なら、依存関係導入が失敗します。

### パッケージとモデルの検証

```bash
cd ~/so101-robotics-env/ros2_ws
~/.pixi/bin/pixi run bash -c '
source install/setup.bash
ros2 pkg executables so101_bringup
'
~/.pixi/bin/pixi run python - <<'PY'
from pathlib import Path
import mujoco
scene = Path('install/so_arm101_description/share/so_arm101_description/mjcf/workspace.xml')
model = mujoco.MjModel.from_xml_path(str(scene.resolve()))
print('MuJoCo load OK', 'joints=', model.njnt, 'cameras=', model.ncam)
PY
```

## 2. Linuxで単独起動して確認する

同じcicero上の別利用者と重複しないROS Domain IDおよびFoxglove用ポートを、事前に割り当ててください。下の値は既存実験用の例です。

```bash
cd ~/so101-robotics-env/ros2_ws
~/.pixi/bin/pixi run bash -c '
source install/setup.bash
export ROS_DOMAIN_ID=73
export ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST
ros2 launch so101_bringup simulation_multi.launch.py foxglove_port:=18765
'
```

このターミナルは起動したままにします。停止は `Ctrl+C`。`SO-101 MuJoCo bridge started (simulation only)` とFoxgloveのポート待受ログを確認します。

**重要:** ROS_DOMAIN_ID 73／リモート18765は既存利用者のサンプル番号です。同じサーバーでほかのユーザーが使っているなら使い回さないでください。

## 3. Macから一括起動する

Macでも本リポジトリを取得するか、`scripts/mac/start-so101-multi.sh` を安全にコピーしてください。MacにROS 2やMuJoCoをインストールする必要はありません。

```bash
# Macで実行
mkdir -p ~/.config/so101
cp config/mac/sim.env.example ~/.config/so101/sim.env
```

`~/.config/so101/sim.env` の `SO101_DOMAIN_ID`、`SO101_REMOTE_PORT`、`SO101_LOCAL_PORT`、`SO101_SSH_HOST`、`SO101_SSH_CONFIG` を自分の環境に合わせて書き換えます。ファイルはGitに追加しません。

```bash
# MacからSSH接続の事前確認
ssh -F ~/.ssh/config-so101 cicero 'hostname'

# Macのリポジトリ直下から
./scripts/mac/start-so101-multi.sh
```

Macとciceroで同じリポジトリをクローンしていても、それぞれ独立したディレクトリです。Mac側ではスクリプトのみ使用し、Linux側でPixiとROS 2を動かします。

### SSH設定の注意

`-F /dev/null` は踏み台・認証などの必要な設定も無視して接続失敗する場合があります。Macの利用者は、必要な接続設定を含みつつ不要なポート転送を除外した `~/.ssh/config-so101` を自分で準備してください。**SSH秘密鍵や設定ファイルはリポジトリに含めません。**

### Foxglove

MacでFoxgloveアプリを開き、WebSocket接続先 `ws://localhost:18766`（`SO101_LOCAL_PORT=18766` の例）を指定します。

- 3Dモデル：URDFを`/robot_description`から読み込み、Joint Statesを`/joint_states`から参照
- Mesh up-axis：モデルが分解表示される場合、Foxglove 3Dパネルの **Z-up** を選択
- カメラ：`/camera/top/image_raw` と `/camera/wrist/image_raw`

## 4. 制御と状態確認（MuJoCoのみ）

```bash
cd ~/so101-robotics-env/ros2_ws
ROS_DOMAIN_ID=73 ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST \
  ~/.pixi/bin/pixi run ros2 topic echo /joint_states --once
```

対象Domainへ、シミュレーション用関節指令を送信する例：

```bash
ROS_DOMAIN_ID=73 ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST \
~/.pixi/bin/pixi run ros2 topic pub --once \
  /so101_controller/joint_trajectory trajectory_msgs/msg/JointTrajectory \
  '{joint_names: [shoulder_pan_joint, shoulder_lift_joint, elbow_flex_joint, wrist_flex_joint, wrist_roll_joint, gripper_joint], points: [{positions: [0.3, 0, 0, 0, 0, 0], time_from_start: {sec: 3}}]}'
```

## よくあるトラブル

- `pixi: command not found`：`~/.pixi/bin/pixi` を使用する
- `executable ... not found`：Pythonエントリーポイントの実行権限を確認して再ビルド
- `Error opening ... collision/...stl`：説明パッケージに衝突メッシュ一式が含まれるか確認
- `bind ... Address already in use`：他の利用者とFoxgloveポートが重複していないか、SSH設定に不要なポート転送がないか確認
- `Connection refused`：cicero側のFoxglove Bridgeが起動しているか確認
- 3Dモデルが分解表示：FoxgloveのMesh up-axisをZ-upに設定

依存関係が最新OSで常に再現できる保証はありません。公開前に**新しいLinuxアカウントへのクローン、Pixi導入、ビルド、起動**を通して検証してください。
