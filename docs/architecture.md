# SpecMatrix アーキテクチャ方針

## 1. 採用方針

SpecMatrix は、初期アーキテクチャとして **Web Monolith Architecture** を採用する。

理由は、SpecMatrix の主価値を単なるファイル検査や CLI レポートではなく、継続的な **品質監視ツール** として提供するためである。

SpecMatrix が扱う中心データは、要求、テストケース、実施結果、エビデンス、AI 指摘、承認履歴、監査ログである。これらは一度の検査で完結するものではなく、プロジェクト期間中に継続的に変化し、複数人で確認、承認、追跡される。

そのため、最初から Web UI、永続 DB、権限管理、履歴管理を中核に置く。

## 2. アーキテクチャ概要

```text
Browser
  ↓
Web Application
  ├─ Dashboard
  ├─ Requirement Management
  ├─ Test Case Management
  ├─ Coverage Matrix
  ├─ AI Review Console
  ├─ Execution Management
  └─ Evidence Management
  ↓
Application Backend
  ├─ Requirement Service
  ├─ Traceability Service
  ├─ Coverage Service
  ├─ Rule Engine
  ├─ AI Review Service
  ├─ Import Service
  ├─ Report Service
  └─ Audit Log Service
  ↓
Database / Object Storage
  ├─ PostgreSQL
  └─ Evidence File Storage
```

## 3. なぜ Web Monolith か

### 3.1 品質監視が主軸であるため

SpecMatrix の価値は、テストケースを静的に検査することだけではない。

重要なのは、プロジェクト全体の品質状態を継続的に監視することである。

- 未対応要求が増えていないか
- 高リスク要求のテストが欠落していないか
- AI 指摘が放置されていないか
- 過去不具合の再発防止テストが維持されているか
- テスト実施結果が悪化していないか
- 仕様変更に対してテスト設計が追従しているか

これらはダッシュボード、通知、履歴、承認フローと相性が良い。

### 3.2 監査性と説明責任が必要なため

品質保証では、単に「AI が不足を指摘した」だけでは不十分である。

以下を保存し、後から説明できる必要がある。

- いつ仕様が取り込まれたか
- どの要求が追加、変更、削除されたか
- 誰が AI 指摘を承認、却下、保留したか
- どの根拠に基づいてテストケースを追加したか
- どのファームウェア、ボード、環境でテストを実施したか
- どのエビデンスが合格判定を支えているか

この性質上、永続 DB と監査ログを持つ Web アプリケーションが適している。

### 3.3 複数人のレビューに向いているため

SpecMatrix では、AI の指摘を人間がレビューし、品質判断として確定する。

想定される操作は以下である。

- テスト設計者がテストケースを追加する
- QA がカバレッジ不足を確認する
- システム設計者が要求抽出結果を修正する
- リーダーが高リスク指摘を承認、却下する
- 監査担当者が履歴とエビデンスを確認する

この協調作業には、Web UI と権限管理が必要である。

## 4. 論理構成

```text
specmatrix
  ├─ presentation
  │   ├─ web_ui
  │   └─ api
  ├─ application
  │   ├─ requirement_service
  │   ├─ test_case_service
  │   ├─ traceability_service
  │   ├─ coverage_service
  │   ├─ review_service
  │   ├─ execution_service
  │   └─ report_service
  ├─ domain
  │   ├─ requirement
  │   ├─ hardware
  │   ├─ model_diagram
  │   ├─ test_case
  │   ├─ finding
  │   ├─ rule
  │   └─ evidence
  ├─ infrastructure
  │   ├─ database
  │   ├─ file_storage
  │   ├─ ai_provider
  │   ├─ document_parser
  │   ├─ mermaid_parser
  │   ├─ mermaid_renderer
  │   └─ notification
  └─ jobs
      ├─ import_job
      ├─ ai_review_job
      ├─ coverage_job
      └─ report_job
```

## 5. 推奨技術スタック

### 5.1 第一候補

```text
Backend: Python / Django
API: Django REST Framework
Async jobs: Celery
Database: PostgreSQL
Cache / Queue: Redis
Frontend: Django templates + HTMX, or React when needed
Object storage: Local filesystem first, S3 compatible later
AI adapter: Provider abstraction layer
Deployment: Docker Compose
```

Django を第一候補とする理由は以下である。

- 管理画面、認証、権限、ORM、マイグレーションが標準で強い
- 監査性のある業務アプリを短期間で作りやすい
- Web Monolith と相性が良い
- Python により文書解析、AI 連携、YAML 処理を実装しやすい
- 初期から PostgreSQL を前提にできる

### 5.2 代替候補

#### Ruby on Rails

Web Monolith として非常に強い。CRUD、管理画面、承認フローを高速に構築できる。

一方で、AI 連携、文書解析、組み込み向け解析ロジックは Python エコシステムの方が扱いやすい。

#### FastAPI + React

API とフロントエンドを分離した構成にしやすい。

ただし、初期から SPA と API を分けると、認証、画面、権限、フォーム、管理機能の実装量が増える。Web Monolith の利点が薄くなるため、初期候補としては Django より優先度を下げる。

#### TypeScript / Next.js

UI 体験を重視する場合は有力。

ただし、文書解析、AI レビュー、ルール検査、バッチ処理が中心になるため、初期の中核実装では Python の方が適している。

## 6. 主要コンポーネント

### 6.1 Web UI

品質監視の中心画面を提供する。

- ダッシュボード
- 要求一覧
- テストケース一覧
- カバレッジマトリクス
- AI 指摘一覧
- 実施結果一覧
- エビデンス閲覧
- 監査ログ

### 6.2 Application Backend

ユースケース単位の処理を担当する。

- 仕様書の取り込み
- リリースバージョン登録
- エンハンス、不具合対策の変更項目登録
- 要求抽出結果の確定
- テストケース登録
- リリース、変更項目、要求、テストケースの紐付け
- カバレッジ計算
- リリース品質ゲート判定
- AI レビュー実行
- 指摘の承認、却下、保留
- テスト実施結果登録
- 不具合状況管理
- レポート生成

### 6.3 Domain Model

品質判断の中核となるモデルを保持する。

- Project
- ReleaseVersion
- ChangeItem
- SpecificationDocument
- Requirement
- HardwareConfiguration
- ModelDiagram
- TestCase
- TraceLink
- TestCampaign
- TestExecution
- Evidence
- Defect
- Rule
- Finding
- ReleaseGate
- ReviewDecision
- AuditLog

### 6.4 Rule Engine

再現性のある検査を担当する。

例:

- すべての要求にテストケースがあるか
- すべてのリリース対象変更項目にテストケースがあるか
- 高リスク要求に異常系テストがあるか
- 過去不具合に再発防止テストがあるか
- リリース候補に未解決の重大不具合が残っていないか
- HW 構成に定義されたボード差分がテスト条件に含まれているか
- Mermaid モデル図に定義された状態、イベント、通信参加者がテスト条件で扱われているか

### 6.5 AI Review Service

AI によるレビュー、要求抽出、テストケース案生成を担当する。

AI Review Service は以下を必ず保存する。

- 使用モデル
- プロンプトバージョン
- 入力データの範囲
- 入力データのハッシュ
- 出力された指摘
- 指摘の根拠
- ユーザーの判断結果

### 6.6 Background Jobs

時間がかかる処理は非同期ジョブとして実行する。

- PDF / Word 解析
- Mermaid 記法の検証とレンダリング
- AI レビュー
- 大規模カバレッジ計算
- レポート生成
- エビデンス解析

## 7. データ保存方針

### 7.1 PostgreSQL

以下の構造化データを保存する。

- プロジェクト
- ユーザー
- リリースバージョン
- 変更項目
- 要求
- テストケース
- トレースリンク
- テストキャンペーン
- AI 指摘
- レビュー判断
- 実施結果
- 不具合
- リリースゲート
- 監査ログ

### 7.2 Object Storage

以下の非構造化データを保存する。

- 元仕様書
- テストログ
- 波形画像
- スクリーンショット
- CI 成果物
- 生成レポート

初期実装ではローカルファイルシステムを使用し、将来的に S3 互換ストレージへ拡張する。

## 8. 外部連携

初期から以下の連携を想定する。

- Git リポジトリからの仕様書取り込み
- CI からのテスト実施結果登録
- JUnit XML のインポート
- Markdown / PDF レポート出力
- OpenAI API またはオンプレ LLM への AI レビュー委譲

## 9. セキュリティと権限

最低限、以下のロールを定義する。

| ロール | 権限 |
| --- | --- |
| Admin | プロジェクト設定、ユーザー管理、全操作 |
| QA Lead | 指摘の承認、却下、ルール設定、レポート発行 |
| Engineer | 要求、テストケース、実施結果の登録 |
| Reviewer | 指摘確認、コメント、承認補助 |
| Auditor | 閲覧、監査ログ確認 |

AI 連携では、外部送信するデータ範囲を明示し、プロジェクト単位で制御できるようにする。

## 10. MVP スコープ

Web Monolith 方針における MVP は以下とする。

1. ユーザー認証
2. プロジェクト作成
3. リリースバージョン管理
4. エンハンス、不具合対策の変更項目管理
5. 仕様書アップロード
6. 要求の登録、編集、一覧
7. HW 構成の登録
8. テストケースの登録、編集、一覧
9. リリース、変更項目、要求、テストケースの紐付け
10. カバレッジマトリクス表示
11. 基本ルール検査
12. AI 指摘の登録、一覧、承認、却下
13. テストキャンペーンと実施結果の登録
14. 不具合状況管理
15. エビデンスファイル添付
16. リリース品質ダッシュボード
17. リリース判定画面

CLI は主軸ではなく、CI や外部連携用の補助インターフェースとして後から追加する。

## 11. 初期実装順序

1. Django プロジェクト作成
2. Project / User / ReleaseVersion / ChangeItem のモデル作成
3. 管理画面と基本 CRUD
4. Requirement / TestCase / TraceLink のモデル作成
5. カバレッジ計算サービス
6. リリース品質ダッシュボード
7. TestCampaign / TestExecution / Evidence / Defect のモデル作成
8. ReleaseGate / Finding / ReviewDecision / AuditLog のモデル作成
9. ルールエンジン
10. AI Review Service の抽象化
11. 仕様書アップロードと要求抽出

## 12. 将来拡張

- GitHub / GitLab 連携
- CI からの結果取り込み API
- JUnit XML / Robot Framework / pytest 結果のインポート
- 状態遷移カバレッジ解析
- Mermaid モデル図からの状態、イベント、シーケンス解析
- ハードウェア差分カバレッジ
- 過去不具合からの再発防止テスト監視
- 通知機能
- SSO
- オンプレ LLM
- マルチテナント対応

## 13. 方針まとめ

SpecMatrix は、CLI 検査ツールではなく、品質状態を継続的に監視する Web アプリケーションとして設計する。

そのため、初期から以下を中核に置く。

- Web UI
- PostgreSQL
- 監査ログ
- 承認フロー
- エビデンス管理
- ダッシュボード
- AI 指摘の人間レビュー

この方針により、SpecMatrix は「テストケースの入れ物」ではなく、「テスト設計の妥当性と品質リスクを監視するシステム」として成立する。
