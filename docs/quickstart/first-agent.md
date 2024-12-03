# 첫 번째 에이전트 만들기

## 에이전트 정의
```python
from pyhub_ai.consumers import AgentChatConsumer

class MyFirstAgent(AgentChatConsumer):
    system_message = "당신은 친절한 AI 어시스턴트입니다."
``` 