import utility.utils as utils
from classes.chapter import Chapter
from classes.page import Page


class Volume:
    def __init__(self, name: str, chapters: list[dict]) -> None:
        """
        Класс, хранящий название тома и список его глав.
        """
        self.name = name
        self.chapters: list[Chapter] = []

        self.__build_chapters(chapters)

    def __repr__(self):
        """
        Строковое представление класса.
        """
        return f'\n\tname: {self.name},\n' \
               f'\tchapters: {self.chapters}'

    def __len__(self) -> int:
        """
        Возвращает количество глав в томе.
        """
        return len(self.chapters)

    def to_JSON(self):
        volume_dict = {
            "name": self.name,
            "chapters": [chapter.to_JSON() for chapter in self.chapters]
        }
        return volume_dict

    def __build_chapters(self, chapters: list[dict]) -> None:
        """
        Формирует список глав данного тома.
        """
        for ch in chapters:
            self.chapters.append(Chapter(ch['name'], ch['url'], ch['pages']))

    def pages_preparation(self, path: str, is_flatten: bool, start_with: int, end_with: int) -> list[Page]:
        """
        Формирует список страниц манги для загрузки с учетом опциональных ограничений start_with и end_with.
        Данные ограничения могут действовать только при отсутствии у манги томов; в ином случае загружаются все главы.
        """
        path = f"{path}{self.name}\\"
        permitted_path = utils.create_dir(path)

        # Список всех загружаемых страниц.
        downloading_pages_lst = []

        # Вычисляем, какой номер будет у первой страницы главы. Если is_flatten=False, то он всегда равен 1;
        # иначе он равен сумме количества страниц ранее обработанных глав.
        ch_start_page_number = 1
        for ch in self.chapters:
            ch_num = int(ch.name.split()[1])
            if start_with <= ch_num < end_with:
                downloading_pages_lst.extend(
                    ch.pages_preparation(permitted_path, ch_start_page_number, is_flatten)
                )
                if is_flatten:
                    ch_start_page_number += len(ch.pages)
        return downloading_pages_lst
