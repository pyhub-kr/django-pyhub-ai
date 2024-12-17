import pytest
from langchain.tools import tool

from pyhub_ai.tools import tool_with_retry


@pytest.mark.it("tool 장식자와 tool_with_retry 장식자는 같은 동작을 해야합니다.")
def test_tool_with_retry_decorator():
    @tool
    def func_a_1(a: int, b: int) -> int:
        """docstring ..."""
        return a + b

    @tool_with_retry
    def func_a_2(a: int, b: int) -> int:
        """docstring ..."""
        return a + b

    def base_func(a: int, b: int) -> int:
        """docstring ..."""
        return a + b

    def assert_tools_equal(tool1, tool2):
        """두 tool의 메타데이터와 동작이 동일한지 검증"""

        # 함수명(title)을 제외한 스키마 비교 : type, required, properties, description
        schema1 = tool1.args_schema.schema()
        schema2 = tool2.args_schema.schema()
        schema1.pop("title", None)
        schema2.pop("title", None)
        assert schema1 == schema2

        # 실제 실행 결과도 동일한지 검증
        assert tool1.invoke({"a": 1, "b": 2}) == 3
        assert tool2.invoke({"a": 1, "b": 2}) == 3

    func_b_1 = tool(base_func)
    func_b_2 = tool_with_retry(base_func)

    # 데코레이터 방식과 함수 래핑 방식 각각 테스트
    assert_tools_equal(func_a_1, func_a_2)
    assert_tools_equal(func_b_1, func_b_2)


@pytest.mark.it("tool 장식자에서는 함수에서 예외가 발생하면 예외로 처리되어야 합니다.")
def test_tool_error_handling():
    @tool
    def func_without_retry(a: int, b: int) -> int:
        """docstring ..."""
        raise ValueError("Test error")

    with pytest.raises(ValueError, match="Test error"):
        func_without_retry.invoke({"a": 1, "b": 2})


@pytest.mark.it(
    "tool_with_retry 장식자에서는 함수에서 예외가 발생하더라도 예외없이, 예외 내역을 문자열 타입으로 반환해야 합니다."
)
def test_tool_with_retry_error_handling():
    @tool_with_retry
    def func_with_retry(a: int, b: int) -> int:
        """docstring ..."""
        raise ValueError("Test error")

    exception_str = func_with_retry.invoke({"a": 1, "b": 2})
    assert isinstance(exception_str, str)
    assert "Test error" in exception_str


@pytest.mark.asyncio
@pytest.mark.it("tool_with_retry 장식자는 async 함수도 지원해야 합니다.")
async def test_tool_with_retry_async():
    @tool_with_retry
    async def func1(a: int, b: int) -> int:
        """docstring ..."""
        return a + b

    result = await func1.ainvoke({"a": 1, "b": 2})
    assert result == 3

    @tool_with_retry
    async def func2(a: int, b: int) -> int:
        """docstring ..."""
        raise ValueError("Test async error")

    error_result = await func2.ainvoke({"a": 1, "b": 2})
    assert isinstance(error_result, str)
    assert "Test async error" in error_result
