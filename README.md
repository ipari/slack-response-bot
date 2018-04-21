# slack-response-bot
[Slack](https://slack.com) 채팅봇입니다.  
간단한 데이터로 다양한 문장 패턴에 대한 응답을 설정할 수 있습니다.

```
groups:
    iu: '아이유, 지은, 징쨩'
    birthday: '생일, 태어나다'
    when: '날짜, 날, 언제, 며칠'

conditions:
    - keywords: 'group:iu, group:birthday, group:when'
      answers: '아이유 생일은 1993년 5월 16일 입니다.'
```

![sample](_img/sample.png)


## 설치

[KoNLPy](http://konlpy.org/ko/v0.4.4/) 을 먼저 설치합니다.

이후에 아래 명령으로 의존하는 패키지를 설치합니다.

```
$ pip3 install -r requirements.txt
```


## 실행

환경변수에 Slack 봇 토큰을 설정하고 실행합니다.

※ Slack 봇 추가하는 방법은 [여기](https://api.slack.com/bot-users#setup)를 참고하세요.

```
$ export SLACK_BOT_TOKEN=xoxb-your-token
$ python3 bot.py
```


## 데이터

`keywords.yml` 에 입력합니다.

- conditions
- groups
- triggers


### `conditions`
가장 기본이 되는 데이터로, 키워드와 대답을 입력합니다.

```
conditions:
    - keywords: '아이유'
      answers: '아이유는 사랑입니다.'
```

- `keywords` 에 동사 키워드를 넣을 경우 동사 원형을 입력합니다. `얻다` 로 입력하면, `얻는`, `얻을까` 등 여러 패턴에 반응합니다.
- `keywords` 에 키워드를 여러 개 넣으면, 모든 키워드를 포함하는 문장에 반응합니다. `'아이유, 혈액형'` 과 같이 `,` 로 구분하여 넣을 수도 있습니다.
- `answers` 에 문장을 여러 개 넣으면, 문장 중 하나를 무작위로 골라 대답합니다.

```
conditions:
    - keywords:
        - 아이유
        - 혈액형
      answers:
        - 아이유는 A형입니다.
        - 아이유는 B형이 아닙니다.
```

### `groups`
같은 의미를 가지는 키워드를 묶는데 사용합니다.

- `groups` 아래에 그룹 ID와 키워드 목록을 입력합니다. 마찬가지로 `,` 로 여러 키워드를 한 번에 넣어도 됩니다.
- `conditions` 의 `keywords` 에 `group:{group_key}` 형식으로 입력합니다.

```
groups:
    iu: '아이유, 지은, 징쨩'
    birthday: '생일, 태어나다'

conditions:
    - keywords:
        - group:birthday
        - group:when
      answers: '아이유 생일은 1993년 5월 16일 입니다.'
```

### `triggers`
**(옵션)** 모든 `conditions` 에 공통으로 적용할 키워드를 입력할 때 사용합니다.

```
conditions:
    - keywords: 'group:iu, 생일'
      answers: ...
    - keywords: 'group:iu, 혈액형'
      answers: ...
```

```
triggers:
  - group:iu

conditions:
  - keywords: '생일'
    answers: ...
  - keywords: '혈액형'
    answers: ...
```

사용하지 않을 때는 아래와 같이 비워둡니다.

```
triggers:
```
