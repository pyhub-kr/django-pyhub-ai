from django import forms

from .fields import MultipleImageField


class MessageForm(forms.Form):
    user_text = forms.CharField(
        required=True,
        widget=forms.Textarea,
    )

    # 기본적으로 이미지 여부, 유효성 검사 수행
    # openai api
    #  - 각 이미지 최대 20MB 지원
    #  - 지원 포맷으로 제한
    # 장고 Form Field 내에서 이미지 포맷 변환이나
    # 이미지 파일 크기 조정을 지원할 수도 있습니다.
    images = MultipleImageField(
        required=False,
        max_file_size=20 * 1024 * 1024,
        allowed_extensions=["png", "jpeg", "jpg", "webp", "gif"],
    )
