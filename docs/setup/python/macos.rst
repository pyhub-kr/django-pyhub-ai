macOS 파이썬 설치
==========================


내장 파이썬
------------------

macOS 기본에는 파이썬이 설치되어있습니다. macOS 기본의 파이썬은 시스템에서 사용하는 파이썬이기에 파이썬 버전 업그레이드를 시도하지 마시고,
무시해주세요.

.. code-block:: text

   $ /usr/bin/python3 --version
   Python 3.9.6


homebrew를 통한 파이썬 설치
--------------------------------

``homebrew``\는 대중적인 맥용 팩키지 매니저입니다. ``homebrew``\를 통해서도 파이썬을 설치하실 수도 있지만,
이는 다른 맥용 팩키지들과 의존성 문제가 발생할 수 있어서, 개발목적으로 ``homebrew``\를 통해 파이썬을 설치하는 것을 권장드리지 않습니다.

다른 맥용 팩키지를 ``homebrew``\를 통해 설치하실 때, 파이썬이 설치되더라도 무시해주세요.


pyenv
-----

설치
~~~~~~~~

다양한 파이썬 버전 관리자가 있지만, ``pyenv``\는 가장 널리 쓰이는 파이썬 버전 관리자입니다.
윈도우에서는 일반적으로 이미 빌드된 파이썬 바이너리를 복사하는 방식으로 설치가 되지만,
``pyenv``\는 소스코드를 빌드하는 방식으로 설치가 됩니다.
그래서 빌드할 때 의존성있는 팩키지들을 모두 설치해줘야 하며, 빌드 시간이 10분 이상 소요될 수 있습니다.

https://github.com/pyenv/pyenv 를 참고해서, ``git``\을 통해 수동으로 설치하실 수도 있구요.

아래와 같이 ``homebrew``\를 통해 설치하실 수도 있습니다. 최신 macOS 버전이 아니시라면 ``git``\을 통한 수동 설치를 권장드립니다.

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


설치 가능한 파이썬 버전 목록 확인
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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


3.13.1 설치
~~~~~~~~~~~~~~~~~~

``pyenv install 3.13.1`` 명령으로 3.13.1 버전을 설치해보실 수 있습니다.


.. code-block:: text
   :emphasize-lines: 1

   $ pyenv install 3.13.1
   python-build: use openssl@3 from homebrew
   python-build: use readline from homebrew
   Downloading Python-3.13.1.tar.xz...
   -> https://www.python.org/ftp/python/3.13.1/Python-3.13.1.tar.xz
   Installing Python-3.13.1...
   python-build: use readline from homebrew
   python-build: use ncurses from homebrew
   python-build: use zlib from xcode sdk
   Installed Python-3.13.1 to /Users/allieus/.pyenv/versions/3.13.1

.. admonition:: Ubuntu 리눅스에서는 파이썬 빌드에 의존성있는 팩키지들을 미리 설치해야 합니다.
   :class: dropdown

   리눅스에서 파이썬 빌드에 의존성있는 팩키지들을 미리 설치해야 합니다.
   팩키지들이 설치되어있지 않으면 ``BUILD FAILED`` 나 ``ModuleNotFoundError`` 에러 메시지를 보실 수 있습니다.
   아래는 Ubuntu 24.04 LTS 기준으로 파이썬 3.13.1 버전 빌드 시에 필요했던 팩키지들입니다.

   .. code-block:: text

      $ sudo apt install -y build-essential libssl-dev zlib1g-dev \
                            libncurses5-dev libncursesw5-dev libreadline-dev \
                            libsqlite3-dev libgdbm-dev libdb5.3-dev libbz2-dev \
                            libexpat1-dev liblzma-dev tk-dev libffi-dev

``pyenv``를 통해 설치한 파이썬 목록은 ``pyenv versions`` 명령으로 확인해보실 수 있습니다.

.. code-block:: text
   :emphasize-lines: 1

   $ pyenv versions
   * system (set by /home/allieus/.pyenv/version)
     3.13.1

macOS 시스템에서는 시스템에 설치된 파이썬을 사용하고, 현재 유저 계정에서는 ``3.13.1`` 버전을 전역으로 사용하겠습니다.
``pyenv global 3.13.1`` 명령으로 현재 유저 계정에서는 ``3.13.1`` 버전을 전역으로 지정합니다.
이제 ``python`` 명령은 현재 유저 계정에서 설치된 ``3.13.1`` 버전을 사용하게 됩니다.

.. code-block:: text
   :emphasize-lines: 1-2

   $ pyenv global 3.13.1
   $ pyenv versions
     system
   * 3.13.1 (set by /Users/allieus/.pyenv/version)

터미널을 다시 열어서 ``python`` 명령을 실행해보면, 현재 유저 계정에서 설치된 ``3.13.1`` 버전을 사용하는 것을 확인해보실 수 있습니다.

.. code-block:: text
   :emphasize-lines: 1

   $ python --version
   Python 3.13.1

.. admonition:: 특정 프로젝트에서만 다른 파이썬 버전을 사용하실려면?
   :class: tip

   ``global`` 버전은 한번 설정하시면 가급적 변경하지 마시고,
   특정 프로젝트에서만 다른 파이썬 버전을 사용하실려면, 해당 프로젝트 루트 디렉토리에서 ``pyenv local 3.13.1`` 명령을 실행해주세요.
   그럼 그 디렉토리에 ``.python-version`` 파일이 생기고 그 파일이 있는 디렉토리에서는 ``python`` 명령은
   로컬로 지정한 파이썬으로 동작하게 됩니다.
