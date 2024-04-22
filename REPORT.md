## Challenge 1 - The Full Stack Challenge

#### 実装内容概要
- CSVインポート機能
  - Userテーブルおよびconsumptionテーブルに対してCSVファイルの内容を取込
- summaryページ
  - 全ユーザー月別総消費量合計推移のグラフ
  - エリア別消費比率のグラフ
  - 全ユーザーのリスト
- detailページ
  - 個別ユーザーの月別消費量合計のグラフ
  - 時間帯別平均使用量のグラフ

#### アプリ実行手順
  1. 必要モジュールのインストール…「pip install -r requirements.txt」
  2. Django関連テーブルの作成…「python manage.py migrate」
  3. アプリ関連テーブルの作成…「python manage.py makemigrations cousumption」⇒「python manage.py migrate consumption」
  4. CSVファイルの取り込み…「python manage.py import」
  5. アプリの起動…「python manage.py runserver」

#### テーブル設計
  - User
    - user_id…int・主キー・項目名「ID」
    - user_area…string・最長10文字・項目名「エリア」
    - user_tariff…string・最長10文字・項目名「関税」
    - created_at…datetime・自動セット・項目名「登録日」

  - Consumption
    - user_id…Userテーブル外部キー
    - cousumption_datetime…datetime・最長10文字・項目名「消費日時」
    - cousumption_value…int・項目名「消費」
    - created_at…datetime・自動セット・項目名「登録日」

#### 実装について
  - グラフの作成について
    - 「matplotlib.pyplot」を使用してグラフを作成。作成後に画像化しHTML上で表示させている。
    - summaryページにおける全ユーザー月別総消費量合計推移のグラフについて、表示速度に課題有。テーブルより必要情報を全件取得した後、集計する構成も検証したが、明確な改善は見られなかったため取得時に集計も実施する現状構成を採用。

  - summaryページのユーザーリストについて
    - 表示方法についてはページネーション機能による分割表示も検証したが、上記全ユーザー月別総消費量合計推移のグラフの表示速度の問題から不採用。様々な代替案が考えられるが今回は一覧のスクロール表示を採用。

  - その他
    - コーディング規約については基本的にPEP8に準拠
    - Djangoのテスト機能によるユニットテスト実施済み