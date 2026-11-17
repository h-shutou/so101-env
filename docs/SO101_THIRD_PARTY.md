# 第三者ソフトウェア・モデルの出典とライセンス

## 確認済みの上流リポジトリ

| 上流 | 利用箇所・関係 | ライセンス | 必要事項 |
|---|---|---|---|
| [ros-physical-ai/ros2_so_arm](https://github.com/ros-physical-ai/ros2_so_arm) | `ros2_ws/src/so_arm101_description` の基礎となったROS 2説明パッケージ、URDF/MJCF/メッシュ | **BSD 3-Clause** | 著作権表示、条件、免責条項を再配布物に残す |
| [TheRobotStudio/SO-ARM100](https://github.com/TheRobotStudio/SO-ARM100) | SO-101の元となった3D機械設計資料の主要出典 | **Apache License 2.0** | 原資料を含む／派生させる場合、Apache 2.0の条件、NOTICE、変更表示等の確認が必要 |

上流ライセンス全文の写し：
- `third_party_licenses/ros2_so_arm/LICENSE`
- `third_party_licenses/SO-ARM100/LICENSE`

これらの全文は元リポジトリのLICENSEをもとに配置しています。**プロジェクト独自コードのライセンスをBSDやApacheに自動的に設定するものではありません。**

## このプロジェクトでの変更

- MuJoCoの`so_arm101.xml`を白色表示・衝突メッシュ参照などに合わせて変更
- `workspace.xml`を追加してTop・Wristカメラと作業空間を定義
- `mjcf/collision/*.stl`に衝突判定用のハルメッシュを追加
- ROS 2のブリッジ、Launch、Mac一括起動スクリプトを追加

## 公開前に未確認の事項（必須）

**衝突判定用`mjcf/collision/*.stl`の生成元・使用元メッシュと権利関係を確認してください。** 現段階では、研究用の別リポジトリから移したことまでは分かりますが、その元データがBSDライセンスのROS 2パッケージ由来なのか、Apacheライセンスの設計資料由来なのか、あるいは別の権利者のものかを確定できていません。

具体的な手順：

1. STL生成元ファイル／自作スクリプト／加工手順を特定する。
2. 利用・改変・配布のライセンス条件と著作権表示を確認する。
3. 必要なNOTICE、変更表示、出典、ライセンス全文を収録する。
4. `so101_bringup/package.xml` の `UNLICENSED` を含め、独自コードの権利者と公開ライセンスを決める。
5. 借用したモデル・データが他にもあれば追加し、未許諾の素材は公開版から除外する。

**未確認のまま一般公開しないでください。** まずGitHubのPrivateリポジトリに保存し、権利関係と機密情報の監査後にPublicへ切り替える運用を推奨します。
