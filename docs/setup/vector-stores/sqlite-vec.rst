==========
sqlite-vec
==========

``sqlite``\는 단일 머신에서 사용할 수 있는 가볍고 빠른 데이터베이스입니다.
게다가 PostgreSQL 등의 일반적인 RDBMS 서버와 다르게 별도의 관리도 필요하지 않습니다.
단지 파일일 뿐 이거든요. 파이썬 기본 라이브러리로 제공됩니다.

``sqlite-vec`` 라이브러리는 SQLite 데이터베이스에서 벡터 연산을 지원하는 확장 라이브러리입니다.
임베딩 벡터를 ``sqlite`` 데이터베이스에 효율적으로 저장하고
벡터 간 거리도 계산할 수 있어, 간편하게 벡터 데이터베이스를 구축할 수 있습니다.

`sqlite-vec 공식문서 API#distance <https://alexgarcia.xyz/sqlite-vec/api-reference.html#distance>`_\에 따르면
다음 3개의 Distance 함수를 제공합니다.

#. ``vec_distance_cosine(a, b)``

   - 코사인 거리 (Cosine Distance)라고 부르며, 두 벡터 간의 각도를 측정하는 지표입니다.
   - **1에서 코사인 유사도를 뺀 값**\입니다.
     코사인 유사도는 -1에서 1 사이의 범위를 가지며, 1에 가까울수록 유사도가 높습니다.
     코사인 거리는 0과 2 사이의 범위를 가지며, 0에 가까울수록 유사도가 높습니다.

#. ``vec_distance_L2(a, b)``

   - 유클리디안 거리 (Euclidean Distance)라고 부르며, 주어진 벡터 간의 직선 거리를 측정하는 지표입니다.,
   - 값이 0에 가까울수록 가깝고, 값이 클수록 멀리 떨어져 있습니다.

#. ``vec_distance_hamming(a, b)``

   - 해밍 거리 (Hamming Distance)라고 부르며, 두 벡터 간의 다른 비트(요소) 수를 측정하는 지표입니다.


운영체제에 따라 지원되지 않는 sqlite 메서드
=================================================

``sqlite-vec`` 라이브러리는 ``sqlite3`` 확장 기능을 사용하는 라이브러리입니다.
그래서 ``sqlite3`` 확장을 로딩하는 ``enable_load_extension`` 메서드가 지원되어야 합니다.
윈도우 파이썬 배포판에서는 기본 지원되지만, 맥/리눅스 배포판에서는 지원되지 않는 버전이 있어
다음과 같이 ``AttributeError`` 예외가 발생할 수 있습니다.
파이썬 버전이 낮아도 발생할 수 있습니다.

리눅스에서는 기본 ``python3``\에서는 SQLite 확장이 지원되지만, ``pyenv`` 등을 통한 직접 빌드를 한 파이썬에서는
빌드 옵션을 지정해주지 않으면 SQLite 확장이 지원되지 않습니다. 도커 리눅스 컨테이너도 기본 파이썬에서는
모두 SQLite 확장이 지원됨을 확인했습니다.

사용하실 파이썬에서 아래 코드를 수행해보시고, ``AttributeError`` 예외가 발생하면 파이썬 재설치가 필요합니다.

.. code-block:: text
    :emphasize-lines: 6

    >>> import sqlite3
    >>> db = sqlite3.connect(":memory:")
    >>> db.enable_load_extension(True)
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    AttributeError: 'sqlite3.Connection' object has no attribute 'enable_load_extension'

운영체제에 맞게 아래 문서를 참고하여 파이썬을 재설치해주시고, 위 코드를 다시 수행해보세요.

* 윈도우 : :doc:`/setup/python/windows`
* 맥 : :doc:`/setup/python/macos`
* 리눅스 : :doc:`/setup/python/linux`

.. tip::

    윈도우 파이썬 배포판은 별도 빌드 과정없이 이미 빌드된 바이너리를 복사하는 프로세스로 설치됩니다.
    윈도우에서는 라이브러리를 사용하는 유저들이 빌드 과정을 구성하기 어렵기 때문에 파이썬도 대개 바이너리로 제공되고,
    마침 ``sqlite3`` 모듈에서 ``enable_load_extension`` 메서드도 지원되고 있네요.

    그에 반해 ``pyenv`` 명령이나 ``asdf`` 명령을 통해 설치된 맥/리눅스 파이썬 배포판은 빌드 과정을 거쳐 설치되는 데,
    이때 빌드되는 머신의 라이브러리 구성에 따라 특정 기능이 지원되지 않도록 빌드될 수 있습니다.
    

sqlite-vec 라이브러리 동작 확인
================================

``sqlite-vec`` 라이브러리를 설치하시고, 쉘 종류에 맞게 아래 코드를 수행해주세요.
명령 끝에 ``uv run python`` 으로 파이썬을 구동하고 있습니다.
현 파이썬에 맞게 명령을 수정해주세요.

.. tab-set::    

    .. tab-item:: 윈도우 파워쉘

        .. code-block:: powershell

            # uv run python 명령으로 실행하기
            (Invoke-WebRequest -Uri "https://gist.githubusercontent.com/allieus/bc1c3a7bef31007441d52f79e6e6c0dd/raw/0fce726a94c2e0961f434f2d811e6b337c4cbb56/check_cosine_distance.py").Content | uv run python -

            # python 명령으로 실행하기
            (Invoke-WebRequest -Uri "https://gist.githubusercontent.com/allieus/bc1c3a7bef31007441d52f79e6e6c0dd/raw/0fce726a94c2e0961f434f2d811e6b337c4cbb56/check_cosine_distance.py").Content | python -

    .. tab-item:: 맥/리눅스 쉘

        .. code-block:: bash

            # uv run python 명령으로 실행하기
            curl "https://gist.githubusercontent.com/allieus/bc1c3a7bef31007441d52f79e6e6c0dd/raw/0fce726a94c2e0961f434f2d811e6b337c4cbb56/check_cosine_distance.py" | uv run python

            # python 명령으로 실행하기
            curl "https://gist.githubusercontent.com/allieus/bc1c3a7bef31007441d52f79e6e6c0dd/raw/0fce726a94c2e0961f434f2d811e6b337c4cbb56/check_cosine_distance.py" | python

다음과 같이 출력되시면 성공입니다. ``sqlite-vec``\를 통해 4차원 임베딩 테이블을 생성하여 벡터 데이터를 저장하고,
``vec_distance_cosine`` 함수를 통해 코사인 거리를 계산하고, 코사인 거리가 가장 작은 3개의 행을 출력합니다.

.. code-block:: text

    sqlite_version=3.45.3, vec_version=v0.1.6
    Top 3 most similar by cosine distance:
    rowid=5, cosine_distance=-1.9868213740892315e-08
    rowid=3, cosine_distance=1.1102230246251565e-16
    rowid=1, cosine_distance=1.552204231813903e-08
