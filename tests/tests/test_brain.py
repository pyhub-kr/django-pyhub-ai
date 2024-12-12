from dataclasses import dataclass
from enum import Enum

import pytest
from django.template.base import Template

from pyhub_ai.brains import Brain
from pyhub_ai.specs import LLMModel


class Tone(str, Enum):
    PROFESSIONAL = "전문적이고 격식있게"
    FRIENDLY = "친근하게 공감하는"
    CLEAR = "명확하고 간단하게"
    ENERGETIC = "열정적이고 활기차게"
    CALM = "차분하고 신중하게"
    SINCERE = "진정성있게"
    HONEST = "솔직하고 진실되게"
    POSITIVE = "긍정적이고 희망적으로"
    GRATEFUL = "감사하고 존중하는"


class EmojiUsage(str, Enum):
    NONE = "사용안함"  # 이모지를 전혀 사용하지 않음
    MODERATE = "보통"  # 적절한 수준으로 이모지 사용
    HIGH = "많이"  # 많은 이모지 사용
    VERY_HIGH = "매우 많이"  # 매우 많은 이모지 사용


@dataclass
class Example:
    review: str
    response: str


@pytest.mark.asyncio
@pytest.mark.it("LLM을 활용한 단건 응답을 생성하고, Fake LLM을 사용했기에 지정한 답변을 받게 됩니다.")
async def test_brain():
    system_prompt_template = Template(
        """
당신은 전문적인 고객 리뷰 답변 작성자입니다.
당신의 목표는 고객 리뷰에 진정성 있고 진심 어린 응답을 제공하는 것입니다.
고객의 감정을 이해하고, 긍정적/부정적 피드백 모두에 성실하게 답변하세요.

TONE: {{ tone }}
EMOJI_USAGE: {{ emoji_usage }}
PARAGRAPH_COUNT: {{ paragraph_count }}

{% if additional_instructions %}ADDITIONAL_INSTRUCTIONS: {{ additional_instructions }}{% endif %}
{% if examples %}
EXAMPLES (few-shot learning)
{% for example in examples %}
<example>
<review>{{ example.review }}</review>
<response>>{{ example.response }}</response>
</example>
{% endfor %}
{% endif %}

지침:
1. 리뷰 내용을 꼼꼼히 분석하고 맥락에 맞는 답변을 작성하세요.
2. 고객의 피드백에 진심으로 감사를 표현하세요.
3. 구체적인 리뷰 내용을 언급하며 맞춤형 답변을 제공하세요.
4. 전문적이고 친절한 어조(TONE)을 유지하세요.
5. 답변은 PARAGRAPH_COUNT 설정에 따른 문단 수로 작성하세요.
6. 답변에는 태그를 적용하지 말고, 답변 내용으로만 작성하세요.
7. ADDITIONAL_INSTRUCTIONS, EMOJI_USAGE 설정을 반영하세요.
        """
    )
    prompt_context_data = {
        "tone": Tone.FRIENDLY,
        "emoji_usage": EmojiUsage.MODERATE,
        "paragraph_count": 2,
        "examples": [
            Example(
                review="남편에게 한번 사줬더니 가끔 생각난다고 하면서 주문해달라고 해서 주문했어요:) 역시 맛있습니당! ❤️",
                response="남편분과 고객님 모두 맛있게 즐겨주신 것 같아 정말 뿌듯하네요. 😍 직접 로스팅한 원두에 직접 개발한 특제 블랜딩 !!!",
            ),
        ],
    }

    expected_response_text: str = (
        "산미를 즐기시는 고객님, 저희 제품의 특별한 풍미를 만끽해주셔서 정말 기쁩니다! 👌 "
        "섬세하고 깔끔한 산미는 많은 분들이 좋아하는 맛의 특징이기도 하죠. "
        "앞으로도 고객님의 입맛을 만족시킬 수 있도록 최선을 다해 품질 관리에 힘쓰겠습니다. 🍃"
    )

    text = await Brain.aquery(
        user_text="산미가 있어서 좋아하는 맛이에요.",
        model=LLMModel.ANTHROPIC_CLAUDE_3_5_HAIKU,
        system_prompt_template=system_prompt_template,
        prompt_context_data=prompt_context_data,
        # Fake LLM 을 활용합니다.
        fake_responses=[expected_response_text],
    )
    assert text == expected_response_text


# TODO: 페이지 주소를 입력하면, 댓글을 알아서 크롤링해서 table 화, 그리고, 댓글 자동 생성
