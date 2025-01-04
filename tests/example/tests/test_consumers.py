from pathlib import Path
from typing import Optional, Tuple, Type, Union

import pytest

from pyhub_ai.consumers import DataAnalysisChatConsumer
from pyhub_ai.utils import find_file_in_app


@pytest.mark.asyncio
@pytest.mark.django_db
class TestTitanicDataAnalysisChatConsumer:

    @pytest.mark.it("dataframe_path 속성은 get_dataframe 메서드를 통해 정상적으로 DataFrame을 반환해야 합니다.")
    @pytest.mark.parametrize(
        "dataframe_path, expected_exceptions",
        [
            ("data/not-exist.csv", FileNotFoundError),
            ("data/titanic.csv", None),
            (find_file_in_app("example", "data/titanic.csv"), None),
        ],
    )
    async def test_get_dataframe(
        self,
        dataframe_path: Union[str, Path],
        expected_exceptions: Optional[Union[Type[Exception], Tuple[Type[Exception], ...]]],
    ):
        consumer = DataAnalysisChatConsumer()
        consumer.dataframe_path = dataframe_path

        if expected_exceptions is not None:
            with pytest.raises(expected_exceptions):
                consumer.get_dataframe()
        else:
            df = consumer.get_dataframe()
            assert df.shape == (891, 12)
