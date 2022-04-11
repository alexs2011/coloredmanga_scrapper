import math

import utility.utils as utils
from classes.c_utils.downloader import Downloader
from classes.c_utils.parser import Parser
from classes.volume import Volume
from utility.decorators import console_log


class Manga:
    def __init__(self, link: str, from_file: bool) -> None:
        """
        Класс, хранящий название манги и список томов, получаемые на основе ссылки.
        При вызове принимает ссылку (на главную страницу либо на файл JSON) и флаг того, считываются ли данные из файла.
        """
        self.link = link
        self.from_file = from_file

        self.name = None
        self.volumes: list[Volume] = []

        self.__build_volumes()

    def __repr__(self):
        """
        Строковое представление класса.
        """
        return f'name: {self.name},\n' \
               f'url: {self.link},\n' \
               f'volumes: {self.volumes}'

    def __len__(self) -> int:
        """
        Возвращает количество томов в манге.
        """
        return len(self.volumes)

    def to_JSON(self):
        manga_dict = {
            "name": self.name,
            "url": self.link,
            "volumes": [volume.to_JSON() for volume in self.volumes]
        }
        return manga_dict

    @console_log(info='обработана главная страница')
    def __get_vols_from_url(self) -> dict[str, dict[str, str]]:
        """
        На основе url-адреса скачивает главную страницу манги и при помощи Parser определяет название и
        тома, а так же url-адреса глав, соответствующих томам.
        """
        downloader = Downloader(self.link)
        manga_html = downloader.download_html()

        parser = Parser(manga_html)
        self.name, manga_vols = parser.parse_manga_page()

        return manga_vols

    def __get_vols_from_file(self) -> list[dict]:
        """
        На основе файла JSON заполняет поля класса Manga. Возвращает список томов для дальнейшей обработки.
        """
        downloader = Downloader(self.link)
        manga_json = downloader.download_local_file()

        self.link = manga_json['url']
        self.name = manga_json['name']

        return manga_json['volumes']

    def __build_vols_from_utl(self, manga_vols: dict[str, dict[str, str]]) -> None:
        """
        Заполняет список томов для данных, полученных из удалённого источника.
        """
        # обработка только 2-х томов в целях отладки.
        # manga_vols = {k: manga_vols[k] for k in list(manga_vols)[:2]}

        for vol_name, chapters in manga_vols.items():
            # Главы в томах располагаются в обратном порядке, например,
            # от Chapter_8 к Chapter_1, поэтому переворачиваем.
            sorted_chapters = dict(sorted(chapters.items(), key=lambda x: int(x[0].split()[1])))
            self.volumes.append(Volume(vol_name, sorted_chapters))

    def __build_vols_from_file(self, manga_vols: list[dict]) -> None:
        """
        Заполняет список томов для данных, полученных из файла.
        """
        for vol in manga_vols:
            self.volumes.append(Volume(vol['name'], vol['chapters'], from_file=True))

    def __build_volumes(self) -> None:
        """
        Формирует данные, учитывая, откуда они поступают: из файла или удалённого ресурса.
        """
        if self.from_file:
            manga_vols = self.__get_vols_from_file()
            self.__build_vols_from_file(manga_vols)
        else:
            manga_vols = self.__get_vols_from_url()
            self.__build_vols_from_utl(manga_vols)

    @staticmethod
    def __validate_downloading_params(start_with: int, end_with: int) -> None:
        """
        Проверяет правильность параметров ограничения начального и конечного томов (глав, в случае, если томов
        у манги нет) для сохранения.
        """
        if start_with < 0 or end_with < 0:
            raise ValueError("Номер тома или главы не может быть меньше 0.")
        if start_with != 0 and end_with != 0:
            if start_with >= end_with:
                raise ValueError("Номер начального тома или главы больше или равен номеру конечного.")

    def download(self, dir_root: str, is_flatten: bool, start_with: int, end_with: int) -> None:
        """
        Загружает тома манги с учетом опциональных ограничений start_with и end_with, и сохраняет их.
        Если томов у манги нет, то данные ограничения применяются к главам.
        """
        self.__validate_downloading_params(start_with, end_with)

        path = f"{dir_root}{self.name}\\"
        permitted_path = utils.create_dir(path)

        if end_with == 0:
            end_with = math.inf

        for vol in self.volumes:
            # У некоторых манг на сайте нет томов, только главы. Обрабатываем такой случай.
            if len(self.volumes) == 1 and self.volumes[0].name == "No Volumes":
                vol_num = start_with
                start_with_ch = start_with
                end_with_ch = end_with
            else:
                vol_num = int(vol.name.split()[1])
                # Если тома есть, то снимаем ограничения start_with и end_with для глав, т.к. в таком случае
                # они - ограничения на тома.
                start_with_ch = 0
                end_with_ch = math.inf
            if start_with <= vol_num < end_with:
                vol.download(permitted_path, is_flatten, start_with_ch, end_with_ch)
