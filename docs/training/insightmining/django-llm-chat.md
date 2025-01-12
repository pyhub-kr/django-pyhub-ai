# django-llm-chat

## 프로젝트 다운로드 및 초기 구동

[인증 구현까지 완료된 장고 프로젝트를 zip 파일로 다운로드](https://github.com/pyhub-kr/django-llm-chat-proj/archive/55b897f27b682f753ad3bc0c27d28b845b78c375.zip)

```{code-block} bash
:linenos:

# 압축을 해제하시고, 프로젝트 디렉토리로 이동합니다.
cd django-llm-chat-proj

# uv 설치
python -m pip install -U uv

# uv를 통한 가상환경 생성
# 디폴트로 .venv 경로에 가상환경이 생성됩니다.
uv venv

# uv를 통한 패키지 설치
uv pip install -r requirements.txt
```

```{code-block} bash
:linenos:

# 가상환경 활성화
venv\Scripts\activate      # 윈도우
source .venv/bin/activate  # 맥/리눅스

python manage.py migrate  # 데이터베이스에 테이블 생성
python manage.py createsuperuser  # 암호 입력에서는 입력 피드백이 없습니다.
python manage.py runserver 00.0.0:8000  # 장고 개발서버 구동
```
