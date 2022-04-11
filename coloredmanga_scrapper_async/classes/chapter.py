import utility.utils as utils
from classes.page import Page


class Chapter:
    def __init__(self, name: str, chapter_url: str, raw_pages: list[str]) -> None:
        """
        Класс, хранящий название главы и список url-адресов её страниц.
        """
        self.name = name
        self.url = chapter_url
        self.raw_pages = raw_pages

        # список формируется путём обработки данных из self.raw_pages.
        self.pages: list[Page] = []

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

    # @console_log(info={'attr': 'name', 'm': 'обработано'})
    def __build_pages(self) -> None:
        """
        Формирует список страниц данной главы.
        """
        for page in self.raw_pages:
            self.pages.append(Page(page))

    def pages_preparation(self, path: str, page_number: int, is_flatten: bool) -> list[Page]:
        """
        Формирует список страниц манги для загрузки.
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

            page.pages_preparation(permitted_path, number_str)

        return self.pages
