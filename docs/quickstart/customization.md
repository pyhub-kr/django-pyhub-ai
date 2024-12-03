# 커스터마이징

## 프롬프트 커스터마이징
```python
class CustomAgent(AgentChatConsumer):
    system_message_template = """
    당신은 {role}입니다.
    전문 분야: {expertise}
    """
    
    def get_llm_prompt_context_data(self):
        return {
            'role': '전문 컨설턴트',
            'expertise': 'Python, Django',
        }
``` 