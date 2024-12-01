from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Dict

from django.utils.functional import cached_property


class LLMModel(str, Enum):
    OPENAI_GPT_4O = "gpt-4o"
    OPENAI_GPT_4O_MINI = "gpt-4o-mini"
    OPENAI_GPT_4_TURBO = "gpt-4-turbo"

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
}
