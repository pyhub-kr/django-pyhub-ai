import pytest
from langchain_core.prompts import BasePromptTemplate

from pyhub_ai.mixins import LLMMixin


@pytest.mark.asyncio
class TestLLMMixin:
    @pytest.mark.it("http URL로 지정된 yaml 파일을 PromptTemplate로서 로딩할 수 있어야 합니다.")
    @pytest.mark.parametrize(
        "llm_system_prompt_path, response_text, expected_input_variables",
        [
            (
                "http://example.com/test.yaml",
                """
_type: prompt
input_variables: ["name", "age"]
template: |
    Hello {name}!
    I understand you are {age} years old.
    How can I help you today?
""",
                {"name", "age"},
            ),
            (
                "http://example.com/test.json",
                """
{
    "_type": "prompt",
    "input_variables": ["name", "age"],
    "template": "Hello {name}!\\nI understand you are {age} years old.\\nHow can I help you today?"
}""",
                {"name", "age"},
            ),
        ],
    )
    async def test_llm_system_prompt_path(
        self,
        llm_system_prompt_path,
        response_text,
        expected_input_variables,
    ):
        a = LLMMixin()
        a.llm_system_prompt_path = llm_system_prompt_path

        async def mock_get(*args, **kwargs):
            class MockResponse:
                text = response_text

            return MockResponse()

        import httpx

        httpx.AsyncClient.get = mock_get

        prompt_template = await a.aget_llm_system_prompt_template()
        assert isinstance(prompt_template, BasePromptTemplate)
        assert set(prompt_template.input_variables) == expected_input_variables
