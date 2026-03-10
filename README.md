# Billnote（領収書管理アプリ）

## 概要
- 領収書管理と顧客管理ができる Web アプリです。  
- 領収書（Excel）のアップロードと、顧客名や年月での検索ができます。

## 目的・背景
- 実家の畳店におけるアナログな領収書管理をデジタル化し、業務効率化を図るために開発しました。

## 使用技術
- Python / FastAPI  
- HTML / CSS / JavaScript  
- AWS（DynamoDB, S3, lambda）  
- Git

## アプリ画面
- 自宅のグローバルIPアドレスでしかアクセスが出来ないためスクリーンショットでの説明になります。
- テスト用の領収書ファイルを2026年6月にアップロードしてテストしています。

### フォルダーをドラッグ＆ドロップした画面
<img width="1905" height="910" alt="image" src="https://github.com/user-attachments/assets/9e203e4d-60ef-47be-8bd4-d05b81cd7703" />

### ファイルをアップロードした画面
<img width="1905" height="910" alt="image" src="https://github.com/user-attachments/assets/f02d170e-7799-4b9a-9729-ac6b764028b7" />

### 年月検索した画面
<img width="1905" height="910" alt="image" src="https://github.com/user-attachments/assets/505d63d8-dd47-4b11-be0c-0751c98c4797" />

## ディレクトリー構造

```text
billnote/
├── main.py              # アプリケーションのエントリポイント（FastAPI）
├── static/              # HTMLファイル
├── utils/               # Excelファイルの処理
├── routers/             # API エンドポイント
├── services/            # AWSとのやりとり
├── others/              # ライブラリ一覧や更新履歴
├── .gitignore
└── README.md            # プロジェクト説明資料
```

## 使用方法・機能

### 1. 対象年・対象月を選択する

### 2. ファイルまたはフォルダーをドラッグ＆ドロップしてアップロード
- Excel がアップロードされ、以下の情報を自動抽出  
  - 顧客名  
  - 住所  
  - 電話番号  
  - 金額  
- 電話番号で顧客を識別  
  - DynamoDB に同じ電話番号がない → 新規顧客ID  
  - 同じ電話番号がある → 既存顧客ID  
  - 電話番号が空 → 顧客ID に 0 を付与  
- Excel は S3 に保存  
- 対象年月 / 抽出情報 / 顧客ID / S3 パス を DynamoDB に保存

### 3. 検索
- 年月を選択、または顧客名を入力して検索  
- 顧客名は部分一致検索に対応

### 4. 検索結果の表示
- DynamoDB に保存されているデータを一覧表示  
- 顧客IDはリンクになっており、クリックするとその顧客IDで再検索  
- 操作欄の「保存」ボタンで領収書（Excel）をダウンロード可能

## 課題
- データ削除機能を追加するか検討中  
- Excel を PDF に変換し、アプリ上で閲覧できるようにしたい  
  - ただし、抽出処理との整合性が保てるか検証中  
- フロントエンドはすべて AI 生成のため、学習して作り直したい
