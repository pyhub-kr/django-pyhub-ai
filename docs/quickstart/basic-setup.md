# 프로젝트 생성 및 ASGI 설정

이미 장고 프로젝트가 생성되어있으시고, ASGI 설정 및 웹소켓 설정이 되어있으시다면 다음 단계로 넘어가셔도 됩니다.

## 튜토리얼 영상

1분부터 시작합니다.

```{raw} html
<div class="video-container">
    <iframe
        src="https://www.youtube.com/embed/10Fp78n3jSw?start=60"
        frameborder="0"
        allowfullscreen>
    </iframe>
</div>
```

## 파이썬 버전 확인

| 장고 버전 | 지원하는 파이썬 버전 |
|---------------|-----------------|
| 4.2 | 3.8, 3.9, 3.10, 3.11, 3.12 (4.2.8 버전에서 추가) |
| 5.0 | 3.10, 3.11, 3.12 |
| 5.1 | 3.10, 3.11, 3.12, 3.13 (5.1.3 버전에서 추가) |

장고 4.2 버전이 파이썬 3.8 버전도 지원하지만, `langchain-community` 라이브러리에서 [파이썬 3.9 이상을 요구](https://github.com/langchain-ai/langchain/blob/master/pyproject.toml#L12)하므로, 파이썬 3.9 이상 3.12 이하 버전을 사용하셔야 합니다. 장고 5.1 이상을 쓰신다면 파이썬 3.13도 사용 가능합니다.

가급적 최신 버전의 파이썬을 사용하시길 권장드립니다. (2024년 12월 기준 3.12 버전)

명령프롬프트 혹은 파워쉘, 터미널 등. 편한 터미널 프로그램을 여시고 파이썬 버전을 확인해주세요.

```shell
python --version
```

`Python 3.12.6` 처럼 버전이 출력되지 않고 아무런 출력이 없거나, `Python was not found` 에러가 출력되거나, Microsoft Store 애플리케이션이 뜨신다면 파이썬이 설치되지 않으셨거나, 파이썬 설치에 문제가 있는 상황입니다.

파이썬 설치를 다시 확인해주시구요. 윈도우 사용자 분들은 `python` 명령 대신에 `py` 명령을 사용해보세요.

```shell
py --version
```

`py` 명령은 파이썬 윈도우 배포판에서만 지원되는 명령으로서, 다수의 파이썬 배포판을 선택해서 실행할 수 있는 명령입니다.
대표적으로 아래 명령을 지원하니 꼭 써보세요.

- `py --list` : 설치된 파이썬 배포판 목록 조회
- `py -3.12` : 파이썬 3.12 버전 실행
- `py -3.12 --version` : 파이썬 3.12 버전 명령어 확인

## 장고 프로젝트 폴더 생성

```shell
# 윈도우: 프로젝트를 생성하실 폴더로 이동하신 후에
mkdir c:/work/
cd c:/work/

# 맥/리눅스
mkdir ~/work
cd ~/work

# 프로젝트 폴더로 사용할 빈 폴더를 생성해주세요.
mkdir myproj

# 프로젝트 폴더로 이동합니다.
cd myproj
```

## 가상환경 생성 및 활성화

하나의 개발 컴퓨터에서 다수의 파이썬 프로젝트를 하게 되므로 가상환경은 필수입니다. 가상환경을 생성하고 활성화하는 방법은 다양하지만, 가장 일반적인 방법은 `venv` 팩키지를 활용해서 가상환경을 생성하겠습니다. 이 외에도 편리하신 방법으로 가상환경을 생성하고 활성화해주세요.

```shell
# 가상환경 생성
python -m venv venv

# 가상환경 활성화 : 윈도우
venv\Scripts\activate

# 가상환경 활성화 : 맥, 리눅스
source venv/bin/activate
```

## 장고 라이브러리 설치 및 프로젝트 생성

장고 라이브러리를 통해, 새 장고 프로젝트를 생성하겠습니다. 가상환경에 장고 라이브러리를 설치합니다.

```shell
# 장고 5.x 버전을 사용하셔도 됩니다.
python -m pip install 'django~=4.2.0'
```

윈도우에서는 `c:/work/myproj` 폴더에서, 맥/리눅스는 `~/work/myproj` 폴더에서 다음 명령어를 실행하여 장고 프로젝트를 생성합니다. 명령 끝에 마침표(.)를 꼭 붙여주세요. 마침표를 붙이지 않으면, mysite 폴더가 하나 더 만들어지며 프로젝트 구조가 달라집니다.

```shell
python -m django startproject mysite .
```

그럼 `c:/work/myproj/` 내의 폴더 구조가 아래와 같아야 합니다. 다르다면 윈도우 탐색기에서 `c:/work/myproj/` 폴더에서 `venv` 폴더 외에는 모두 삭제하신 후에 `python -m django startproject mysite .` 명령어를 다시 실행해주세요.

```
manage.py
mysite/
    __init__.py
    asgi.py
    settings.py
    urls.py
    wsgi.py
```

## 개발서버 구동 테스트

아래 명령으로 장고 개발서버를 구동하실 수 있습니다.

```shell
python manage.py runserver
```

아래와 같은 출력이 뜨실 것이구요. `Ctrl-C` 혹은 `Ctrl-BREAK`를 눌러 서버를 중지할 수 있습니다. 윈도우의 GUI 애플리케이션에서는 `Ctrl-C`는 일반적으로 복사(Copy) 단축키이지만, 터미널에서는 복사가 아니라 인터럽트(Interrupt) 단축키입니다.

```text
Watching for file changes with StatReloader
Performing system checks...

System check identified no issues (0 silenced).

You have 18 unapplied migration(s). Your project may not work properly until you apply the migrations for app(s): admin, auth, contenttypes, sessions.
Run 'python manage.py migrate' to apply them.
December 03, 2024 - 22:01:33
Django version 4.2.16, using settings 'mysite.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

## 기본 데이터베이스 생성

위 `runserver` 로그에 보시면, 아래의 메시지가 있습니다. 18개의 적용되지 않은 마이그레이션이 있으며, `python manage.py migrate` 명령어를 실행하면 아직 적용되지 않은 마이그레이션을 적용할 수 있다고 합니다.

```text
You have 18 unapplied migration(s). Your project may not work properly until you apply the migrations for app(s): admin, auth, contenttypes, sessions.
Run 'python manage.py migrate' to apply them.
```

본 문서는 장고 기본을 다루지 않으므로, 마이그레이션에 대한 설명은 생략합니다.

`python manage.py runserver` 명령을 수행한 창에서 `Ctrl-C` 키를 눌러 개발 서버를 중단해주시구요. 다음 명령어를 실행하여, 미적용 마이그레이션을 적용해주세요.

```shell
python manage.py migrate
```

그럼 아래와 같은 출력이 뜨실 것이구요.

```text
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, sessions
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  Applying admin.0001_initial... OK
  Applying admin.0002_logentry_remove_auto_add... OK
  Applying admin.0003_logentry_add_action_flag_choices... OK
  Applying contenttypes.0002_remove_content_type_name... OK
  Applying auth.0002_alter_permission_name_max_length... OK
  Applying auth.0003_alter_user_email_max_length... OK
  Applying auth.0004_alter_user_username_opts... OK
  Applying auth.0005_alter_user_last_login_null... OK
  Applying auth.0006_require_contenttypes_0002... OK
  Applying auth.0007_alter_validators_add_error_messages... OK
  Applying auth.0008_alter_user_username_max_length... OK
  Applying auth.0009_alter_user_last_name_max_length... OK
  Applying auth.0010_alter_group_name_max_length... OK
  Applying auth.0011_update_proxy_permissions... OK
  Applying auth.0012_alter_user_first_name_max_length... OK
  Applying sessions.0001_initial... OK
```

파이썬은 기본적으로 SQLite 데이터베이스를 내장하고 있으며, Django 프로젝트도 기본값으로 SQLite를 사용하도록 설정되어 있습니다. 프로젝트 루트 디렉토리에서 `db.sqlite3` 파일을 확인하실 수 있는데, 이 단일 파일이 현재 Django 프로젝트의 전체 데이터베이스입니다.

SQLite는 단일 파일로 동작하는 경량 데이터베이스이지만, 지난 20년간 CPU, 메모리, SSD 등 컴퓨팅 성능이 비약적으로 발전했기 때문에 개발 단계나 소규모 서비스에서는 SQLite만으로도 충분한 성능을 발휘할 수 있습니다.

필요한 경우 Django의 설정만 변경하면 PostgreSQL, MySQL, MariaDB, Oracle, SQL Server 등의 데이터베이스로 손쉽게 전환할 수 있습니다.

## Visual Studio Code로 프로젝트 열기

Visual Studio Code나 PyCharm 같은 통합개발환경(IDE)으로 `c:/work/myproj` 폴더를 열어주세요.

Visual Studio Code와 PyCharm에서의 장고 개발환경 설정에 대해서 궁금하신 분은 [파이썬/장고 웹서비스 개발 완벽 가이드 with 리액트 (장고 4.2 기준)](https://inf.run/Fcn6n) 인프런 강의에서 "미리보기"로 공개한 영상에서 무료로 확인하실 수 있으니 참고해주세요.

- [00-04 VSCode 장고 개발환경 설정](https://www.inflearn.com/course/%ED%8C%8C%EC%9D%B4%EC%8D%AC-%EC%9E%A5%EA%B3%A0-%EC%9B%B9%EC%84%9C%EB%B9%84%EC%8A%A4-with%EB%A6%AC%EC%95%A1%ED%8A%B8/unit/197630?inst=d81f8ac6)
- [00-06 파이참 장고 개발환경 설정](https://www.inflearn.com/course/%ED%8C%8C%EC%9D%B4%EC%8D%AC-%EC%9E%A5%EA%B3%A0-%EC%9B%B9%EC%84%9C%EB%B9%84%EC%8A%A4-with%EB%A6%AC%EC%95%A1%ED%8A%B8/unit/197632?inst=d81f8ac6)

## channels/daphne 라이브러리 설치

장고를 비롯한 웹 서비스는 WSGI 스펙을 기반으로 동작합니다. WSGI에서는 비동기 처리를 지원하지 않기 때문에, 비동기 처리를 지원하는 ASGI 스펙을 기반으로 동작하는 channels/daphne 라이브러리를 설치해주세요.

```shell
python -m pip install channels daphne
```

## ASGI 활성화

`mysite/settings.py` 파일을 여시면 70번째 줄 쯤에 아래 코드가 보이실 겁니다.

```{code-block} python
:caption: mysite/settings.py

WSGI_APPLICATION = 'mysite.wsgi.application'
```

이 코드를 주석 처리하고, 아래와 같이 `ASGI_APPLICATION` 설정을 추가해주세요.

```{code-block} python
:caption: mysite/settings.py

# WSGI_APPLICATION = 'mysite.wsgi.application'
ASGI_APPLICATION = 'mysite.asgi.application'
```

그리고, 33번째 줄 쯤에 `INSTALLED_APPS` 설정이 있습니다. `INSTALLED_APPS` 리스트 처음에 `daphne` 앱을 추가해주세요.
장고 기본의 `runserver` 명령은 WSGI 만을 지원하므로, `daphne` 앱을 가장 앞에 추가해주어야 `daphne` 앱의 `runserver` 명령이 먼저 동작할 수 있기 때문입니다.

```{code-block} python
:caption: mysite/settings.py

INSTALLED_APPS = [
    "daphne",
    # 생략 ...
]
```

이제 다시 `python manage.py runserver` 명령어를 실행해주세요. 그럼 아래와 같이 출력 메시지에서 `Starting ASGI/Daphne` 문구를 확인하실 수 있습니다.
WSGI가 아닌 ASGI로 개발서버가 구동되었습니다.

```text
Watching for file changes with StatReloader
Performing system checks...

System check identified no issues (0 silenced).
December 03, 2024 - 22:28:38
Django version 4.2.16, using settings 'mysite.settings'
Starting ASGI/Daphne version 4.1.2 development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```
