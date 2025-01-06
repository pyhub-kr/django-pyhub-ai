# 인증 구현하기

장고에서는 `django.contrib.auth` 기본 앱을 통해 회원가입/로그인/로그아웃/프로필/암호변경/암호재설정 기능을 바로 가져다쓸 수 있을 정도로 지원해주고 있습니다.

## `accounts` 앱 생성 및 등록

먼저 `manage.py` 파일이 있는 프로젝트 루트에서 아래의 명령으로 `accounts` 앱을 생성해주세요.

```{code-block} shell
python manage.py startapp accounts
```

```{code-block} python
:caption: accounts/urls.py 파일 생성

from django.urls import path
from . import views

urlpatterns = []
```

`accounts` 앱을 프로젝트에 등록합니다.

```{code-block} python
:caption: mysite/settings.py

INSTALLED_APPS = [
    # ...
    "accounts",  # Tip: 끝에 콤마(,)를 꼭 넣어주세요.
]
```

```{code-block} python
:caption: mysite/urls.py

urlpatterns = [
    # ...
    path("accounts/", include("accounts.urls")),
]
```

## 회원가입 구현하기

```{code-block} python
:caption: accounts/forms.py

from django.contrib.auth.forms import UserCreationForm

class SignupForm(UserCreationForm):
    pass
```

```{code-block} python
:caption: accounts/views.py

from django.views.generic import CreateView
from django.contrib.auth.forms import UserCreationForm


signup = CreateView.as_view(
    form_class=UserCreationForm,
    template_name="form.html",
    success_url="/accounts/login/",
    # login 페이지가 구현된 후에는 reverse_lazy 사용을 추천
    # URL 문자열 계산은 장고에게 맡기세요. ;-)
    # success_url=reverse_lazy("accounts:login"),
)
```

```{code-block} django
:caption: templates/form.html

<form action="" method="post" enctype="multipart/form-data">
    {% csrf_token %}
    <table>
        {{ form.as_table }}
    </table>
    <input type="submit" />
</form>
```

프로젝트 전반적으로 사용되는 템플릿은 장고 앱 내의 `templates` 폴더가 아닌, 장고 앱 밖에 생성하고 활용합니다. 해당 템플릿 경로는 `settings.TEMPLATES` 의 `DIRS` 리스트에 등록합니다.

```{code-block} python
:caption: mysite/settings.py

TEMPLATES = [
    {
        # ...
        'DIRS': [
            BASE_DIR / 'templates',  # 추가
        ],
        # ...
    },
]
```

```{code-block} python
:caption: accounts/urls.py

from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("signup/", views.signup, name="signup"),
]
```

[http://localhost:8000/accounts/signup/](http://localhost:8000/accounts/signup/) 페이지를 방문하시면 아래 화면을 확인하실 수 있습니다.

![회원가입 페이지 en](./assets/signup-form-page-en.png)

```{code-block} python
:caption: mysite/settings.py

# LANGUAGE_CODE = 'en-us'
LANGUAGE_CODE = 'ko-kr'  # 디폴트 언어코드를 한국어로 변경
```

![회원가입 페이지 ko](./assets/signup-form-page-ko.png)

![로그인 페이지 아직 미구현](./assets/login-page-not-found.png)

## 로그인 구현하기

```{code-block} python
:caption: accounts/views.py

from django.contrib.auth.views import LoginView

login = LoginView.as_view(
    redirect_authenticated_user=True,
    template_name="form.html",
)
```

```{code-block} python
:caption: accounts/urls.py

urlpatterns = [
    # ...
    path("login/", views.login, name="login"),
]
```

![로그인 페이지 ko](./assets/login-form-page-ko.png)

![로그인 페이지 유효성 검사 에러 ko](./assets/login-form-page-error-ko.png)

![로그인 성공 후에 프로필 페이지 주소로 이동](./assets/profile-page-not-found.png)

## 프로필 페이지 구현하기

```{code-block} python
:caption: accounts/views.py

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def profile(request):
    return render(request, "accounts/profile.html")
```

```{code-block} django
:caption: accounts/templates/accounts/profile.html

<!doctype html>
<html lang="ko">
<head>
    <meta charset="UTF-8" />
    <title>프로필</title>
</head>
<body>

    <h2>{{ user }}'s 프로필</h2>

    <table>
        <tbody>
        <tr>
            <th>email</th>
            <td>{{ user.email|default:"&dash;" }}</td>
        </tr>
        <tr>
            <th>last_login</th>
            <td>{{ user.last_login|date:"Y년 m월 d일" }}</td>
        </tr>
        <tr>
            <th>date_joined</th>
            <td>{{ user.date_joined|date:"Y년 m월 d일" }}</td>
        </tr>
        </tbody>
    </table>

</body>
</html>
```

```{code-block} python
:caption: accounts/urls.py

urlpatterns = [
    # ...
    path("profile/", views.profile, name="profile"),
]
```

![프로필 페이지 ko](./assets/profile-page.png)

## 로그아웃 구현하기

```{code-block} python
:caption: accounts/views.py

from django.contrib.auth.views import LoginView, LogoutView

logout = LogoutView.as_view(
    next_page="accounts:login",
)
```

```{code-block} python
:caption: accounts/urls.py

urlpatterns = [
    # ...
    path("logout/", views.logout, name="logout"),
]
```

```{code-block} django
:caption: templates/accounts/profile.html

    {# 장고 5 이전까지 가능 #}
    <a href="/accounts/logout/">로그아웃</a>
    <a href="{% url 'accounts:logout' %}">로그아웃</a>  {# URL Reverse 활용 #}

    {# 장고 5 부터 LogoutView는 POST 요청만 허용합니다. #}
    <form action="/accounts/logout/" method="post"
          style="display: inline-block;">
        {% csrf_token %}
        <input type="submit" value="로그아웃" />
    </form>
</body>
</html>
```

![장고 5 이후 버전에서는 LogoutView는 POST 요청만 허용합니다.](./assets/logout-get-405-method-not-allowed.png)

![로그아웃 후에 로그인 페이지로 이동했습니다.](./assets/login-form-page-ko.png)

## 상단 메뉴에 인증 관련 메뉴 배치하기

```{code-block} django
:caption: templates/base.html

<!doctype html>
<html lang="ko">
<head>
    <meta charset="UTF-8"/>
    <title>튜토리얼 #02</title>
</head>
<body>

<nav>
    <ul>
        {% if not user.is_authenticated %}
            <li><a href="{% url 'accounts:signup' %}">회원가입</a></li>
            <li><a href="{% url 'accounts:login' %}">로그인</a></li>
        {% else %}
            <li><a href="{% url 'accounts:profile' %}">프로필</a></li>
            <li>
                <form action="/accounts/logout/" method="post"
                      style="display: inline-block;">
                    {% csrf_token %}
                    <input type="submit" value="로그아웃"/>
                </form>
            </li>
        {% endif %}
    </ul>
</nav>

<main>
    {% block main %}
    {% endblock %}
</main>

<footer>
    &copy; 2025. 파이썬사랑방.
</footer>

</body>
</html>
```

```{code-block} django
:caption: accounts/templates/accounts/profile.html

{% extends "base.html" %}

{% block main %}
    <h2>{{ user }}'s 프로필</h2>

    <table>
        <tbody>
        <tr>
            <th>email</th>
            <td>{{ user.email|default:"&dash;" }}</td>
        </tr>
        <tr>
            <th>last_login</th>
            <td>{{ user.last_login|date:"Y년 m월 d일" }}</td>
        </tr>
        <tr>
            <th>date_joined</th>
            <td>{{ user.date_joined|date:"Y년 m월 d일" }}</td>
        </tr>
        </tbody>
    </table>
{% endblock %}
```

```{code-block} django
:caption: templates/form.html

{% extends "base.html" %}

{% block main %}
    <form action="" method="post" enctype="multipart/form-data">
        {% csrf_token %}
        <table>
            {{ form.as_table }}
        </table>
        <input type="submit"/>
    </form>
{% endblock %}
```

![](./assets/profile-page-logged.png)
