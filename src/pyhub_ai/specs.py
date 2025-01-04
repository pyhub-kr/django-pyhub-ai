from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Dict

from django.utils.functional import cached_property


class LLMModel(str, Enum):
    OPENAI_GPT_4O = "gpt-4o"
    OPENAI_GPT_4O_MINI = "gpt-4o-mini"
    OPENAI_GPT_4_TURBO = "gpt-4-turbo"
    # https://docs.anthropic.com/en/docs/about-claude/models#model-comparison-table
    ANTHROPIC_CLAUDE_3_5_SONNET = "claude-3-5-sonnet-20241022"
    ANTHROPIC_CLAUDE_3_5_HAIKU = "claude-3-5-haiku-20241022"
    ANTHROPIC_CLAUDE_3_OPUS = "claude-3-opus-20240229"
    GOOGLE_GEMINI_1_5_FLASH = "gemini-1.5-flash"
    GOOGLE_GEMINI_1_5_PRO = "gemini-1.5-pro"
    # https://guide.ncloud-docs.com/docs/clovastudio-dev-langchain
    CLOVASTUDIO_HCX_DASH_001 = "HCX-DASH-001"
    CLOVASTUDIO_HCX_003 = "HCX-003"

    @cached_property
    def spec(self) -> "LLMModelSpec":
        """Returns the LLMModelSpec for this model."""
        try:
            return LLM_MODEL_SPECS[self]
        except KeyError:
            raise ValueError(f"Unsupported LLM model: {self}")


@dataclass
class LLMModelSpec:
    max_output_tokens: int
    support_vision: bool = False


# 모델별 설정 정보 (2024.11.15 기준) : https://openai.com/api/pricing/
LLM_MODEL_SPECS: Dict[LLMModel, LLMModelSpec] = {
    # https://platform.openai.com/docs/models#gpt-4o
    LLMModel.OPENAI_GPT_4O: LLMModelSpec(
        max_output_tokens=16_384,
        support_vision=True,
    ),
    # https://platform.openai.com/docs/models#gpt-4o-mini
    LLMModel.OPENAI_GPT_4O_MINI: LLMModelSpec(
        max_output_tokens=16_384,
        support_vision=True,
    ),
    # https://platform.openai.com/docs/models#gpt-4-turbo-and-gpt-4
    LLMModel.OPENAI_GPT_4_TURBO: LLMModelSpec(
        max_output_tokens=4_096,
    ),
    # https://docs.anthropic.com/en/docs/about-claude/models#model-comparison-table
    # https://www.anthropic.com/pricing#anthropic-api
    LLMModel.ANTHROPIC_CLAUDE_3_5_SONNET: LLMModelSpec(
        max_output_tokens=8_192,
        support_vision=True,
    ),
    LLMModel.ANTHROPIC_CLAUDE_3_5_HAIKU: LLMModelSpec(
        max_output_tokens=4_096,
    ),
    LLMModel.ANTHROPIC_CLAUDE_3_OPUS: LLMModelSpec(
        max_output_tokens=4_096,
        support_vision=True,
    ),
    # https://cloud.google.com/vertex-ai/generative-ai/pricing
    LLMModel.GOOGLE_GEMINI_1_5_FLASH: LLMModelSpec(
        max_output_tokens=4_096,
        support_vision=True,
    ),
    LLMModel.GOOGLE_GEMINI_1_5_PRO: LLMModelSpec(
        max_output_tokens=4_096,
        support_vision=True,
    ),
    # https://www.ncloud.com/product/aiService/clovaStudio#pricing
    LLMModel.CLOVASTUDIO_HCX_DASH_001: LLMModelSpec(
        max_output_tokens=2_048,
    ),
    LLMModel.CLOVASTUDIO_HCX_003: LLMModelSpec(
        max_output_tokens=2_048,
    ),
}
