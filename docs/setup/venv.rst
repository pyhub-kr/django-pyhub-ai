가상환경 제대로 알고 사용하기
=======================================

가상환경이란?
-------------------

파이썬에서는 하나의 라이브러리는 하나의 버전 밖에 설치하지 못합니다.
동시에 여러 프로젝트를 개발할 경우, 서로 다른 버전의 라이브러리를 사용해야할 때가 있는 데요.
이때 각 프로젝트를 사용할 때마다 그 프로젝트에서 사용하는 라이브러리를 재설치해야하는 번거로움이 있습니다.

그래서 가상환경을 사용합니다. 가상환경은 라이브러리를 격리해서 설치할 수 있는 디렉토리를 뜻합니다.

프로젝트마다 라이브러리를 설치하는 디렉토리를 구별해서 사용하면,
서로 다른 버전의 라이브러리도 여럿 설치할 수 있게 됩니다.
물론 한 가상환경 내에서는 하나의 버전만 설치할 수 있습니다.

venv
-----

파이썬3 기본에서 제공해주는 가상환경 모듈입니다.
파이썬2에서는 기본제공 가상환경 모듈이 없어서 써드파티 ``virtualenv`` 라이브러리를 사용했었습니다.

아래 명령으로 가상환경을 생성합니다. 즉 라이브러리를 격리해서 설치하는 디렉토리를 생성한 것입니다.

.. code-block:: text

   # 지정 경로에 가상환경을 생성합니다.
   $ python -m venv 가상환경을_생성할_경로

가상환경은 프로젝트마다 하나씩 생성하시기를 권장드립니다. 각 프로젝트에서 사용하는 라이브러리가 비슷하더라도 개발하다보면 라이브러리 버전이 달라집니다.
프로젝트 생성 단계에서부터 가상환경을 달리 생성하여 관리하시면 라이브러리 관리가 편해집니다.
요즘 디스크 용량이 많이 커졌기 때문에 디스크 용량이 부족해지는 경우는 드뭅니다.
디스크 용량을 희생하고 마음의 평화를 얻으세요. 😉

가상환경은 대개 프로젝트 루트 경로에서 ``venv`` 혹은 ``.venv`` 이름으로 생성합니다.

.. code-block:: text

   # 프로젝트 루트로 먼저 이동하신 후에, 현재 디렉토리 .venv 디렉토리에 가상환경을 생성합니다.
   $ python -m venv .venv

.. admonition:: 주의
   :class: warning

   ``git commit`` 전에 반드시 ``.gitignore`` 파일에 가상환경 디렉토리 패턴을 추가해주세요.
   많은 초심자 분들이 가상환경 디렉토리를 커밋하는 실수를 하는데, 이런 실수를 미연에 방지하기 위함입니다.

   .. code-block:: text

      .venv
      venv

생성된 가상환경은 반드시 활성화(``activate``) 단계를 거쳐야 사용할 수 있습니다.
윈도우와 맥/리눅스는 생성되는 가상환경 파일도 다르고, 사용하는 쉘이 달라서 활성화 명령이 다릅니다.

.. code-block:: text

   # 윈도우 명령프롬프트/파워쉘 공통 ($ 부분은 명령이 아닙니다.)
   $ .venv\Scripts\activate

   # 맥/리눅스 쉘 공통
   $ source .venv/bin/activate

가상환경를 활성화하신 후에, 반드시 현재 ``python`` 명령이 가상환경 내의 ``python`` 명령을 가리키는 지 확인해주세요.
만약 ``python`` 경로가 가상환경 경로를 가리키지 않는다면, ``python`` 명령 혹은 ``pip`` 명령이 가상환경 내 라이브러리를 사용하지 않습니다.

.. code-block:: text

   # 윈도우 명령 프롬프트
   $ where python
   C:\work\project\.venv\Scripts\python.exe

   # 윈도우 파워쉘
   $ Get-Command python | Select-Object -ExpandProperty Source
   C:\work\project\.venv\Scripts\python.exe

   # 맥/리눅스
   $ which python
   /Users/username/work/project/.venv/bin/python

가상환경이 활성화되셨다면, 이제 ``python``, ``python -m pip`` 명령은 해당 가상환경에 라이브러리를 설치하고, 그 가상환경의 라이브러리를 활용하게 됩니다.

가상환경 사용이 끝나셨다면 ``deactivate`` 명령을 통해 가상환경을 비활성화. 즉 가상환경을 빠져나오실 수 있습니다.

VSCode와 PyCharm에서는 각 프로젝트마다 사용하는 가상환경을 지정하는 기능이 있습니다. 이를 지정하시면 터미널 실행 시에 자동으로 가상환경이 활성화되며,
소스코드 편집기에서도 가상환경 내의 라이브러리를 참조하게 됩니다.

.. admonition:: VSCode에서는 Python 확장이 필요합니다.
   :class: tip

   VSCode에서는 `Python 확장 <https://marketplace.visualstudio.com/items?itemName=ms-python.python>`_\을 설치하신 후에,
   명령 팔레트에서 ``Python: Select Interpreter`` 명령을 통해 현 프로젝트에서 사용할 가상환경 경로를 지정하실 수 있습니다.


uv
--

`uv <https://docs.astral.sh/uv/>`_\는 Rust로 개발된 매우 빠른 파이썬 패키지/프로젝트 관리자입니다.
``pip``\보다 10~100배 이상 빠르다고 알려져있습니다. 저도 요즘 즐겨 사용하고 있습니다.

``uv`` 명령은 다양한 기능들이 있지만, 그 중 ``venv`` 관련된 명령만 살펴보겠습니다.

먼저 전역으로 ``uv``\를 설치합니다.

.. code-block:: bash

   python -m pip install --upgrade uv

프로젝트 루트 경로로 이동한 후에, ``uv venv`` 명령을 통해 가상환경을 생성합니다.
디폴트로 ``.venv`` 디렉토리에 가상환경이 생성됩니다.
``.gitignore`` 파일에 ``.venv`` 패턴도 꼭 추가해주시구요.

.. code-block:: bash

   uv venv

따로 가상환경을 활성화할 필요없이 ``uv pip`` 명령으로 가상환경에 패키지를 설치하고,
``uv run`` 명령으로 가상환경을 사용하여 파이썬 파일을 실행할 수 있습니다.

.. code-block:: bash

   uv pip install 패키지명
   uv pip install -r requirements.txt

   uv run python 실행할_파일명.py

가상환경 활성화가 필요하시다면, ``.venv`` 경로를 참조해서 아래와 같이 활성화하실 수도 있습니다.

.. code-block:: bash

   # 윈도우
   .venv\Scripts\activate

   # 맥/리눅스
   source .venv/bin/activate


conda environment
-----------------

Anaconda Python에서는 ``conda`` 명령을 통해 가상환경을 생성하실 수 있습니다. 이를 ``Conda Environment``\라고 부릅니다.
파이썬 가상환경은 라이브러리만 격리해서 설치할 수 있는 디렉토리를 생성하는 것이었다면,
Conda Environment는 이에 더해 사용할 파이썬 버전까지 격리해서 생성할 수 있습니다.

파이썬 3.8 버전의 Anaconda Python을 설치했었더라도, 아래 명령으로 파이썬 3.13 버전의 Conda Environment를 생성할 수 있습니다.
Anaconda Python을 사용하신다면 절대 여러 버전의 파이썬을 설치하실 필요가 전혀 없습니다.

.. code-block:: text

   conda create -n 가상환경_이름 python=3.13

``python -m venv`` 명령은 원하는 경로에 가상환경을 생성하기 때문에 해당 디렉토리로 이동해야만 가상환경을 활성화할 수 있습니다.
그에 반면 ``conda create -n`` 명령은 Anaconda Python의 특정 디렉토리에 모여 생성되기 때문에,
어느 경로에서든 아래 ``conda activate 가상환경_이름`` 명령으로 활성화할 수 있습니다.

.. code-block:: text

   conda activate 가상환경_이름

   # Conda Environment 빠져나오기
   conda deactivate
