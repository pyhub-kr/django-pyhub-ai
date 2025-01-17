pyhub-git-commit-apply 유틸리티
===============================

소개
----

핸즈온 세션을 진행하면서, 작은 오타가 문제를 일으킨다거나 타이핑이 느리신 분들은 실습이 한 번 밀리면 더 이상 따라가실 수가 없으시죠.
이때 빠르게 커밋을 현재 프로젝트에 적용하실 수 있으시도록, 커밋 코드를 현재 경로에 덮어쓰기 하는 유틸리티를 만들었습니다. 😉


지원 서비스
--------------

* ✅ ``https://github.com/`` 커밋 URL

설치
----

* 라이브러리 설치

  - ``uv pip install -U pyhub-git-commit-apply``

* 사용법

  - ``uv run pyhub-git-commit-apply <github-commit-url>`` : 커밋에서 **변경된 파일들만** 현재 경로에 덮어쓰기

  - ``uv run pyhub-git-commit-apply --all <github-commit-url>`` : 커밋에서 **프로젝트 내 모든 파일들을** 현재 경로에 덮어쓰기


``pyhub-git-commit-apply`` 명령과 더불어 ``python -m pyhub_git_commit_apply`` 명령으로도 지원합니다.


.. tip::

   ``uv`` 를 사용하지 않으실 경우 해당 가상환경을 활성화하시고 ``pyhub-git-commit-apply`` 명령어를 바로 사용하시면 됩니다.


예시
-----

`이 커밋 <https://github.com/pyhub-kr/django-llm-chat-proj/commit/d338364896984aa0a0e535926fea77d60c88347d>`_\에서는
3개의 파일만 변경되었기에, 3개의 파일만 덮어쓰기 됩니다.

.. code-block:: text
   :emphasize-lines: 1

   $ uv run pyhub-git-commit-apply https://github.com/pyhub-kr/django-llm-chat-proj/commit/d338364896984aa0a0e535926fea77d60c88347d
   Overwritten: chat/templates/chat/index.html
   Overwritten: chat/views.py
   Overwritten: templates/base.html


.. warning::

   적용할 프로젝트 루트 경로에서 명령어를 실행하셔야만 합니다. 명령을 실행하는 현재 경로에 파일을 덮어쓰기 합니다.
   다른 경로에서 엉뚱한 파일들을 덮어쓰지 않도록 주의해주세요.
