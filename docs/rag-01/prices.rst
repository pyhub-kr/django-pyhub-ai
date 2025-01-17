비용 계산 함수
=======================

곧 OpenAI LLM API를 호출할텐데요. API는 사용한 토큰 수 만큼 과금이 됩니다.

각 LLM 응답마다 입출력 토큰 수를 알 수 있구요. 토큰 수만 봐서는 비용을 가늠하기 어렵기 때문에
사용된 입출력 토큰수에 기반해서 비용을 계산하는 함수를 작성해서 활용하겠습니다.

`OpenAI API 가격 계산 <https://openai.com/api/pricing/>`_ 문서를 참고했습니다. (2025년 1월 기준)

.. list-table:: OpenAI API 가격
   :header-rows: 1
   :widths: 20, 20, 20
   :class: price-table

   * - Model
     - Input (100만 토큰 당)
     - Output (100만 토큰 당)

   * - **OpenAI gpt-4o-mini**
     - $ 0.15
     - $ 0.6

   * - OpenAI gpt-4o
     - $ 2.5
     - $ 10.0

   * - OpenAI gpt-o1-mini
     - $ 3.0
     - $ 12.0

   * - OpenAI gpt-o1
     - $ 0.15
     - $ 60.0

   * - OpenAI gpt-4o-audio-preview
     - $ 40.0
     - $ 80.0

.. code-block:: python
   :linenos:
   :caption: oneshot.py

   def print_prices(input_tokens: int, output_tokens: int) -> None:
       """OpenAI gpt-4o-mini 기준으로만 원화로 비용 계산"""

       input_price = (input_tokens * 0.15 / 1_000_000) * 1_500
       output_price = (output_tokens * 0.6 / 1_000_000) * 1_500
       print("input: tokens {}, krw {:.4f}".format(input_tokens, input_price))
       print("output: tokens {}, krw {:4f}".format(output_tokens, output_price))

OpenAI API 응답 객체에서 ``usage`` 토큰 수 속성을 활용하여, ``print_prices`` 함수를 호출해보면 아래와 같은 출력을 볼 수 있습니다.

.. code-block:: text

   input: tokens 39, krw 0.0088
   output: tokens 46, krw 0.041400

``print_prices`` 함수는 다음 페이지 :doc:`glance` 코드에 적용되어있습니다.
