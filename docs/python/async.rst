미지원 async 파이썬 함수 구현
=======================================


async ``enumerate`` 함수
---------------------------------------

파이썬의 `enumerate <https://docs.python.org/3/library/functions.html#enumerate>`_ 함수는 비동기를 지원하지 않습니다.
아래와 같이 비동기 ``enumerate`` 함수를 구현할 수 있습니다.

.. code-block:: python

    from typing import AsyncIterator

    async def aenumerate(
        iterable: AsyncIterator[str],
        start: int = 0,
    ) -> AsyncIterator[tuple[int, str]]:
        """Async version of enumerate function."""
        i = start
        async for x in iterable:
            yield i, x
            i += 1


사용 예시:


.. code-block:: python

    import asyncio
    from typing import AsyncIterator

    async def aenumerate(
        iterable: AsyncIterator[str],
        start: int = 0,
    ) -> AsyncIterator[tuple[int, str]]:
        """Async version of enumerate function."""
        i = start
        async for x in iterable:
            yield i, x
            i += 1

    async def async_iterable() -> AsyncIterator[str]:
        for number in ["a", "b", "c", "d", "e"]:
            yield number

    async def main():
        async for i, value in aenumerate(async_iterable()):
            print(f"{i}: {value}")

    asyncio.run(main())

실행 결과:

.. code-block:: text

    0: a
    1: b
    2: c
    3: d
    4: e
