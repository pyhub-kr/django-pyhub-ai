import json
import re
from typing import Dict, List, Optional

from bs4 import BeautifulSoup

from .utils import get_number_from_string, get_response, remove_quotes

MELON_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36",
    "Referer": "https://www.melon.com/index.htm",
}


async def search_melon_songs(query: str) -> List[Dict[str, str]]:
    """멜론 사이트에서 곡을 검색합니다.

    Args:
        query: 검색할 곡 제목/아티스트/앨범명 등의 검색어

    Returns:
        List[Dict[str, str]]: 검색된 곡들의 정보를 담은 딕셔너리 리스트
            - song_uid: 곡 ID
            - song_name: 곡 제목
            - album_img_url: 앨범 이미지 URL
            - album_uid: 앨범 ID
            - album_name: 앨범명
            - artist_uid: 아티스트 ID
            - artist_name: 아티스트명
    """

    # LLM을 통한 인자에서 쌍따옴표/홑따옴표가 붙기도 합니다.
    # 이를 제거하지 않으면 멜론에서 검색결과가 없습니다.
    query = remove_quotes(query)

    url = "https://www.melon.com/search/keyword/index.json"
    jscallback = "_"
    params = {
        "jscallback": jscallback,
        "query": query,
    }

    res = await get_response(url, params=params, headers=MELON_HEADERS)
    jsonp_string = res.text

    json_string = jsonp_string.replace(f"{jscallback}(", "").replace(");", "")
    obj = json.loads(json_string)

    song_list = []
    for song_content in obj.get("SONGCONTENTS", []):
        song_list.append(
            {
                "song_uid": song_content["SONGID"],
                "song_name": song_content["SONGNAME"],
                "album_img_url": song_content["ALBUMIMG"],
                "album_uid": song_content["ALBUMID"],
                "album_name": song_content["ALBUMNAME"],
                "artist_uid": song_content["ARTISTID"],
                "artist_name": song_content["ARTISTNAME"],
            }
        )

    return song_list


async def get_song_detail(song_id: str) -> Optional[Dict[str, Optional[str | List[str]]]]:
    """멜론 사이트에서 특정 곡의 상세 정보를 가져옵니다.

    Args:
        song_id: 멜론 곡 ID

    Returns:
        Optional[Dict[str, Optional[str | List[str]]]]: 곡의 상세 정보를 담은 딕셔너리
            - name: 곡 제목
            - album_name: 앨범명
            - artist_name: 아티스트명
            - cover_url: 앨범 커버 이미지 URL
            - lyric: 가사
            - genre: 장르 목록
            - published_date: 발매일(YYYY-MM-DD 형식)
    """

    # LLM을 통한 인자에서 쌍따옴표/홑따옴표가 붙기도 합니다.
    # 이를 제거하지 않으면 멜론에서 검색결과가 없습니다.
    song_id = remove_quotes(song_id)

    song_detail_url = f"https://www.melon.com/song/detail.htm?songId={song_id}"

    res = await get_response(song_detail_url, headers=MELON_HEADERS)
    song_html = res.text
    soup = BeautifulSoup(song_html, "html.parser")

    for tag in soup.select(".none, img"):
        tag.extract()

    try:
        name = soup.select_one(".song_name").text.strip()
        album_name = soup.select_one("[href*=goAlbumDetail]").text.strip()
        artist_name = soup.select_one(".artist_name").text.strip()

        try:
            cover_url = soup.select_one(".section_info img")["src"].split("?", 1)[0]
        except TypeError:
            cover_url = None

        keys = [tag.text.strip() for tag in soup.select(".section_info .meta dt")]
        values = [tag.text.strip() for tag in soup.select(".section_info .meta dd")]
        meta_dict = dict(zip(keys, values))

        lyric_tag = soup.select_one(".lyric")
        if lyric_tag:
            inner_html = soup.select_one(".lyric").encode_contents().decode("utf8")
            inner_html = re.sub(r"<!--.*?-->", "", inner_html).strip()
            lyric = re.sub(r"<br\s*/?>", "\n", inner_html).strip()
        else:
            lyric = ""

        genre = [s.strip() for s in meta_dict.get("장르", "").split(",") if s.strip()]
        published_date = meta_dict.get("발매일", "").replace(".", "-") or None

        return {
            "name": name,
            "album_name": album_name,
            "artist_name": artist_name,
            "cover_url": cover_url,
            "lyric": lyric,
            "genre": genre,
            "published_date": published_date,
        }
    except AttributeError:
        return None


async def get_melon_top100() -> List[Dict[str, str | int]]:
    """멜론 실시간 TOP 100 차트 정보를 가져옵니다.

    Returns:
        List[Dict[str, str | int]]: TOP 100 곡 정보 목록
            - song_uid: 곡 ID
            - rank: 순위
            - song_name: 곡 제목
            - artist_uid: 아티스트 ID
            - artist_name: 아티스트명
            - album_uid: 앨범 ID
            - album_name: 앨범명
    """
    page_url = "https://www.melon.com/chart/index.htm"

    res = await get_response(page_url, headers=MELON_HEADERS)
    html = res.text

    # HTML 응답 문자열로부터, 필요한 태그 정보를 추출하기 위해, BeautifulSoup4 객체를 생성합니다.
    soup = BeautifulSoup(html, "html.parser")

    # BeautifulSoup4 객체를 통해 노래 정보를 추출해냅니다.
    song_list = []

    for song_tag in soup.select("#tb_list tbody tr, #pageList tbody tr"):
        play_song_tag = song_tag.select_one("a[href*=playSong]")
        song_name = play_song_tag.text
        __, song_uid = re.findall(r"\d+", play_song_tag["href"])
        song_uid = int(song_uid)

        artist_tag = song_tag.select_one("a[href*=goArtistDetail]")
        artist_name = artist_tag.text
        artist_uid = int(get_number_from_string(artist_tag["href"]))

        album_tag = song_tag.select_one("a[href*=goAlbumDetail]")
        album_uid = int(get_number_from_string(album_tag["href"]))
        album_name = album_tag["title"]
        rank = song_tag.select_one(".rank").text

        song = {
            "song_uid": song_uid,
            "rank": rank,
            "song_name": song_name,
            "artist_uid": artist_uid,
            "artist_name": artist_name,
            "album_uid": album_uid,
            "album_name": album_name,
        }

        song_list.append(song)

    return song_list
