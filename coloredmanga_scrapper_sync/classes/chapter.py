import utility.utils as utils
from classes.c_utils.downloader import Downloader
from classes.c_utils.parser import Parser
from classes.page import Page
from utility.decorators import console_log


class Chapter:
    def __init__(self, name: str, chapter_url: str, raw_pages: list[str] = None, from_file: bool = False) -> None:
        """
        Класс, хранящий название главы и список url-адресов её страниц.
        """
        self.name = name
        self.url = chapter_url
        self.from_file = from_file

        # список формируется с учётом параметра from_file: либо анализируется страница по адресу self.url, либо
        # обрабатываются данные формата JSON, лежащие в self.raw_pages.
        self.pages: list[Page] = []
        # данные о страницах главы в формате JSON, считанные из файла, если from_file=True, иначе None.
        self.raw_pages = raw_pages

        self.__build_pages()

    def __repr__(self):
        """
        Строковое представление класса.
        """
        return f'\n\t\tname: {self.name},\n' \
               f'\t\turl: {self.url},\n' \
               f'\t\tpages: {self.pages}'

    def to_JSON(self):
        chapter_dict = {
            "name": self.name,
            "url": self.url,
            "pages": [page.to_JSON() for page in self.pages]
        }
        return chapter_dict

    def __len__(self) -> int:
        """
        Возвращает количество страниц в главе.
        """
        return len(self.pages)

    def __get_pages_from_url(self) -> list[str]:
        """
        На основе url-адреса скачивает html-страницу главы и при помощи Parser определяет url-адреса страниц,
        т.е. изображений, в главе.
        """
        downloader = Downloader(self.url)
        chapter_html = downloader.download_html()

        parser = Parser(chapter_html)
        return parser.parse_chapter_page()

    def __build_pages_from_url(self, chapter_pages: list[str]) -> None:
        """`
        Формирует список страниц для данных, полученных из удалённого источника.
        """
        for page in chapter_pages:
            self.pages.append(Page(page))

    def __build_pages_from_file(self) -> None:
        """`
        Формирует список страниц для данных, полученных из файла.
        """
        for page in self.raw_pages:
            self.pages.append(Page(page))

    @console_log(info={'attr': 'name', 'm': 'обработано'})
    def __build_pages(self) -> None:
        """
        Формирует список страниц данной главы с учётом того, откуда поступают данные.
        """
        if self.from_file:
            self.__build_pages_from_file()
        else:
            chapter_pages = self.__get_pages_from_url()
            self.__build_pages_from_url(chapter_pages)

    def download(self, path: str, page_number: int, is_flatten: bool) -> None:
        """
        Загружает страницы манги и сохраняет их.
        """
        if is_flatten:
            permitted_path = path
        else:
            path = f"{path}{self.name}\\"
            permitted_path = utils.create_dir(path)

        number = page_number
        for page in self.pages:
            # Формируем имена страниц: "001" для обычного режима и "0001" для упрощённой иерархии файлов.
            if is_flatten:
                number_str = str(number).rjust(4, "0")
            else:
                number_str = str(number).rjust(3, "0")

            number += 1

            page.download(permitted_path, number_str)
