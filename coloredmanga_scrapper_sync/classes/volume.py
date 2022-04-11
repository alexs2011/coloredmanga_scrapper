import utility.utils as utils
from classes.chapter import Chapter


class Volume:
    def __init__(self, name: str, chapters: dict[str, str] | list[dict], from_file: bool = False) -> None:
        """
        Класс, хранящий название тома и список его глав.
        """
        self.name = name
        self.chapters: list[Chapter] = []
        self.from_file = from_file

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

    def __build_chapters_from_url(self, chapters: dict[str, str]) -> None:
        """`
        Формирует список глав для данных, полученных из удалённого источника.
        """
        for chapter_name, chapter_url in chapters.items():
            self.chapters.append(Chapter(chapter_name, chapter_url))

    def __build_chapters_from_file(self, chapters: list[dict]) -> None:
        """`
        Формирует список глав для данных, полученных из файла.
        """
        for ch in chapters:
            self.chapters.append(Chapter(ch['name'], ch['url'], raw_pages=ch['pages'], from_file=True))

    def __build_chapters(self, chapters: dict[str, str] | list[dict]) -> None:
        """
        Формирует список глав данного тома с учётом того, откуда поступают данные.
        """
        if self.from_file:
            self.__build_chapters_from_file(chapters)
        else:
            self.__build_chapters_from_url(chapters)

    def download(self, path: str, is_flatten: bool, start_with: int, end_with: int) -> None:
        """
        Загружает главы манги с учетом опциональных ограничений start_with и end_with и сохраняет их.
        Данные ограничения могут действовать только при отсутствии у манги томов; в ином случае загружаются все главы.
        """
        path = f"{path}{self.name}\\"
        permitted_path = utils.create_dir(path)

        # Вычисляем, какой номер будет у первой страницы главы. Если is_flatten=False, то он всегда равен 1;
        # иначе он равен сумме количества страниц ранее обработанных глав.
        ch_start_page_number = 1
        for ch in self.chapters:
            ch_num = int(ch.name.split()[1])
            if start_with <= ch_num < end_with:
                ch.download(permitted_path, ch_start_page_number, is_flatten)
                if is_flatten:
                    ch_start_page_number += len(ch.pages)
