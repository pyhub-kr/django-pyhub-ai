==========================
macOS에 파이썬 설치
==========================


내장 파이썬
=================

macOS 기본에는 파이썬이 설치되어있습니다. macOS 기본의 파이썬은 시스템에서 사용하는 파이썬이기에 파이썬 버전 업그레이드를 시도하지 마시고,
무시해주세요.

.. code-block:: text

   $ /usr/bin/python3 --version
   Python 3.9.6


homebrew 설치 확인
======================

`homebrew <https://brew.sh>`_\는 대중적인 맥용 팩키지 매니저입니다.
터미널에서 ``brew --version`` 명령으로 설치 여부를 확인하실 수 있습니다.
버전이 출력되지 않고 ``command not found: brew`` 에러 메시지가 출력된다면, 터미널에서 아래 명령으로 설치해주세요.
이 명령은 `homebrew <https://brew.sh>`_ 공식 홈페이지에서 제공하는 명령입니다.

.. code-block:: bash

   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"


최신 sqlite 설치
======================

SQLite 데이터베이스는 ``sqlite-vec``\를 비롯한 다양한 확장 기능이 있습니다. 이를 파이썬에서 사용하기 위해서는 확장 지원이 필요합니다.
`sqlite-vec 공식문서 <https://alexgarcia.xyz/sqlite-vec/python.html#macos-blocks-sqlite-extensions-by-default>`_\에 따르면
맥에 번들로 제공되는 기본 SQLite 라이브러리는 SQLite 확장에 대한 지원이 빠져있다고 합니다.

``pyenv``\를 통해 설치되는 파이썬에서는 기본적으로 SQLite 확장이 지원되지 않습니다. 빌드 시에 빌드 옵션을 지정해줘야만 합니다.
맥에 번들로 설치된 ``sqlite3``\는 ``/usr/bin/sqlite3`` 경로에 있습니다.
``homebrew``\를 통해 ``sqlite3``\를 최신 버전으로 설치합니다.

.. code-block:: bash

    brew install sqlite
    brew link --force sqlite

설치된 경로는 ``brew --prefix sqlite`` 명령으로 확인하실 수 있고, 저는 ``/opt/homebrew/opt/sqlite`` 경로에 설치되었습니다.
이 경로는 맥과 homebrew 버전에 따라 다를 수 있습니다.
Big Sur 맥에서는 ``/usr/local/opt/sqlite`` 경로로 확인됩니다.

환경변수 ``PATH`` 상에서 시스템의 ``/usr/bin/``\가 높은 우선 순위를 가집니다.
맥 기본 ``sqlite3`` 명령이 ``/usr/bin/`` 경로에 저장되어있거든요.
``homebrew``\를 통해 설치한 ``sqlite3`` 경로가 우선 순위를 가지도록 환경변수 ``PATH`` 값을 변경합니다.
터미널에서 아래 명령을 수행해주시고, 쉘 설정파일(zsh의 경우 ``~/.zshrc``, bash의 경우 ``~/.bashrc``)에도 추가해주세요.

.. code-block:: bash

    export PATH="$(brew --prefix sqlite)/bin:$PATH"

이어서 ``which sqlite3`` 명령으로 ``/usr/bin/sqlite3`` 경로가 아닌
``/opt/homebrew/opt/sqlite/bin/sqlite3`` 경로 혹은
``/usr/local/opt/sqlite/bin/sqlite3`` 경로가 출력되는지 확인해주세요.


pyenv 설치
=================

다양한 파이썬 버전 관리자가 있지만, ``pyenv``\는 가장 널리 쓰이는 파이썬 버전 관리자입니다.
다양한 종류와 버전의 파이썬을 설치하고 관리하기 편리합니다.

윈도우에서는 일반적으로 이미 빌드된 파이썬 바이너리를 복사하는 방식으로 설치가 되지만,
``pyenv``\는 소스코드를 빌드하는 방식으로 설치가 됩니다.
그래서 빌드할 때 의존성있는 팩키지들을 모두 설치해줘야 하며, 머신에 따라 빌드 시간이 10분 이상 소요될 수 있습니다.

아래와 같이 ``homebrew``\를 통해 설치하실 수도 있고,
https://github.com/pyenv/pyenv 를 참고해서 ``git``\을 통해 수동으로 설치하실 수도 있구요.
최신 macOS 버전이 아니시라면 ``git``\을 통한 수동 설치를 권장드립니다.

.. code-block:: bash

   # pyenv 설치
   brew update
   brew install pyenv

   # zsh 쉘을 사용하실 경우, pyenv 환경변수를 ~/.zshrc 파일에 추가합니다.
   echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.zshrc
   echo '[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.zshrc
   echo 'eval "$(pyenv init - zsh)"' >> ~/.zshrc

   # bash 쉘을 사용하실 경우, pyenv 환경변수를 ~/.bash_profile 파일에 추가합니다.
   echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bash_profile
   echo '[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bash_profile
   echo 'eval "$(pyenv init - bash)"' >> ~/.bash_profile

.. admonition:: 현재 사용 쉘은 ``echo $SHELL`` 명령으로 확인하실 수 있습니다.
   :class: tip

   macOS Catalina (10.15) 이전에는 맥 기본 쉘이 ``bash`` 였고,
   macOS Catalina (10.15) 부터 맥 기본 쉘이 ``zsh`` 로 변경되었습니다.

쉘 설정을 다시 읽어들이기 위해, 터미널을 종료하신 후 다시 실행해주세요.

``pyenv --help`` 명령이 동작하신다면, pyenv가 정상적으로 설치된 것입니다.

.. code-block:: bash

   pyenv --help


pyenv로 설치 가능한 파이썬 버전 목록 확인
=============================================

``pyenv install --all`` 명령으로 설치 가능한 파이썬 버전 목록을 확인해보실 수 있습니다. 파이썬 ``2.1`` 버전부터 최신 버전까지 지원하며,
이 외에도 ``anaconda3``, ``graalpython``, ``jython``, ``miniconda3``, ``pypy3`` 등 다양한 배포판을 ``pyenv``\를 통해 설치할 수 있습니다.

.. code-block:: text

   $ pyenv install --all

   Available versions:
     생략
     3.12.8
     3.13.0
     3.13.1
     생략
     anaconda3-5.3.1
     생략


pyenv로 파이썬에 sqlite3 지원을 추가하여, 빌드하기
===========================================================

``pyenv`` 명령이나 ``asdf`` 명령을 통해 파이썬을 설치하실 때 이미 빌드된 바이너리를 복사하는 것이 아니라 매번 새롭게 빌드합니다.
파이썬 빌드 시에 방금 설치한 ``sqlite`` 모듈이 사용되도록 환경변수들을 맞춰주고, 파이썬을 빌드합니다.
아래 명령은 파이썬 ``3.13.1`` 버전을 빌드합니다. 원하시는 버전으로 빌드해주세요.

.. code-block:: bash
   :emphasize-lines: 5

   LDFLAGS="-L$(brew --prefix sqlite)/lib" \
   CPPFLAGS="-I$(brew --prefix sqlite/include" \
   CFLAGS="-DSQLITE_ENABLE_LOAD_EXTENSION=1" \
   PYTHON_CONFIGURE_OPTS="--enable-loadable-sqlite-extensions" \
   pyenv install 3.13.1

``pyenv``\를 통해 설치한 파이썬 목록은 ``pyenv versions`` 명령으로 확인하실 수 있습니다.

.. code-block:: text
   :emphasize-lines: 1

   $ pyenv versions
   * system (set by /Users/allieus/.pyenv/version)
     3.13.1

``pyenv global 3.13.1`` 명령으로 현재 유저 계정에서는 ``3.13.1`` 버전을 전역으로 지정합니다.

.. code-block:: text

   pyenv global 3.13.1

현재 유저가 사용하는 ``python`` 명령은 현재 유저 계정에서 설치된 ``3.13.1`` 버전을 사용하게 됩니다.

.. code-block:: text
   :emphasize-lines: 1

   $ pyenv versions
     system
   * 3.13.1 (set by /Users/allieus/.pyenv/version)

터미널을 다시 열어서 ``python`` 명령을 실행해보면, 현재 유저 계정에서 설치된 ``3.13.1`` 버전을 사용하는 것을 확인해보실 수 있습니다.

.. code-block:: text
   :emphasize-lines: 1

   $ python --version
   Python 3.13.1

파이썬 쉘에서 아래 코드가 오류없이 수행이 되면, SQLite 확장도 지원하는 파이썬 빌드 성공입니다.

.. code-block:: python

    import sqlite3
    db = sqlite3.connect(":memory:")
    db.enable_load_extension(True)

.. figure:: ./assets/mac-python-sqlite-extension.png

.. admonition:: 특정 프로젝트에서만 다른 파이썬 버전을 사용하실려면?
   :class: tip

   ``global`` 버전은 한번 설정하시면 가급적 변경하지 마시고,
   특정 프로젝트에서만 다른 파이썬 버전을 사용하실려면, 해당 프로젝트 루트 디렉토리에서 ``pyenv local 3.13.1`` 명령을 실행해주세요.
   그럼 그 디렉토리에 ``.python-version`` 파일이 생기고 그 파일이 있는 디렉토리에서는 ``python`` 명령은
   로컬로 지정한 파이썬으로 동작하게 됩니다.
