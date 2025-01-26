====================================
[supabase] Postgre 서비스 활용하기
====================================

`Supabase <https://supabase.com/>`_\는 오픈소스 기반의 Firebase 대체 서비스입니다.
Postgre 데이터베이스를 기반으로 하며, 인증, 실시간 구독, 자동 API 생성 등 다양한 기능을 제공합니다.

Supabase는 기본적으로 pgvector 확장을 지원하므로, 별도의 설정 없이 벡터 검색 기능을 바로 사용할 수 있습니다.
무료 티어에서도 500MB의 데이터베이스 용량과 함께 가볍게 시작하실 수 있습니다.


프로젝트 생성하기
=====================

Supabase 홈페이지에서 회원가입을 하시고, 로그인을 해주세요.

.. image:: ./assets/supabase-01-root.png

계정 확인 과정을 거친 후에, 새로운 조직을 생성하실 수 있습니다.
원하시는 이름을 지정하시고 "Create organization" 버튼을 클릭해주세요.

.. image:: ./assets/supabase-02-new-org.png

프로젝트 생성 페이지에서 원하시는 이름을 지정하시고, 데이터베이스 암호를 입력해주세요.
"Generator a password" 버튼을 클릭해서 자동 생성하면 생성된 암호를 알 수 없구요.
데이터베이스 직접 연결에서 암호를 알 필요가 있으므로 복잡한 암호로 **직접** 입력해주세요.
저장된 암호는 supabase 서비스에서 알려주지 않습니다.
잃어버리셨다면 데이터베이스 설정 페이지에서 재설정하실 수 있습니다.

Region은 가까운 지역을 선택하시고, "Create project" 버튼을 클릭해주세요.

.. image:: ./assets/supabase-03-new-project.png

프로젝트 생성이 완료되고 대시보드 페이지로 자동 이동합니다.
데이터베이스 생성에 몇 분 정도 소요되므로 잠시 기다려주세요.

.. image:: ./assets/supabase-04-dashboard.png


Connection String 얻기
==================================

`supabase 공식문서 <https://supabase.com/docs/guides/database/connecting-to-postgres>`_\에 따르면
supabase에서는 2가지 연결 방식을 지원합니다.

#. 프론트엔드 라이브러리에서는 `data api <https://supabase.com/docs/guides/database/connecting-to-postgres#data-apis-and-client-libraries>`_ 인터페이스를 통해
   데이터베이스에 접근할 수 있습니다.
#. 장고와 같은 백엔드나 데이터베이스 애플리케이션에서는
   `Postgres 데이터베이스에 직접 연결 <https://supabase.com/docs/guides/database/connecting-to-postgres#direct-connection>`_\할 수 있습니다.

데이터베이스 연결에는 유저명, 암호, 호스트명, 포트, 데이터베이스명이 필요한데요. 아래와 같이 ``Connection String`` 포맷으로 제공됩니다.

.. code-block:: text

    postgresql://postgres:[YOUR-PASSWORD]@db.apbkobhfnmcqqzqeeqss.supabase.co:5432/postgres

대시보드 상단의 "Connect" 버튼을 클릭하면 아래의 "Connect to your project" 창이 뜨며, 다음 3가지 연결 모드를 지원한다고 합니다.
이 중에 ``Direct connection``\을 사용해보겠습니다.

* ``Direct connection`` : 가상 머신이나 장기 실행 컨테이너와 같이 지속적이고 장기적인 연결이 필요한 애플리케이션에 이상적입니다.
* ``Transaction pooler`` : Postgres와의 각 상호작용이 짧고 독립적인 서버리스 함수와 같은 무상태 애플리케이션에 이상적입니다.
* ``Session pooler`` : IPv4 네트워크를 통해 연결할 때 Direct Connection의 대안으로만 권장됩니다.

.. image:: ./assets/supabase-05-connection-string.png

암호는 보안을 이유로 제공되지 않습니다. connection string을 메모장에 복사해둡니다.

.. code-block:: text

    postgresql://postgres:[YOUR-PASSWORD]@db.eulifeisshortjvs.supabase.co:5432/postgres


암호를 Connection string에 적용하기
=============================================

조금 전에 지정하셨던 암호 기억하시나요?
암호를 까먹으셨다면 아래 섹션을 참고해서 암호를 재설정해주세요.

암호를 위 connection string에 적용하셔야 하는 데요.
암호를 ``password!@#$`` 이라고 가정해보겠습니다. 암호에 아래와 같이 골뱅이 ``@`` 문자가 있습니다.
connection string에 암호를 적용하면 아래와 같습니다.

.. code-block:: text

    postgresql://postgres:password!@#$@db.eulifeisshortjvs.supabase.co:5432/postgres

이 connection string은 유저명, 암호, 호스트, 포트, 데이터베이스명으로 파싱되어야하는 데요.
이를 파싱하는 라이브러리에 따라, 암호에 포함된 ``@`` 문자로 인해 암호가 잘려 파싱이 엉뚱하게 될 수 있습니다.
장고에서 사용하는 ``django-environ`` 최신 버전에서는 오류없이 잘 처리됩니다.

.. code-block:: python
    :emphasize-lines: 1,9

    >>> password = 'password!@#$'
    >>> connection_string = f'postgresql://postgres:{password}@db.eulifeisshortjvs.supabase.co:5432/postgres'

    >>> from environ import Env  # django-environ 라이브러리 설치 필요
    >>> env = Env()
    >>> env.db_url_config(connection_string)
    {'NAME': 'postgres',
    'USER': 'postgres',
    'PASSWORD': 'password!@#$',
    'HOST': 'db.eulifeisshortjvs.supabase.co',
    'PORT': 5432,
    'ENGINE': 'django.db.backends.postgresql'}

암호에 특수 문자가 포함된 경우, ``django-environ`` 라이브러리에서는 오류없이 잘 처리하지만, 라이브러리에 따라 오류가 있을 수 있습니다.
안전하게 처리하기 위해서는 암호를 URL 인코딩해주셔야 합니다. 파이썬에서는 ``urllib.parse.quote_plus`` 함수를 사용해서 암호를 URL 인코딩할 수 있습니다.

.. code-block:: python
    :emphasize-lines: 1-2,5,12

    >>> from urllib.parse import quote_plus
    >>> password = quote_plus('password!@#$')  # 'password%21%40%23%24'
    >>> connection_string = f'postgresql://postgres:{password}@db.eulifeisshortjvs.supabase.co:5432/postgres'
    >>> connection_string
    'postgresql://postgres:password%21%40%23%24@db.eulifeisshortjvs.supabase.co:5432/postgres'

    >>> from environ import Env
    >>> env = Env()
    >>> env.db_url_config(connection_string)
    {'NAME': 'postgres',
    'USER': 'postgres',
    'PASSWORD': 'password!@#$',
    'HOST': 'db.eulifeisshortjvs.supabase.co',
    'PORT': 5432,
    'ENGINE': 'django.db.backends.postgresql'}

connection string 파싱이 오류없이 잘 동작함을 확인하실 수 있습니다.
위의 ``connection_string`` 변수값에서 앞뒤로 홑따옴표를 제거하면 아래와 같습니다.
이 값이 데이터베이스 연결에 필요한 값입니다.

.. code-block:: text

    postgresql://postgres:password%21%40%23%24@db.eulifeisshortjvs.supabase.co:5432/postgres

장고 프로젝트에서 ``django-environ`` 라이브러리를 사용하실 때에는 ``DATABASE_URL`` 환경변수로 주입해주세요.
그럼 settings 내에서 ``env.db()`` 함수를 통해 ``DATABASE_URL`` 환경변수를 파싱해서 데이터베이스 연결 설정을 완료할 수 있습니다.

.. code-block:: python

    DATABASES = {
        'default': env.db(),
    }


암호를 재설정할려면?
========================

Project Settings → Database → Database Settings → Database password 섹션에서
암호를 재설정하실 수 있습니다.

.. image:: ./assets/supabase-06-project-settings.png
