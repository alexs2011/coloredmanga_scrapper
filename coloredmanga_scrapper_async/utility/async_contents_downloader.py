import asyncio
from copy import deepcopy

import aiohttp

import utility.utils as utils
from classes.c_utils.parser import Parser


async def get_pages(session: aiohttp.ClientSession, ch_name: str, ch_link: str) -> dict:
    """
    На основе url-адреса асинхронно скачивает html-страницу главы и при помощи Parser определяет url-адреса страниц,
    т.е. изображений, в главе.
    """
    async with session.get(ch_link) as resp:
        ch_html = await resp.text()
        parser = Parser(ch_html)
        pages = parser.parse_chapter_page()
        print(f"Обработано {ch_name}")
        return {
            "name": ch_name,
            "url": ch_link,
            "pages": pages
        }


async def get_vol_chapters(session: aiohttp.ClientSession, vol_name: str, chapters: dict[str, str]) -> dict:
    """
    Обрабатывает главы манги.
    """
    tasks_ch = []
    for ch_name, ch_link in chapters.items():
        tasks_ch.append(asyncio.ensure_future(get_pages(session, ch_name, ch_link)))
    all_chapters = await asyncio.gather(*tasks_ch)
    return {vol_name: all_chapters[::-1]}


async def get_manga_vols(vols: dict[str, dict[str, str]]) -> list[dict[str, list[dict[str, list]]]]:
    """
    Открывает соединение для асинхронной загрузки данных; обрабатывает тома манги.
    """
    connector = aiohttp.TCPConnector(limit=50)  # Число одновременных соединений
    timeout = aiohttp.ClientTimeout(total=60 * 60 * 12)  # устанавливаем максимальное время работы сессии на 12 часов.
    async with aiohttp.ClientSession(headers=utils.headers, connector=connector, timeout=timeout) as session:
        tasks_vols = []
        for vol_name, vol_chapters in vols.items():
            tasks_vols.append(asyncio.ensure_future(get_vol_chapters(session, vol_name, vol_chapters)))
        all_vols = await asyncio.gather(*tasks_vols)
        return all_vols


def get_full_contents(manga_vols: dict[str, dict[str, str]]) -> list[dict[str, list[dict[str, list]]]]:
    """
    Позволяет асинхронно загрузить содержание (ссылки на страницы) для всех глав и томов.
    """
    vols = deepcopy(manga_vols)

    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    vols = asyncio.run(get_manga_vols(vols))
    return vols
