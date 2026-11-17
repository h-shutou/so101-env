# cicero上の複数人・複数シミュレーション運用

## 原則

**GitHubリポジトリは共通、Linuxログインアカウント・作業ディレクトリ・MuJoCoプロセス・ROS Domain ID・Foxgloveサーバーポートは利用者ごとに分離**します。

同じcicero上でも異なるROS Domain IDなら、通常は異なるROSグラフとして発見・通信が分かれます。`ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST` はネットワーク上の発見範囲を制限するもので、**同じホスト内の別の利用者を隔離する設定ではありません**。ROS Domain IDはセキュリティ機構ではありません。

| 項目 | 利用者A（検証例） | 利用者B（検証例） |
|---|---|---|
| Linux作業パス | `/home/USER_A/so101-robotics-env` | `/home/USER_B/so101-robotics-env` |
| ROS_DOMAIN_ID | `73` | `74` |
| cicero側Foxglove Port | `18765` | `18767` |
| Mac側Port | `18766` | `18766`（別のMacであれば同じでよい） |
| MuJoCo | 個別プロセス | 個別プロセス |

**使用前に重複確認:** 上記ID/ポートは動作実績の例で、実際の利用者への恒久的な割り当てではありません。研究室内で管理者が番号を管理することを推奨します。共有Linuxアカウントや共有データディレクトリは避けてください。

## 割り当ての記録

GitHubには `config/multi_user_allocations.example.csv` の**例だけ**を置きます。実際の利用者名・割り当て情報は研究室で管理するファイルやアクセス制限した場所に保存します。

- `ROS_DOMAIN_ID` は同じcicero上で重複しない番号を使用（この環境では候補を0〜101に制限）
- リモートFoxgloveポートは同じcicero上で重複禁止
- Macのローカルポートは同じMac内で重複禁止
- 別のLinuxアカウントの`~/so101-robotics-env`へ直接書き込まない
- ロボット実機のUSBデバイスを複数人で同時に制御しない

### Mac側設定の例

```bash
mkdir -p ~/.config/so101
cp config/mac/sim.env.example ~/.config/so101/sim.env
# 例を編集して、自分に割り当てられた値だけを記入
# 秘密鍵や認証情報は記載しない
./scripts/mac/start-so101-multi.sh
```

## 同時起動の検証

まず別々の環境でAとBを起動し、それぞれ`/joint_states`を取得します。

```bash
# ciceroのターミナル（A）
ROS_DOMAIN_ID=73 ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST \
~/.pixi/bin/pixi run ros2 topic echo /joint_states --once

# ciceroのターミナル（B）
ROS_DOMAIN_ID=74 ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST \
~/.pixi/bin/pixi run ros2 topic echo /joint_states --once
```

Aにのみ0.3 radの関節指令を送信した後、A=約0.3、B=約0を確認。次にBにのみ0.2 radを送り、A=約0.3、B=約0.2を確認します。

このテストは、**2026-11-12に同一Linuxアカウント内の2つのMuJoCoプロセスで成功**しました。**異なるLinuxアカウント同士の権限・資源分離、GPUメモリ容量、複数名での再現性は未検証**です。

## 制限と運用上の注意

1. `ROS_DOMAIN_ID` は完全なセキュリティ境界ではありません。アクセス権や外部ネットワーク保護は別に必要です。
2. CPU/GPU/メモリはcicero全体で共有され、複数プロセスを同時に実行すると重くなります。利用者は実験時に使用量を確認してください。
3. 実験ログ、録画、学習データは自分のホームディレクトリに出力してください。
4. `localhost`の18765などはciceroの待受ポートです。不要な外部公開はしないでください。
5. 実機使用は単一の操作主体が占有し、管理者による許可と安全確認の後に開始してください。現時点のパッケージは実機制御未対応です。
