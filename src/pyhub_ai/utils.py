import logging
import mimetypes
import re
from base64 import b64decode, b64encode
from enum import Enum
from io import BytesIO
from pathlib import Path
from typing import IO, Dict, List, Optional, Tuple, Union

from django.apps import apps
from django.core.files import File
from django.core.files.base import ContentFile
from django.utils.datastructures import MultiValueDict
from PIL import Image

logger = logging.getLogger(__name__)


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


def find_file_in_apps(*paths: Union[str, Path]) -> Path:
    """주어진 경로에서 파일을 찾아 반환합니다.

    먼저 PYHUB_AI_APP_DIR에서 파일을 찾고, 없으면 설치된 모든 Django 앱에서 순차적으로 검색합니다.

    Args:
        *paths: 찾고자 하는 파일의 경로 구성요소들. str 또는 Path 객체.

    Returns:
        Path: 찾은 파일의 전체 경로

    Raises:
        FileNotFoundError: 주어진 경로에서 파일을 찾을 수 없는 경우
    """

    for app_config in apps.get_app_configs():
        path = Path(app_config.path).joinpath(*paths)
        if path.exists():
            return path

    raise FileNotFoundError(f"{paths} 경로의 파일을 찾을 수 없습니다.")
