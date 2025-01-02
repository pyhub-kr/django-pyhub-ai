import pytest
from django.core.exceptions import ImproperlyConfigured

from pyhub_ai.utils import find_file_in_app, format_map_html


def test_format_map_html():
    # s = format_map_html("{name}: {age}", name="NAME", age="AGE")
    # assert s == "NAME: AGE"

    s = format_map_html("{name}: {age}", name="NAME")
    assert s == "NAME: "


class TestFindFileInApp:
    @pytest.mark.it(
        "등록되지 않은 앱을 지정되고 raise_exception=True 인자가 지정되면, ImproperlyConfigured 예외가 발생해야 합니다."
    )
    def test_unregistered_app_raises_improperly_configured(self):
        with pytest.raises(ImproperlyConfigured):
            find_file_in_app("other_app")

    @pytest.mark.it("앱 내에서 존재하는 파일 경로를 지정하면, 그 파일에 대한 Path 경로를 반환해야만 합니다.")
    def test_existing_file_returns_valid_path(self):
        exist_path = "data/titanic.csv"
        path = find_file_in_app("example", exist_path)
        assert path and path.is_file()

    @pytest.mark.it(
        "앱 내에 존재하지 않는 파일 경로를 지정되고 raise_exception=True 인자가 지정되면, FileNotFoundError 예외가 발생해야 합니다."
    )
    def test_non_existing_file_raises_file_not_found(self):
        not_exist_path = "data/titanic1.csv"
        with pytest.raises(FileNotFoundError):
            find_file_in_app("example", not_exist_path)

    @pytest.mark.it(
        "앱 내에 존재하지 않는 파일 경로를 지정되고 raise_exception=False 인자가 지정되면, None을 반환해야 합니다."
    )
    def test_non_existing_file_returns_none_without_raise(self):
        not_exist_path = "data/titanic1.csv"
        path = find_file_in_app("example", not_exist_path, raise_exception=False)
        assert path is None
