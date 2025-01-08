# 튜토리얼 #02: 인증 구현하고, 데이터베이스에 채팅 기록 자동 저장하기

본 튜토리얼을 진행하기에 앞서, [](../quickstart/index)를 먼저 진행해주세요.

앞선 튜토리얼의 실습코드가 없으신 분은 [샘플 저장소를 다운](https://github.com/pyhub-kr/django-pyhub-ai-sample/archive/refs/heads/main.zip)받으신 후에 압축을 푸시고, `tutorial_01` 디렉토리 기반으로 진행해주세요. `tutorial_01` 프로젝트 초기 설정은 [tutorial_01/README.md](https://github.com/pyhub-kr/django-pyhub-ai-sample/tree/main/tutorial_01) 문서를 참고해주세요.

튜토리얼 #01 에서는 페이지를 새로고침하면 채팅이 처음부터 다시 시작하는 문제가 있었습니다. 이 문제는 채팅 기록이 저장되지 않아서 인데요.

`django-pyhub-ai` 라이브러리에서는 채팅 기록을 데이터베이스에 자동 저장하고, LLM 요청 시에 채팅 기록을 자동으로 전달하는 **기능이 있습니다**. `pyhub_ai` 앱의 `Conversation` 모델과 `ConversationMessage` 모델을 통해 저장/관리됩니다. 그런데 아직 채팅 기록 기능이 동작하지 않는 상황입니다.

채팅 기록 기능을 활성화될려면, 다음 2가지 조건이 충족되어야 합니다.

1. 유저 식별이 되어야 합니다.
2. 채팅방 별로 채팅 기록을 저장할 `Conversation` 을 자동 생성하고, 기본키 지정하기

본 튜토리얼 #02에서는 인증 기능을 먼저 구현하고, 이어서 채팅 기록 자동 저장 기능을 활성화하는 방법을 살펴보겠습니다.

---

준비되셨나요? Let's go!

```{toctree}
:maxdepth: 2

auth
conversation-messages
```
