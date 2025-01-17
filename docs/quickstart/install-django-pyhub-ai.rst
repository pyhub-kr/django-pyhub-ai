django-pyhub-ai 라이브러리 설치하기
===========================================


튜토리얼 영상
-------------------

6분 20초부터 시작합니다.

.. raw:: html

   <div class="video-container">
       <iframe
           src="https://www.youtube.com/embed/10Fp78n3jSw?start=380"
           frameborder="0"
           allowfullscreen>
       </iframe>
   </div>


라이브러리 설치
----------------------

``python manage.py runserver`` 터미널은 그대로 두시고, 새로운 터미널을 열어주세요. ``runserver`` 터미널과 명령 터미널은 분리해서 사용하시면 편리합니다.

#. 새 터미널 열기 : 명령프롬프트, 파워쉘, 터미널 등.
#. ``c:/work/myproj`` 폴더로 이동
#. 가상환경 활성화
#. 아래 명령으로 라이브러리 설치

.. code-block:: shell

   python -m pip install --upgrade django-pyhub-ai

이 라이브러리 하나만 설치하셔도 LLM 구동에 필요한 의존성이 걸린 라이브러리들이 자동으로 설치됩니다. 설치되는 라이브러리가 많으므로 설치에 시간이 조금 걸릴 수 있습니다.

+ ``langchain``, ``langchain-community``, ``langchain-openai`` 등
+ ``django-cotton`` 컴포넌트 라이브러리 등


장고 앱 활성화
----------------------

``mysite/settings.py`` 파일을 여신 후에 ``INSTALLED_APPS`` 항목에 ``pyhub_ai`` 앱과 ``django_cotton`` 앱을 추가해주세요. 순서는 상관없습니다.

.. code-block:: python
   :caption: mysite/settings.py

   INSTALLED_APPS = [
       # ...
       'pyhub_ai',
       'django_cotton',
   ]

``pyhub_ai`` 앱을 통해 기본 제공해드리는 템플릿에서 ``django_cotton``\을 활용한 컴포넌트가 있으므로 ``django_cotton`` 앱도 꼭 함께 활성화해주셔야 합니다.


데이터베이스 테이블 생성
-----------------------------------

``pyhub_ai`` 앱에서는 대화내역 저장을 위해 다음 2개 모델을 지원합니다.

+ ``Conversation`` : 대화방
+ ``ConversationMessage`` : 대화방 내 메시지

이 모델들을 데이터베이스에 생성하기 위해, 아래 명령을 실행해주세요.

.. code-block:: shell

   python manage.py migrate pyhub_ai

그럼 아래의 출력과 함께 ``db.sqlite3`` 데이터베이스 파일에 두 테이블이 추가로 생성됩니다.

.. code-block:: text

   Operations to perform:
     Apply all migrations: pyhub_ai
   Running migrations:
     Applying pyhub_ai.0001_initial... OK
