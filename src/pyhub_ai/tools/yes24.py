import json
from typing import Dict, List, Optional

from bs4 import BeautifulSoup, NavigableString, Tag

from .utils import get_response

BASE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36",
    "Referer": "https://www.melon.com/index.htm",
}


async def search_yes24_books(query: str) -> List[Dict[str, str]]:
    """Yes24 도서 검색을 수행합니다.

    Args:
        query: 검색할 도서명/저자/출판사 등의 검색어

    Returns:
        List[Dict[str, str]]: 검색된 도서들의 정보를 담은 딕셔너리 리스트
            - uid: 도서 ID
            - url: 도서 상세 페이지 URL
            - name: 도서명
            - weight: 검색 가중치
    """

    url = "https://www.yes24.com/Product/searchapi/bulletsearch/goods"

    max_page = 3

    book_list = []
    for page in range(1, max_page + 1):
        params = {
            "query": query,
            "domain": "ALL",
            "page": page,
        }

        res = await get_response(url, params=params)
        json_string = res.text
        obj = json.loads(json_string)

        total = obj["iGoodsTotalCount"]  # ex: 903

        for book in obj["lstSearchKeywordResult"]:
            book_uid = book["GOODDS_INDEXES"]["GOODS_NO"]
            book_url = f"https://www.yes24.com/Product/Goods/{book_uid}"
            book_name = book["GOODDS_INDEXES"]["GOODS_NM"]
            weight = book["GOODDS_INDEXES"]["WEIGHT"]

            book_list.append(
                {
                    "uid": book_uid,
                    "url": book_url,
                    "name": book_name,
                    "weight": weight,
                }
            )

        if len(book_list) >= total:
            break

    return book_list


async def get_yes24_toc(book_url: str) -> Optional[str]:
    """Yes24 도서의 목차 정보를 가져옵니다.

    Args:
        book_url: Yes24 도서 상세 페이지 URL

    Returns:
        Optional[str]: 도서의 목차 텍스트
            목차 정보가 없는 경우 None을 반환합니다.
    """

    res = await get_response(book_url)
    html = res.text
    soup = BeautifulSoup(html, "html.parser")
    el = soup.select_one("#infoset_toc textarea")
    if el:
        toc = ""
        for child_el in el:
            if isinstance(child_el, Tag) and child_el.name == "br":
                toc += "\n"
            elif isinstance(child_el, NavigableString):
                toc += child_el.text
        return toc
    return None
