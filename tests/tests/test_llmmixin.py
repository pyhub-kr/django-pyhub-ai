import httpx
import pytest

from pyhub_ai.mixins import LLMMixin


@pytest.mark.asyncio
class TestLLMMixin:
    @pytest.mark.it("http URL로 지정된 yaml 파일을 PromptTemplate로서 로딩할 수 있어야 합니다.")
    @pytest.mark.parametrize(
        "llm_system_prompt_path, response_text, llm_prompt_context_data, expected_system_prompt",
        [
            (
                "http://example.com/test.yaml",
                """
_type: prompt
input_variables: ["언어"]
template: |
    {언어}로 대화를 나눕시다. 번역/발음없이 {언어}로만 답변해주세요.
""",
                {"언어": "영어"},
                "영어로 대화를 나눕시다. 번역/발음없이 영어로만 답변해주세요.",
            ),
            (
                "http://example.com/test.json",
                """
{
    "_type": "prompt",
    "input_variables": ["언어"],
    "template": "{언어}로 대화를 나눕시다. 번역/발음없이 {언어}로만 답변해주세요."
}""",
                {"언어": "영어"},
                "영어로 대화를 나눕시다. 번역/발음없이 영어로만 답변해주세요.",
            ),
            (
                "http://example.com/test.txt",
                "{언어}로 대화를 나눕시다. 번역/발음없이 {언어}로만 답변해주세요.",
                {"언어": "영어"},
                "영어로 대화를 나눕시다. 번역/발음없이 영어로만 답변해주세요.",
            ),
        ],
    )
    async def test_llm_system_prompt_path(
        self,
        monkeypatch,
        llm_system_prompt_path,
        response_text,
        llm_prompt_context_data,
        expected_system_prompt,
    ):
        a = LLMMixin()
        a.llm_system_prompt_path = llm_system_prompt_path
        a.llm_prompt_context_data = llm_prompt_context_data

        async def mock_get(*args, **kwargs):
            class MockResponse:
                text = response_text

            return MockResponse()

        with monkeypatch.context() as patch:
            patch.setattr(httpx.AsyncClient, "get", mock_get)
            actual_system_prompt = await a.aget_llm_system_prompt()
            assert actual_system_prompt.strip() == expected_system_prompt.strip()
