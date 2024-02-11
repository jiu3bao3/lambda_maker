### 概要
AWSのLambdaをPythonで作成する

無償版の[LocalStack](https://github.com/localstack/localstack)では永続化できないので，毎回Lambda関数を作成してデプロイする必要があるため，自動化したもの。

※AWSサービスでの動作確認はしていません。

#### 設定
- LocalStackでLambda,APIGatewayを起動する（手順はLocalStackのドキュメントを参照）
- Lambdaで実行するソースプログラムを作成する（この例ではresourcesディレクトリにmock.pyという名前のPythonコードを作成している）
- config.ymlファイルに必要な設定を記述する。

|パラメータ名| 設定内容| 記述例 |
|-----------|----------|--------|
|aws.region | リージョン | "us-east-1" |
|aws.endpoint-url | LocalStackのエンドポイントURL | "http://localstack:4566" |
|aws.access_key_id | AWSのアクセスキーID |  |
|aws.secret_access_key | AWSのシークレットアクセスキー| |
|aws.lambda.runtime | Lambdaランタイムの種類 | "python3.12" |
|aws.lambda.role | Lambda実行ロール（注１） | "arn:aws:iam::000000000000:role/lambda-role" |
|aws.lambda.handler| Lambdaのハンドラ設定（ファイル名と実行する関数名を"."で連結した文字列） | "mock.hello" |
|aws.lambda.source_dir | Lambdaで実行する関数のソースコードを格納したディレクトリのパス | "resource" |
|aws.lambda.override | 同名のLambdaが存在した場合に上書きするか | True / False |
|aws.apigateway.rest_api_gateway_name | rest_api_gatewayの名前 | "mock" | 
|aws.apigateway.http_method | 対応するHTTPメソッド | ANY/POST/GET etc. |
|aws.apigateway.type | | AWS_PROXY" |
|aws.apigateway.integration_http_method | | "ANY" |
|aws.apigateway.stage_name | | |

注１）LocalStackではフォーマットしかチェックされない様子

<details>
  <summary>config.yml記述例</summary>

```
aws:
  region: "ap-northeast-1"
  endpoint_url: "http://localhost:4566"
  access_key_id: "dummy"
  secret_access_key: "dummy"
  lambda:
    runtime: "python3.11"
    role: "arn:aws:iam::000000000000:role/lambda-role"
    handler: "mock.hello"
    source_dir: "resource"
    override: True
  apigateway:
    rest_api_gateway_name: "mock"
    http_method: "ANY"
    type: "AWS_PROXY"
    integration_http_method: "ANY"
    stage_name: "TEST"
```
</details>

#### 実行
```
python create_lambda.py

START
http://localhost:4566/restapis/z973jgzjsa/test/_user_request_/hello
END
```

curlコマンドで作成したLambdaを実行する
```
curl http://localhost:4566/restapis/z973jgzjsa/test/_user_request_/hello

{"message": "Hello Lambda"}
```
<details>
<summary>LocalStackのログ</summary>

```
2024-02-11 13:00:20 2024-02-11T04:00:20.768 DEBUG --- [   asgi_gw_2] l.u.c.docker_sdk_client    : Copying file /tmp/lambda/awslambda-ap-northeast-1-tasks/hello-b18221a9-5daf-46b9-baee-b3f3ff070d26/code/. into 20-dev-aws-1-lambda-hello-067bc33ae4a4f2d825b565b74edbbec3:/var/task
2024-02-11 13:00:20 2024-02-11T04:00:20.811 DEBUG --- [   asgi_gw_2] l.u.c.docker_sdk_client    : Starting container 20-dev-aws-1-lambda-hello-067bc33ae4a4f2d825b565b74edbbec3
2024-02-11 13:00:21 2024-02-11T04:00:21.064 DEBUG --- [   asgi_gw_2] l.u.c.container_client     : Getting ipv4 address for container 20-dev-aws-1-lambda-hello-067bc33ae4a4f2d825b565b74edbbec3 in network 20_dev_default.
2024-02-11 13:00:21 2024-02-11T04:00:21.302 DEBUG --- [   asgi_gw_1] rolo.gateway.wsgi          : POST 172.18.0.3:4566/_localstack_lambda/067bc33ae4a4f2d825b565b74edbbec3/status/067bc33ae4a4f2d825b565b74edbbec3/ready
2024-02-11 13:00:21 2024-02-11T04:00:21.303 DEBUG --- [   asgi_gw_2] l.s.l.i.execution_environm : Start of execution environment 067bc33ae4a4f2d825b565b74edbbec3 for function arn:aws:lambda:ap-northeast-1:000000000000:function:hello:$LATEST took 1877.54ms
2024-02-11 13:00:21 2024-02-11T04:00:21.303  INFO --- [   asgi_gw_1] localstack.request.http    : POST /_localstack_lambda/067bc33ae4a4f2d825b565b74edbbec3/status/067bc33ae4a4f2d825b565b74edbbec3/ready => 202
2024-02-11 13:00:21 2024-02-11T04:00:21.304 DEBUG --- [   asgi_gw_2] l.s.l.i.docker_runtime_exe : Sending invoke-payload '{"invoke-id": "b06f6b31-b704-4a42-b415-f66126854b68", "invoked-function-arn": "arn:aws:lambda:ap-northeast-1:000000000000:function:hello", "payload": "{\"path\": \"/hello\", \"headers\": {\"Host\": \"localhost:4566\", \"User-Agent\": \"curl/8.4.0\", \"accept\": \"*/*\", \"X-Forwarded-For\": \"192.168.65.1, localhost:4566\", \"x-localstack-edge\": \"http://localhost:4566\"}, \"multiValueHeaders\": {\"Host\": [\"localhost:4566\"], \"User-Agent\": [\"curl/8.4.0\"], \"accept\": [\"*/*\"], \"X-Forwarded-For\": [\"192.168.65.1, localhost:4566\"], \"x-localstack-edge\": [\"http://localhost:4566\"]}, \"body\": \"\", \"isBase64Encoded\": false, \"httpMethod\": \"GET\", \"queryStringParameters\": null, \"multiValueQueryStringParameters\": null, \"pathParameters\": {\"proxy\": \"hello\"}, \"resource\": \"/{proxy+}\", \"requestContext\": {\"accountId\": \"000000000000\", \"apiId\": \"z973jgzjsa\", \"resourcePath\": \"/{proxy+}\", \"domainPrefix\": \"localhost\", \"domainName\": \"localhost\", \"resourceId\": \"9vodgma8nb\", \"requestId\": \"b5ec1d4d-37e4-478d-81fe-11f9a2b618b5\", \"identity\": {\"accountId\": \"000000000000\", \"sourceIp\": \"192.168.65.1\", \"userAgent\": \"curl/8.4.0\"}, \"httpMethod\": \"GET\", \"protocol\": \"HTTP/1.1\", \"requestTime\": \"11/Feb/2024:04:00:19 +0000\", \"requestTimeEpoch\": 1707624019419, \"authorizer\": {}, \"path\": \"/test/hello\", \"stage\": \"test\"}, \"stageVariables\": {}}", "trace-id": "Root=1-65c84655-036ff76de5f235d8af004b70;Parent=4a337c2305ea124e;Sampled=0"}' to executor '067bc33ae4a4f2d825b565b74edbbec3'
2024-02-11 13:00:21 2024-02-11T04:00:21.309 DEBUG --- [   asgi_gw_1] rolo.gateway.wsgi          : POST 172.18.0.3:4566/_localstack_lambda/067bc33ae4a4f2d825b565b74edbbec3/invocations/b06f6b31-b704-4a42-b415-f66126854b68/logs
2024-02-11 13:00:21 2024-02-11T04:00:21.310  INFO --- [   asgi_gw_1] localstack.request.http    : POST /_localstack_lambda/067bc33ae4a4f2d825b565b74edbbec3/invocations/b06f6b31-b704-4a42-b415-f66126854b68/logs => 202
2024-02-11 13:00:21 2024-02-11T04:00:21.313 DEBUG --- [   asgi_gw_1] rolo.gateway.wsgi          : POST 172.18.0.3:4566/_localstack_lambda/067bc33ae4a4f2d825b565b74edbbec3/invocations/b06f6b31-b704-4a42-b415-f66126854b68/response
2024-02-11 13:00:21 2024-02-11T04:00:21.314  INFO --- [   asgi_gw_1] localstack.request.http    : POST /_localstack_lambda/067bc33ae4a4f2d825b565b74edbbec3/invocations/b06f6b31-b704-4a42-b415-f66126854b68/response => 202
2024-02-11 13:00:21 2024-02-11T04:00:21.317 DEBUG --- [   asgi_gw_2] l.s.l.i.version_manager    : Got logs for invocation 'b06f6b31-b704-4a42-b415-f66126854b68'
2024-02-11 13:00:21 2024-02-11T04:00:21.318 DEBUG --- [   asgi_gw_2] l.s.l.i.version_manager    : [hello-b06f6b31-b704-4a42-b415-f66126854b68] START RequestId: b06f6b31-b704-4a42-b415-f66126854b68 Version: $LATEST
2024-02-11 13:00:21 2024-02-11T04:00:21.318 DEBUG --- [   asgi_gw_2] l.s.l.i.version_manager    : [hello-b06f6b31-b704-4a42-b415-f66126854b68] {'path': '/hello', 'headers': {'Host': 'localhost:4566', 'User-Agent': 'curl/8.4.0', 'accept': '*/*', 'X-Forwarded-For': '192.168.65.1, localhost:4566', 'x-localstack-edge': 'http://localhost:4566'}, 'multiValueHeaders': {'Host': ['localhost:4566'], 'User-Agent': ['curl/8.4.0'], 'accept': ['*/*'], 'X-Forwarded-For': ['192.168.65.1, localhost:4566'], 'x-localstack-edge': ['http://localhost:4566']}, 'body': '', 'isBase64Encoded': False, 'httpMethod': 'GET', 'queryStringParameters': None, 'multiValueQueryStringParameters': None, 'pathParameters': {'proxy': 'hello'}, 'resource': '/{proxy+}', 'requestContext': {'accountId': '000000000000', 'apiId': 'z973jgzjsa', 'resourcePath': '/{proxy+}', 'domainPrefix': 'localhost', 'domainName': 'localhost', 'resourceId': '9vodgma8nb', 'requestId': 'b5ec1d4d-37e4-478d-81fe-11f9a2b618b5', 'identity': {'accountId': '000000000000', 'sourceIp': '192.168.65.1', 'userAgent': 'curl/8.4.0'}, 'httpMethod': 'GET', 'protocol': 'HTTP/1.1', 'requestTime': '11/Feb/2024:04:00:19 +0000', 'requestTimeEpoch': 1707624019419, 'authorizer': {}, 'path': '/test/hello', 'stage': 'test'}, 'stageVariables': {}}
2024-02-11 13:00:21 2024-02-11T04:00:21.319 DEBUG --- [   asgi_gw_2] l.s.l.i.version_manager    : [hello-b06f6b31-b704-4a42-b415-f66126854b68] {'isBase64Encoded': False, 'statusCode': 200, 'headers': {'Content-Type': 'application/json'}, 'body': {'message': 'Hello Lambda'}}
2024-02-11 13:00:21 2024-02-11T04:00:21.320 DEBUG --- [   asgi_gw_2] l.s.l.i.version_manager    : [hello-b06f6b31-b704-4a42-b415-f66126854b68] END RequestId: b06f6b31-b704-4a42-b415-f66126854b68
2024-02-11 13:00:21 2024-02-11T04:00:21.320 DEBUG --- [   asgi_gw_2] l.s.l.i.version_manager    : [hello-b06f6b31-b704-4a42-b415-f66126854b68] REPORT RequestId: b06f6b31-b704-4a42-b415-f66126854b68   Duration: 1.24 ms       Billed Duration: 2 ms   Memory Size: 128 MB     Max Memory Used: 128 MB
2024-02-11 13:00:21 2024-02-11T04:00:21.320 DEBUG --- [   asgi_gw_2] l.s.lambda_.provider       : Lambda invocation duration: 1895.54ms
2024-02-11 13:00:21 2024-02-11T04:00:21.323  INFO --- [   asgi_gw_0] localstack.request.http    : GET /restapis/z973jgzjsa/test/_user_request_/hello => 200
```
</details>
