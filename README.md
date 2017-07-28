# Liveagent API


## environ
* LIVEAGENT_HOST = <LIVEAGENT_HOST>
* LIVEAGENT_ORGANIZATION_ID = <LIVEAGENT_ORGANIZATION_ID>
* LIVEAGENT_DEPLOYMENT_ID = <LIVEAGENT_DEPLOYMENT_ID>
* LIVEAGENT_BUTTON_ID = <LIVEAGENT_BUTTON_ID>
* DISABLE_COLLECTSTATIC = 1
* SSL = True
* SECRET_KEY = <RANDOM_STRING>


deploy後にマイグレーション
```
$ heroku run bash --app アプリ名
```

```
$ python manage.py migrate
```

## Initialize
> 初期接続
```
https://example.com/init
```

method: POST

content-type: application/json

post key:
* line_id
* display_name(lineで取得した名前)
* prechatEntities

#### prechatEntities (example)
```
'prechatEntities': [{
    'entityName': 'Contact',　# 変更　(SFの参照オブジェクト)
    'showOnCreate': false,
    'linkToEntityName': null,
    'linkToEntityField': null,
    'saveToTranscript': 'ContactId',　# 変更　(SFの参照オブジェクト　プライマリーキー)
    'entityFieldsMaps': [{
       'fieldName': 'LINE_ID__c',　# 変更　(SFの参照LINEのIDが入っているカスタム項目キー)
       'label': 'ContactLineId',
       'doFind': true,
       'isExactMatch': true,
       'doCreate': false,
    }]
}]
```
### Response:

content-type: application/json

```
{
    'type': res_type,
    'message': result
}
```

type: response data
* ok
* fail

message: response data
* 接続しました。
* ただいま接続できません。



## Messages
> メッセージを取得
```
https://example.com/messages
```

method: POST

content-type: application/json

post key:
* line_id

### Response:

content-type: application/json

```
{
    'type': res_type,
    'message': result
}
```

type: response data
* message
* end

message: response data
* Liveagent側のコメント。
* 接続が終了しました。

## Message Send
> Lineからメッセージを送信
```
https://example.com/send
```

method: POST

content-type: application/json

post key:
* line_id
* message

### Response:

content-type: application/json

```
{
    'type': res_type,
    'message': result
}
```

type: response data
* bad
* send

message: response data
* send
* bad request

## Close
> 接続を切る
```
https://example.com/close
```

method: POST

content-type: application/json

post key:
* line_id

### Response:

content-type: application/json

```
{
    'type': res_type,
    'message': result
}
```

type: response data
* end

message: response data
* deleted session
