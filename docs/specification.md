# SpecMatrix 仕様案

## 1. コンセプト

SpecMatrix は、組み込み開発向けの **仕様駆動テスト妥当性管理システム** である。

従来のテスト管理ツールが主に「作成済みテストケースの管理」を中心にしていたのに対し、SpecMatrix は次の問いに答えることを目的とする。

> このテスト設計で、仕様・構成・状態・異常系・過去不具合を十分に検証できているか。

そのため、単なるテストケース管理ではなく、以下を統合して扱う。

- 要求解析
- ハードウェア構成管理
- 状態遷移・I/O・通信仕様のモデル化
- テストケースとのトレーサビリティ
- ルールベース検査
- AI によるテスト観点レビュー
- 実施結果とエビデンス管理

## 2. 目的

SpecMatrix の目的は、組み込み開発で起きやすいテスト漏れを早期に検出し、テスト設計の妥当性を説明可能な形で管理することである。

特に次のような不足を検出する。

- 仕様要求に対応するテストケースが存在しない
- 異常系、境界値、タイミング条件の観点が不足している
- ハードウェア差分や部品差分を考慮したテスト条件が不足している
- 状態遷移の一部状態・イベントが未検証である
- 通信断、電源断、センサー異常などの組み込み固有リスクが未試験である
- 過去不具合に対する再発防止テストが存在しない
- テストケースは存在するが、期待結果や条件が曖昧である

## 3. 想定ユーザー

- 組み込みソフトウェアエンジニア
- QA エンジニア
- テスト設計者
- システム設計者
- 機能安全・品質保証担当者
- プロジェクトリーダー

## 4. 基本ワークフロー

```text
仕様書
ハードウェア構成
状態遷移
I/O一覧
通信仕様
安全要求
過去不具合
    ↓
要求抽出・構造化
    ↓
AI / ルール / モデル解析
    ↓
テスト観点の抽出
網羅性チェック
矛盾検出
未試験リスク検出
    ↓
テストケース生成・レビュー
    ↓
実施管理・エビデンス管理
```

## 5. 最小構成

初期バージョンでは、以下の機能を MVP とする。

1. 仕様書を Markdown / Asciidoc / Word / PDF から取り込む
2. 要求を ID 付きで抽出・管理する
3. ハードウェア構成を YAML で定義する
4. テストケースを ID 付きで管理する
5. 要求とテストケースの対応表を作成する
6. AI とルールベース検査により、未対応要求や弱い異常系を指摘する
7. 指摘理由、根拠、推奨テストケースを説明可能な形で表示する

## 6. 入力データ

### 6.1 仕様書

仕様書は以下の形式をサポートする。

- Markdown
- Asciidoc
- Word
- PDF
- プレーンテキスト

仕様書からは、要求、制約、条件、例外、状態、I/O、通信、タイミング、安全要求を抽出する。

抽出された要求には、システム内で安定した ID を付与する。

```yaml
requirements:
  - id: REQ-POWER-001
    title: Low voltage recovery
    source: spec.md#3.2.1
    text: The device shall recover communication after low voltage is cleared.
    category: power
    risk: high
```

### 6.2 ハードウェア構成

ハードウェア構成は YAML で定義する。

```yaml
boards:
  - name: main_board_revA
    mcu: STM32F407
    sensors:
      - temperature
      - pressure
    interfaces:
      - UART
      - CAN
      - GPIO

  - name: main_board_revB
    mcu: STM32F407
    sensors:
      - temperature
      - pressure
      - current
    interfaces:
      - UART
      - CAN
      - GPIO
      - SPI

power:
  modes:
    - normal
    - low_voltage
    - sudden_shutdown

environment:
  temperature:
    min: -20
    max: 85
    unit: celsius
```

### 6.3 状態遷移

状態遷移は YAML または表形式で定義する。

```yaml
states:
  - boot
  - idle
  - measuring
  - communicating
  - error
  - shutdown

transitions:
  - from: boot
    event: boot_completed
    to: idle
  - from: measuring
    event: sensor_error
    to: error
  - from: communicating
    event: can_timeout
    to: error
```

### 6.4 テストケース

テストケースは ID、目的、前提条件、手順、期待結果、対象要求、対象構成を持つ。

```yaml
test_cases:
  - id: TC-POWER-LOW-RECOVERY
    title: Low voltage recovery during CAN communication
    requirements:
      - REQ-POWER-001
    boards:
      - main_board_revA
      - main_board_revB
    conditions:
      power: low_voltage
      interface: CAN
    steps:
      - Start CAN communication.
      - Drop supply voltage below threshold.
      - Restore supply voltage.
    expected:
      - Device resumes CAN communication within the specified recovery time.
```

### 6.5 過去不具合

過去不具合は、再発防止テストの有無を確認するための入力として扱う。

```yaml
defects:
  - id: BUG-2024-017
    title: CAN communication did not recover after low voltage event
    affected_boards:
      - main_board_revA
    related_requirements:
      - REQ-POWER-001
    required_regression_test: true
```

## 7. 主要機能

### 7.1 要求抽出

仕様書から要求候補を抽出し、ユーザーが確認・修正できるようにする。

抽出対象は以下とする。

- 機能要求
- 非機能要求
- 安全要求
- 異常系要求
- タイミング要求
- 境界値
- 通信仕様
- 電源条件
- センサー条件
- ハードウェア依存条件

AI は要求候補を抽出するが、最終的な確定はユーザー操作で行う。

### 7.2 トレーサビリティ管理

要求、テストケース、ハードウェア構成、過去不具合を関連付ける。

代表的な対応関係は以下とする。

```text
要求 ↔ テストケース
要求 ↔ ハードウェア構成
要求 ↔ 状態遷移
要求 ↔ 過去不具合
テストケース ↔ 実施結果
テストケース ↔ エビデンス
```

### 7.3 網羅性チェック

次の観点で網羅性を確認する。

- すべての要求にテストケースが紐付いているか
- すべての高リスク要求に異常系テストが存在するか
- すべての電源モードで必要な機能が確認されているか
- すべての通信インターフェースで正常系・異常系が確認されているか
- すべての状態とイベントの組み合わせが確認されているか
- すべての対象ボードで必要なテストが実施されているか
- 過去不具合に対する再発防止テストが存在するか

### 7.4 組み込み向けレビュー観点

初期ルールセットでは、以下の観点を標準で提供する。

| 観点 | チェック内容 |
| --- | --- |
| 機能要求 | 要求ごとにテストケースが存在するか |
| 異常系 | 電源断、通信断、センサー異常、タイムアウトを確認しているか |
| HW 構成 | ボード差分、部品差分、インターフェース差分を考慮しているか |
| 状態遷移 | 全状態、全イベント、異常遷移を通っているか |
| 境界値 | 電圧、温度、タイミング、バッファ長、閾値を確認しているか |
| 過去不具合 | 再発防止テストが存在するか |
| 通信 | 切断、遅延、再送、CRC 異常、バスオフを確認しているか |
| 電源 | 低電圧、瞬断、復帰、起動中断を確認しているか |
| センサー | 未接続、固定値、異常値、ノイズを確認しているか |

### 7.5 AI レビュー

AI レビューは、仕様、構成、テストケースを入力として、テスト設計の不足を指摘する。

ただし、AI の出力は単独の判断結果として扱わず、必ず根拠を持つレビュー項目として保存する。

出力形式は以下を基本とする。

```yaml
findings:
  - id: FINDING-POWER-001
    severity: high
    title: Low voltage communication recovery test is missing
    finding: 低電圧時の通信復帰試験が不足しています。
    evidence:
      - 仕様書 3.2.1 に低電圧復帰要件があります。
      - HW 構成に power.low_voltage があります。
      - 既存テストケースに low_voltage と CAN recovery を同時に扱う条件がありません。
    recommendation:
      action: add_test_case
      suggested_id: TC-POWER-LOW-RECOVERY
      description: 低電圧解除後に CAN 通信が規定時間内に復帰することを確認する。
    linked_requirements:
      - REQ-POWER-001
```

### 7.6 ルールベース検査

説明可能性と再現性を確保するため、AI だけでなくルールベース検査を併用する。

例:

```yaml
rules:
  - id: RULE-REQ-HAS-TEST
    description: Every requirement must have at least one linked test case.
    severity: high

  - id: RULE-POWER-MODE-COVERAGE
    description: Every declared power mode must be covered by at least one test case when power behavior requirements exist.
    severity: medium

  - id: RULE-DEFECT-REGRESSION
    description: Every past defect marked as requiring regression must have a linked regression test.
    severity: high
```

### 7.7 テストケース生成支援

不足が検出された場合、AI はテストケース案を生成する。

生成されるテストケース案には、以下を含める。

- テスト ID 案
- タイトル
- 対象要求
- 対象ボード
- 前提条件
- 入力条件
- 手順
- 期待結果
- 必要な計測・ログ
- 推奨エビデンス

AI が生成したテストケースは、ユーザーが承認するまで正式なテストケースとして扱わない。

### 7.8 実施管理

テストケースの実施状態を管理する。

```yaml
executions:
  - test_case_id: TC-POWER-LOW-RECOVERY
    result: pass
    tester: user@example.com
    executed_at: 2026-05-26T10:00:00+09:00
    environment:
      board: main_board_revB
      firmware: v1.4.2
      toolchain: gcc-arm-none-eabi-12
    evidence:
      - logs/can_recovery_20260526.log
      - images/power_waveform_20260526.png
```

### 7.9 エビデンス管理

テスト実施結果に紐付くログ、波形、スクリーンショット、シリアル出力、CI 結果を管理する。

初期バージョンでは、ファイルパスまたは URL の参照管理を行う。

## 8. 画面案

### 8.1 ダッシュボード

- 要求数
- テストケース数
- 未対応要求数
- 高リスク未対応数
- AI 指摘数
- ルール違反数
- 実施済みテスト数
- 失敗テスト数

### 8.2 要求一覧

- 要求 ID
- タイトル
- 種別
- リスク
- 参照元
- 紐付くテストケース
- カバレッジ状態

### 8.3 テストケース一覧

- テスト ID
- タイトル
- 対象要求
- 対象ボード
- 条件
- 実施状態
- 最終実施結果

### 8.4 カバレッジマトリクス

要求とテストケースの対応表を表示する。

```text
                 TC-001  TC-002  TC-003
REQ-POWER-001      x              x
REQ-CAN-002               x       x
REQ-SENSOR-003
```

空欄の要求は未対応候補として強調する。

### 8.5 AI レビュー画面

- 指摘
- 重要度
- 根拠
- 関連要求
- 関連テストケース
- 推奨対応
- 承認、保留、却下

## 9. データモデル概要

```text
Project
  ├─ SpecificationDocument
  ├─ Requirement
  ├─ HardwareConfiguration
  ├─ StateMachine
  ├─ TestCase
  ├─ TestExecution
  ├─ Evidence
  ├─ Defect
  ├─ Rule
  └─ Finding
```

主要エンティティの関係は以下とする。

```text
Requirement 1..* ↔ 0..* TestCase
Requirement 0..* ↔ 0..* HardwareConfiguration
Requirement 0..* ↔ 0..* Defect
TestCase 1 ↔ 0..* TestExecution
TestExecution 1 ↔ 0..* Evidence
Finding 1 ↔ 0..* Requirement
Finding 1 ↔ 0..* TestCase
```

## 10. 非機能要件

### 10.1 説明可能性

すべての指摘には、根拠、参照元、対象データ、推奨対応を含める。

### 10.2 再現性

ルールベース検査は、同じ入力に対して同じ結果を返す。

AI レビュー結果についても、使用モデル、プロンプトバージョン、入力データのハッシュを保存する。

### 10.3 監査性

要求、テストケース、AI 指摘、承認操作、却下操作の変更履歴を保持する。

### 10.4 拡張性

プロジェクトごとにルールセットを追加できる。

### 10.5 セキュリティ

仕様書や不具合情報には機密情報が含まれるため、以下を考慮する。

- ローカル実行モード
- オンプレミス LLM 対応
- 外部 AI API 利用時の送信範囲制御
- プロジェクト単位のアクセス制御
- エビデンスファイルの権限管理

## 11. CLI 案

初期実装では CLI を提供し、CI から実行できるようにする。

```bash
specmatrix init
specmatrix import-spec docs/spec.md
specmatrix validate
specmatrix review --ai
specmatrix coverage
specmatrix suggest-tests
```

出力例:

```text
Coverage Summary
----------------
Requirements: 128
Test cases: 214
Uncovered requirements: 9
High risk uncovered requirements: 3
Hardware condition gaps: 4
Past defect regression gaps: 2
```

## 12. CI 連携

CI 上で `specmatrix validate` を実行し、以下の条件を検出できるようにする。

- 高リスク要求にテストケースがない
- 必須ルールに違反している
- 過去不具合の再発防止テストが削除された
- 仕様変更により要求が追加されたが、テストが追加されていない

CI では、エラー、警告、情報の 3 段階で結果を返す。

## 13. 既存ツールとの差別化

Kiwi TCMS や TestLink は、テストケースや実施結果の管理に強い。

一方、SpecMatrix は以下を中心価値とする。

> テスト実施管理ではなく、テスト妥当性管理を中心にする。

差別化ポイントは以下である。

- 仕様とテストのトレーサビリティを中心に設計する
- 組み込み固有の HW 条件、状態遷移、電源、通信、センサー異常を扱う
- AI とルールベース検査を組み合わせる
- 指摘には必ず根拠を付与する
- 過去不具合を再発防止テストに接続する
- CI でテスト設計の劣化を検出する

## 14. 段階的ロードマップ

### Phase 1: ファイルベース MVP

- Markdown 仕様書の取り込み
- YAML による要求、HW 構成、テストケース定義
- 要求とテストケースの対応チェック
- 基本ルール検査
- Markdown / JSON レポート出力

### Phase 2: AI レビュー

- AI による要求抽出
- AI による未試験リスク指摘
- テストケース案生成
- 指摘の承認、却下、保留

### Phase 3: Web UI

- ダッシュボード
- 要求一覧
- テストケース一覧
- カバレッジマトリクス
- AI レビュー画面
- エビデンス参照

### Phase 4: 実施管理・CI 連携

- テスト実施結果の記録
- エビデンス管理
- CI からの検査
- レポート生成

### Phase 5: 高度なモデル解析

- 状態遷移網羅性
- 組み合わせテスト観点生成
- 境界値自動抽出
- ハードウェア差分解析
- 過去不具合クラスタリング

## 15. 成功基準

MVP の成功基準は以下とする。

- 仕様書から抽出した要求を ID 付きで管理できる
- YAML で定義したテストケースと要求を対応付けできる
- 未対応要求を検出できる
- HW 条件不足を検出できる
- 過去不具合に対する再発防止テスト不足を検出できる
- 指摘に根拠と推奨対応を表示できる
- CI で検査結果を返せる

## 16. 設計方針

SpecMatrix は、AI を「判断の代替」ではなく「レビュー支援」として扱う。

品質保証で重要なのは、指摘の正しさだけではなく、なぜその指摘が出たのかを人間が確認できることである。

したがって、本システムは以下の原則を持つ。

- AI の出力は必ず根拠付きにする
- ルールベース検査で再現性を確保する
- 仕様、構成、テスト、実施結果をトレーサブルに接続する
- ユーザーが AI 指摘を承認、却下、修正できるようにする
- 組み込み開発の現場で説明できるレポートを生成する

## 17. まとめ

SpecMatrix は、テストケースを保管するためのシステムではなく、テスト設計が仕様とリスクに対して妥当かを検証するためのシステムである。

組み込み開発における仕様、ハードウェア構成、状態遷移、異常系、過去不具合を統合し、AI とルールベース検査によってテスト漏れを説明可能な形で提示する。

この方向性により、従来のテスト管理ツールでは扱いにくかった「試験設計の妥当性」を管理対象にできる。
