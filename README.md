# WebAppViewer

WebAppViewerは、PythonとPyQt6を用いて作成されたGUIアプリケーションで、Webアプリケーションを独立したデスクトップアプリとして表示・管理できるビューアです。各Webアプリケーションをモジュールとして追加し、デスクトップエントリ（.desktopファイル）を生成して簡単にアクセスすることができます。

## 特徴

- PyQt6とQtWebEngineによるWeb表示
- Webアプリごとにカスタムプロファイル・キャッシュ管理
- スクリーンショット機能（クリップボード保存・ファイル保存）
- Webアプリごとのデスクトップエントリ作成（Linuxのアプリケーションランチャー対応）
- Webアプリ用のアイコン自動取得
- 日本語UI対応

## インストール

1. 必要なPythonパッケージをインストールしてください（PyQt6, requests, BeautifulSoup4, Pillowなど）。

   ```bash
   pip install PyQt6 PyQt6-WebEngine requests beautifulsoup4 pillow
   ```

2. リポジトリをクローンします。

   ```bash
   git clone https://github.com/shimarin/webappviewer.git
   cd webappviewer
   ```

3. アプリケーションを起動します（デフォルトモード）。

   ```bash
   python3 webappviewer.py
   ```

## 使い方

### 新しいWebアプリモジュールを追加する場合

- `webappviewer_apps` ディレクトリにPythonモジュール（例：`mywebapp.py`）を作成してください。
- モジュールには `desktop` 辞書（アプリ名やアイコンURLなど）および `open(window, browser)` 関数を実装します。

### デスクトップエントリの作成

以下のコマンドでアプリ名に応じた `.desktop` ファイルとアイコンを自動生成します。

```bash
python3 webappviewer.py --install <app_name>
```

これにより `~/.local/share/applications/` 配下にエントリが作成されます。

### スクリーンショット機能

アプリケーションメニューからクリップボードまたはファイルとしてWeb画面のスクリーンショット保存が可能です。

## ライセンス

MIT License  
Copyright (c) 2025 Tomoatsu Shimada

詳細は [LICENSE](./LICENSE) をご覧ください。
