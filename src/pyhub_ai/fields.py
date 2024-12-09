from typing import List, Optional, Union

from django import forms
from django.core.files.base import File
from django.core.validators import FileExtensionValidator

#
# form fields
#


class MultipleClearableFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleImageField(forms.ImageField):
    widget = MultipleClearableFileInput

    def __init__(
        self,
        *,
        max_file_size: Optional[int] = None,
        allowed_extensions: Optional[List[str]] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.max_file_size = max_file_size
        if allowed_extensions is not None:
            self.validators.append(
                FileExtensionValidator(
                    allowed_extensions=allowed_extensions,
                )
            )

    # clean 메서드 안에서 validate 메서드와 run_validators 메서드가 호출되어 유효성 검사를 수행합니다.
    def validate(self, file: File) -> None:
        super().validate(file)

        if self.max_file_size is not None:
            if file and file.size > self.max_file_size:
                raise forms.ValidationError(
                    f"파일 크기는 {self.max_file_size / (1024 * 1024):.2f}MB를 초과할 수 없습니다. "
                    f"현재 파일 크기: {file.size / (1024 * 1024):.2f}MB"
                )

    def clean(self, value, initial=None) -> Union[List[File], File]:
        single_clean = super().clean
        if isinstance(value, (list, tuple)):
            return [single_clean(v, initial) for v in value]
        else:
            return single_clean(value, initial)
