튜토리얼 실습 준비
===========================

API Key 구하기
--------------------

OpenAI API Key가 없으신 분은 :doc:`../quickstart/first-chat-bot` 튜토리얼의 "OpenAI API Key 얻기" 섹션을 참고해주세요.

OPEN_API_KEY 환경변수 설정
---------------------------------

프레임워크/운영체제에 따라서 환경변수를 설정하는 방법은 제각각입니다.
현 개발환경에서는 프로그램 실행 시 ``.env`` 파일 내역을 환경변수로서 로딩토록 하겠습니다.

프로젝트 루트 경로에 ``.env`` 파일을 생성하시고 아래와 같이 ``OPENAI_API_KEY`` 환경변수를 설정해주세요.

.. code-block:: text
   :linenos:
   :caption: .env 파일 생성

   OPENAI_API_KEY=sk-...

환경변수의 값으로는 여러분의 API Key를 적용해주세요. 절대 등호(=) 앞뒤로 띄워쓰기를 쓰시면 안 됩니다.
띄워쓰기를 쓰시면 ``.env`` 문법 오류로서 해당 환경변수는 무시되어 환경변수로서 로딩되지 않습니다.


.env 로딩 방법
----------------------

파이썬에서는 ``python-dotenv`` 라이브러리를 통해 ``.env`` 파일을 로딩하는 데요.
본 튜토리얼에서는 보다 장고 친화적인 ``django-environ`` 라이브러리를 통해 ``.env`` 파일을 환경변수로 로딩토록 하겠습니다.

.. code-block:: shell
   :linenos:

   pip install -U django-environ

아래와 같이 쓰시면, 이 파이썬 코드가 있는 폴더 경로에서 ``.env`` 파일을 찾아 환경변수로서 로딩합니다.

.. code-block:: python
   :linenos:

   from environ import Env

   env = Env()
   # .env 경로를 지정해서 로딩할 수도 있습니다.
   env.read_env(overwrite=True)

``.env`` 파일 까지만 생성해주시구요. ``.env`` 로딩 부분은 이후 내용에서 다시 적용하겠습니다.

.gitignore 파일 수정
------------------------

``.env`` 파일에는 중요한 계정정보가 들어있는 경우가 많기 때문에, 이 파일은 절대 소스코드 관리 대상에서 제외해야만 합니다.
``git add`` 명령을 실행하시기 전에 반드시 ``.gitignore`` 파일에 ``.env*`` 파일 패턴을 추가해주세요.

.. code-block:: text
   :linenos:

   .env*

이미 ``git add`` 하신 상황이라면, ``git rm --cached .env`` 명령으로 파일은 삭제하지 않으면서, 소스코드 관리 대상에서 제외할 수 있습니다.
그리고 커밋까지 해주시면 소스코드 관리 대상에서 제외됩니다.


Jupyter Lab을 사용하실려면
--------------------------------------

:doc:`./typical/index`\를 실습하실 때에는 Jupyter Notebook/Lab을 사용하셔도 됩니다.
``uv``\에서는 아래 명령으로 ``jupyter`` 패키지를 설치하고 원하는 명령으로 실행할 수 있습니다.

.. code-block:: bash

   uv pip install jupyter

   # uv run jupyter notebook
   uv run jupyter lab

단 :doc:`./django/index`\를 실습하실 때에는 Jupyter를 사용하실 수 없습니다.
소스코드 편집기가 필요하구요. Visual Studio Code 혹은 PyCharm Professional을 추천드립니다.
