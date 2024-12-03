# 기본 설정

## URL 설정
```python
from django.urls import path, include

urlpatterns = [
    ...
    path('ai/', include('pyhub_ai.urls')),
]
``` 