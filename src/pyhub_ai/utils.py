import asyncio
import logging
import mimetypes
import re
from base64 import b64decode, b64encode
from collections import defaultdict
from enum import Enum
from io import BytesIO
from pathlib import Path
from typing import IO, AsyncIterator, Dict, List, Optional, Tuple, TypeVar, Union

from django.apps import AppConfig, apps
from django.core.exceptions import ImproperlyConfigured
from django.core.files import File
from django.core.files.base import ContentFile
from django.utils.datastructures import MultiValueDict
from django.utils.html import conditional_escape
from django.utils.safestring import SafeString, mark_safe
from PIL import Image

logger = logging.getLogger(__name__)


T = TypeVar("T")


def encode_image_files(
    files: Optional[List[File]] = None,
    max_size: int = 1024,
    quality: int = 80,
    resampling: Image.Resampling = Image.Resampling.LANCZOS,
) -> List[str]:
    """이미지 파일을 base64로 인코딩하여 반환합니다.

    Args:
        files (Optional[List[File]]): 이미지 파일 목록.
        max_size (int): 최대 허용 픽셀 크기 (가로/세로 중 큰 쪽 기준)
        quality (int): JPEG 품질 설정 (1-100)
        resampling (int): 리샘플링 방법

    Returns:
        List[Dict]: base64로 인코딩된 이미지 파일 목록.
    """
    if not files:
        return []

    encoded_image_urls = []
    for image_file in files:

        # TODO: base64 데이터가 아닌 이미지 http URL 활용하거나, openai 파일 스토리지에 업로드 한후 `file_id` 획득 하여 처리
        # 장시간 실행되는 대화는 base64 대신 URL을 통해 이미지를 전달하는 것이 좋습니다.
        # 모델의 지연 시간은 detail 옵션에서 예상하는 크기보다 이미지 크기를 줄여 개선할 수 있습니다.
        # - low (512px 이하), high (짧은 면은 768 이하, 긴 면은 2000 px 이하)
        # https://platform.openai.com/docs/guides/vision#limitations
        # https://platform.openai.com/docs/guides/vision#calculating-costs
        content_type = mimetypes.guess_type(image_file.name)[0]
        if content_type.startswith("image/"):
            optimized_image, content_type = optimize_image(
                image_file.file,
                max_size=max_size,
                quality=quality,
                resampling=resampling,
            )

            prefix = f"data:{content_type};base64,"
            b64_string = b64encode(optimized_image).decode("utf-8")
            encoded_image_urls.append(f"{prefix}{b64_string}")
        else:
            logger.warning(f"Unsupported file type: {content_type} for {image_file.name}")
    return encoded_image_urls


def optimize_image(
    image_file: IO,
    max_size: int = 1024,
    quality: int = 80,
    resampling: Image.Resampling = Image.Resampling.LANCZOS,
) -> Tuple[bytes, str]:
    """이미지를 최적화하여 bytes로 반환합니다.

    Args:
        image_file: 이미지 파일 객체
        max_size (int): 최대 허용 픽셀 크기 (가로/세로 중 큰 쪽 기준)
        quality (int): JPEG 품질 설정 (1-100)
        resampling (int): 리샘플링 방법

    Returns:
        bytes: 최적화된 이미지의 바이트 데이터
    """
    # 이미지 열기
    img = Image.open(image_file)

    # RGBA to RGB (PNG -> JPEG 변환 시 필요)
    if img.mode == "RGBA":
        bg = Image.new("RGB", img.size, (255, 255, 255))
        bg.paste(img, mask=img.split()[3])
        img = bg

    # 이미지 크기 조정
    if max(img.size) > max_size:
        ratio = max_size / max(img.size)
        width, height = (int(dim * ratio) for dim in img.size)
        img = img.resize((width, height), resampling)

    # 최적화된 이미지를 바이트로 변환
    buffer = BytesIO()
    img.save(buffer, format="JPEG", quality=quality, optimize=True)

    return buffer.getvalue(), "image/jpeg"


def extract_base64_files(request_dict: Dict, base64_field_name_postfix: str = "__base64") -> MultiValueDict:
    """base64로 인코딩된 파일 데이터를 디코딩하여 Django의 MultiValueDict 형태로 반환합니다.

    request_dict에서 field_name_postfix로 끝나는 필드를 찾아 base64로 인코딩된 파일 데이터를 디코딩합니다.
    현재는 이미지 파일만 처리합니다.

    Args:
        request_dict (Dict): 요청 데이터를 담고 있는 딕셔너리.
        base64_field_name_postfix (str): base64로 인코딩된 파일 필드 이름 접미사

    Returns:
        MultiValueDict: 디코딩된 파일들을 담고 있는 Django의 MultiValueDict 객체.
            키는 원본 필드 이름(접미사 제외)이고, 값은 ContentFile 객체들의 리스트.

    Examples:
        >>> files = decode_base64_files({
        ...     "image__base64": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgA..."
        ... })
        >>> files.getlist("image")[0]  # ContentFile 객체 반환
    """
    files = MultiValueDict()
    for field_name in request_dict.keys():
        if field_name.endswith(base64_field_name_postfix):
            file_field_name = re.sub(rf"{base64_field_name_postfix}$", "", field_name)
            file_list: List[File] = []
            for base64_str in request_dict[field_name].split("||"):
                if base64_str.startswith("data:image/"):
                    header, data = base64_str.split(",", 1)
                    matched = re.search(r"data:([^;]+);base64", header)
                    if matched and "image/" in matched.group(1):
                        extension: str = matched.group(1).split("/", 1)[-1]
                        file_name = f"{file_field_name}.{extension}"
                        file_list.append(ContentFile(b64decode(data), name=file_name))

            if file_list:
                files.setlist(file_field_name, file_list)
    return files


class Mimetypes(Enum):
    JPEG = "image/jpeg"
    PNG = "image/png"
    GIF = "image/gif"
    BMP = "image/bmp"
    WEBP = "image/webp"


IMAGE_SIGNATURES = {
    "jpeg": [
        (0, bytes([0xFF, 0xD8, 0xFF]), Mimetypes.JPEG),
        (0, bytes([0xFF, 0xD8, 0xFF, 0xE0]), Mimetypes.JPEG),
        (0, bytes([0xFF, 0xD8, 0xFF, 0xE1]), Mimetypes.JPEG),
    ],
    "png": [(0, bytes([0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A]), Mimetypes.PNG)],
    "gif": [(0, b"GIF87a", Mimetypes.GIF), (0, b"GIF89a", Mimetypes.GIF)],
    "bmp": [(0, bytes([0x42, 0x4D]), Mimetypes.BMP)],
    "webp": [(8, b"WEBP", Mimetypes.WEBP)],
}


def get_image_mimetype(header: bytes) -> Optional[Mimetypes]:
    for format_name, format_sigs in IMAGE_SIGNATURES.items():
        for offset, signature, mimetype in format_sigs:
            if header[offset : offset + len(signature)] == signature:
                return mimetype
    return None


def find_file_in_app(
    app_label: str,
    *paths: Union[str, Path],
    raise_exception: bool = True,
) -> Optional[Path]:
    """지정된 Django 앱에서 파일을 찾습니다.

    Args:
        app_label: 검색할 Django 앱의 레이블
        *paths: 찾고자 하는 파일의 경로 구성요소들. str 또는 Path 객체
        raise_exception: 파일을 찾지 못했을 때 예외를 발생시킬지 여부. 기본값은 True

    Returns:
        찾은 파일의 Path 객체. 파일을 찾지 못하고 raise_exception이 False인 경우 None 반환

    Raises:
        ImproperlyConfigured: 지정된 앱을 찾을 수 없는 경우 (raise_exception이 True일 때)
        FileNotFoundError: 지정된 경로에서 파일을 찾을 수 없는 경우 (raise_exception이 True일 때)
    """
    try:
        app_config: AppConfig = apps.get_app_config(app_label)
    except (KeyError, LookupError):
        if raise_exception:
            raise ImproperlyConfigured(f"{app_label} 앱을 찾을 수 없습니다.")
    else:
        path = Path(app_config.path).joinpath(*paths)
        if path.exists():
            return path

        if raise_exception:
            raise FileNotFoundError(f"{paths} 경로의 파일을 찾을 수 없습니다.")

    return None


def find_file_in_apps(
    *paths: Union[str, Path],
    raise_exception: bool = True,
) -> Optional[Path]:
    """설치된 모든 Django 앱에서 순차적으로 파일을 검색합니다.

    설치된 모든 Django 앱을 순회하면서 지정된 경로의 파일을 찾습니다.
    첫 번째로 발견된 파일의 경로를 반환합니다.

    Args:
        *paths: 찾고자 하는 파일의 경로 구성요소들. str 또는 Path 객체
        raise_exception: 파일을 찾지 못했을 때 예외를 발생시킬지 여부. 기본값은 True

    Returns:
        찾은 파일의 Path 객체. 파일을 찾지 못하고 raise_exception이 False인 경우 None 반환

    Raises:
        FileNotFoundError: 모든 앱에서 파일을 찾을 수 없는 경우 (raise_exception이 True일 때)
    """
    for app_config in apps.get_app_configs():
        path = Path(app_config.path).joinpath(*paths)
        if path.exists():
            return path

    if raise_exception:
        raise FileNotFoundError(f"{paths} 경로의 파일을 찾을 수 없습니다.")

    return None


def sum_and_merge_dicts(*dicts: Dict[str, Union[int, float, Dict]]) -> Dict[str, Union[int, float, Dict]]:
    """
    여러 사전을 병합하여 중첩된 구조를 재귀적으로 처리하고,
    숫자 값은 합산하며, 중첩된 사전은 병합한다.
    """

    def merge_two_dicts(
        dict1: Dict[str, Union[int, float, Dict]], dict2: Dict[str, Union[int, float, Dict]]
    ) -> Dict[str, Union[int, float, Dict]]:
        """
        두 사전을 병합하는 함수 (재귀적으로 처리)
        """
        result = {}
        all_keys = set(dict1.keys()).union(dict2.keys())

        for key in all_keys:
            value1 = dict1.get(key)
            value2 = dict2.get(key)

            if isinstance(value1, dict) and isinstance(value2, dict):
                # 둘 다 사전이면 재귀적으로 병합
                result[key] = merge_two_dicts(value1, value2)
            elif isinstance(value1, (int, float)) and isinstance(value2, (int, float)):
                # 둘 다 숫자 값이면 합산
                result[key] = value1 + value2
            else:
                # 둘 중 하나만 존재하거나 숫자가 아닌 경우 값 유지
                result[key] = value1 if value2 is None else value2

        return result

    # 가변 인자로 받은 사전들을 순차적으로 병합
    merged_result = {}
    for dictionary in dicts:
        merged_result = merge_two_dicts(merged_result, dictionary)

    return merged_result


def format_map_html(format_string: str, fallback: Optional[str] = "", **kwargs) -> SafeString:
    """HTML 이스케이프된 값으로 문자열을 포맷팅합니다.

    Args:
        format_string: 포맷팅할 문자열. 파이썬의 str.format() 스타일 포맷팅을 사용합니다.
        fallback: 키가 없을 때 사용할 기본값. 기본값은 빈 문자열입니다.
        **kwargs: 포맷팅에 사용할 키워드 인자들.

    Returns:
        SafeString: HTML 이스케이프 처리된 값들로 포맷팅된 안전한 문자열.

    Example:
        >>> format_map_html("<p>{name}</p>", name="John")
        SafeString('<p>John</p>')
        >>> format_map_html("<p>{missing}</p>", fallback="N/A")
        SafeString('<p>N/A</p>')

    References:
        django/utils/html.py
    """
    kwargs_safe = {k: conditional_escape(v) for (k, v) in kwargs.items()}
    kwargs_safe = defaultdict(lambda: fallback, kwargs_safe)
    return mark_safe(format_string.format_map(kwargs_safe))


def parse_bool_string(value: Optional[str]) -> bool:
    """문자열을 불리언 값으로 변환합니다.

    Args:
        value: 변환할 문자열. 숫자 또는 'true', 'on', 'yes', '1' 등의 문자열을 허용합니다.

    Returns:
        bool: 변환된 불리언 값.
            - 숫자인 경우: 0이 아닌 값은 True, 0은 False
            - 문자열인 경우: 't', 'o', 'y', '1'로 시작하는 문자열(대소문자 무관)은 True, 그 외는 False

    Examples:
        >>> parse_bool_string("1")
        True
        >>> parse_bool_string("0")
        False
        >>> parse_bool_string("true")
        True
        >>> parse_bool_string("yes")
        True
        >>> parse_bool_string("false")
        False
    """

    if value is None:
        return False

    try:
        return int(value) != 0
    except ValueError:
        return bool(re.match(r"^\s*[toy1]", value.strip(), re.IGNORECASE))


async def amerge(**streams: AsyncIterator[T]) -> AsyncIterator[Tuple[str, T]]:
    """여러 비동기 스트림을 병합하여 순차적으로 처리합니다.

    각 스트림에서 데이터가 준비되는 대로 해당 스트림의 키와 함께 결과를 반환합니다.
    모든 스트림이 종료될 때까지 실행됩니다.

    Args:
        **streams: 키-스트림 쌍으로 구성된 비동기 이터레이터들.
            각 스트림은 키로 식별됩니다.

    Yields:
        Tuple[str, T]: 스트림의 키와 해당 스트림에서 생성된 다음 값의 튜플.

    Raises:
        Exception: 스트림 처리 중 발생한 모든 예외.
            예외 발생 시 실행 중인 모든 태스크가 취소됩니다.

    Example:
        >>> async for key, value in amerge(
        ...     stream1=aiter([1, 2, 3]),
        ...     stream2=aiter(['a', 'b', 'c'])
        ... ):
        ...     print(f"{key}: {value}")
        stream1: 1
        stream2: a
        stream1: 2
        stream2: b
        stream1: 3
        stream2: c
    """
    nexts: Dict[asyncio.Task, str] = {asyncio.create_task(anext(stream)): key for key, stream in streams.items()}

    while nexts:
        done, __ = await asyncio.wait(nexts, return_when=asyncio.FIRST_COMPLETED)
        for task in done:
            key = nexts.pop(task)
            stream = streams[key]
            try:
                yield key, task.result()
                nexts[asyncio.create_task(anext(stream))] = key
            except StopAsyncIteration:
                pass
            except Exception as e:
                for task in nexts:
                    task.cancel()
                raise e
