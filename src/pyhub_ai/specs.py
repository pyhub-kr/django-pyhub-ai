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

    @cached_property
    def spec(self) -> "LLMModelSpec":
        """Returns the LLMModelSpec for this model."""
        try:
            return LLM_MODEL_SPECS[self]
        except KeyError:
            raise ValueError(f"Unsupported LLM model: {self}")

    def get_cost(self, input_tokens: int, output_tokens: int) -> Decimal:
        input_cost = input_tokens * self.spec.cost_input_tokens_1m / 1_000_000
        output_cost = output_tokens * self.spec.cost_output_tokens_1m / 1_000_000
        return input_cost + output_cost

    def get_cost_krw(
        self,
        input_tokens: int,
        output_tokens: int,
        usd_rate: float = 1_400,
    ) -> Decimal:
        return self.get_cost(input_tokens, output_tokens) * Decimal(usd_rate)


@dataclass
class LLMModelSpec:
    max_output_tokens: int
    support_vision: bool
    cost_input_tokens_1m: Decimal
    cost_output_tokens_1m: Decimal


# 모델별 설정 정보 (2024.11.15 기준) : https://openai.com/api/pricing/
LLM_MODEL_SPECS: Dict[LLMModel, LLMModelSpec] = {
    # https://platform.openai.com/docs/models#gpt-4o
    LLMModel.OPENAI_GPT_4O: LLMModelSpec(
        max_output_tokens=16_384,
        support_vision=True,
        cost_input_tokens_1m=Decimal("2.5"),
        cost_output_tokens_1m=Decimal("10"),
    ),
    # https://platform.openai.com/docs/models#gpt-4o-mini
    LLMModel.OPENAI_GPT_4O_MINI: LLMModelSpec(
        max_output_tokens=16_384,
        support_vision=True,
        cost_input_tokens_1m=Decimal("0.15"),
        cost_output_tokens_1m=Decimal("0.6"),
    ),
    # https://platform.openai.com/docs/models#gpt-4-turbo-and-gpt-4
    LLMModel.OPENAI_GPT_4_TURBO: LLMModelSpec(
        max_output_tokens=4_096,
        support_vision=False,
        cost_input_tokens_1m=Decimal("10"),
        cost_output_tokens_1m=Decimal("30"),
    ),
    # https://docs.anthropic.com/en/docs/about-claude/models#model-comparison-table
    # https://www.anthropic.com/pricing#anthropic-api
    LLMModel.ANTHROPIC_CLAUDE_3_5_SONNET: LLMModelSpec(
        max_output_tokens=8_192,
        support_vision=True,
        cost_input_tokens_1m=Decimal("3"),
        cost_output_tokens_1m=Decimal("15"),
    ),
    LLMModel.ANTHROPIC_CLAUDE_3_5_HAIKU: LLMModelSpec(
        max_output_tokens=4_096,
        support_vision=False,
        cost_input_tokens_1m=Decimal("0.8"),
        cost_output_tokens_1m=Decimal("4"),
    ),
    LLMModel.ANTHROPIC_CLAUDE_3_OPUS: LLMModelSpec(
        max_output_tokens=4_096,
        support_vision=True,
        cost_input_tokens_1m=Decimal("15"),
        cost_output_tokens_1m=Decimal("75"),
    ),
    # https://cloud.google.com/vertex-ai/generative-ai/pricing
    LLMModel.GOOGLE_GEMINI_1_5_FLASH: LLMModelSpec(
        max_output_tokens=4_096,
        support_vision=True,
        cost_input_tokens_1m=Decimal("0.01875"),
        cost_output_tokens_1m=Decimal("0.0375"),
    ),
    LLMModel.GOOGLE_GEMINI_1_5_PRO: LLMModelSpec(
        max_output_tokens=4_096,
        support_vision=True,
        cost_input_tokens_1m=Decimal("0.3125"),
        cost_output_tokens_1m=Decimal("1.25"),
    ),
}
