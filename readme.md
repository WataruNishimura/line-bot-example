# LINE BOT EXAMPLE

LINE Messaging API を利用した開発基盤

Status: working

## Requirements

### Python Packages

必要なパッケージはその都度 `requirements.txt` に記載

### Requirement files

- アサーション署名用の鍵ペアの生成が必要（[genjwtkey](https://github.com/WataruNishimura/genjwtkey) で生成可能）
- 以下の変数が含まれたheader.jsonを作成(参考：[JWTを生成する【LINE Developersドキュメント】](https://developers.line.biz/ja/docs/messaging-api/generate-json-web-token/#:~:text=%E5%BF%85%E9%A0%88%E3%83%95%E3%82%A3%E3%83%BC%E3%83%AB%E3%83%89%E3%81%A7%E3%81%99%E3%80%82-,%E3%83%98%E3%83%83%E3%83%80%E3%83%BC,-%E3%83%97%E3%83%AD%E3%83%91%E3%83%86%E3%82%A3))
  - alg ( RS256 ) 
  - typ ( JWT )
  - kid ( 登録した公開鍵のkid )
- .envファイルまたは環境変数にて、以下の定数の設定
  - `CLINET_ID` チャネルID
  - `CLIENT_SECRET` チャネルシークレット
