import json
import os

import requests

from classes.c_utils.decorators.retry import retry
from utility.decorators import timer


class Downloader:
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.60 Safari/537.36"
    }

    def __init__(self, link: str) -> None:
        """
        Класс, обеспечивающий загрузку данных по сети и из файла на основе ссылки.
        """
        self.link = link

    @staticmethod
    def __is_status_code_ok(data: requests.models.Response) -> None:
        """
        Проверяет, что в результате выполнения запроса получен код 200 (ОК).
        """
        if data.status_code != 200:
            raise ConnectionError("Удалённый ресурс не отвечает или не существует.")

    @staticmethod
    def __is_content_type_html(data: requests.models.Response) -> None:
        """
        Проверяет, в результате выполнения запроса получены данные в формате html.
        """
        if 'text/html' not in (cont_type := data.headers.get('Content-Type')):
            raise requests.exceptions.InvalidHeader(f"Результат запроса не HTML: {cont_type}")

    def __validate_html_data(self, data: requests.models.Response) -> None:
        """
        Проверка корректности полученных данных.
        """
        self.__is_status_code_ok(data)
        self.__is_content_type_html(data)

    @timer
    def download_html(self) -> str:
        """
        Загружает данные из удалённого источника.
        """
        try:
            data = requests.get(self.link, headers=self.headers, timeout=10)
        except requests.exceptions.ConnectionError:
            raise TimeoutError(f"Сервер не отвечает на запрос по адресу {self.link}.")

        self.__validate_html_data(data)

        return data.text

    def download_local_file(self) -> dict:
        """
        Загружает данные из файла.
        """
        try:
            with open(self.link, 'r', encoding='utf-8') as f_in:
                if os.stat(self.link).st_size == 0:  # если файл пуст
                    raise ValueError("Файл пуст. Произведите загрузку данных из удалённого источника.")
                return json.load(f_in)
        except FileNotFoundError:
            raise FileNotFoundError(
                "Файл отсутствует. Проверьте путь до файла или произведите загрузку данных из удалённого источника."
            )

    @staticmethod
    def __save_img(data: requests.models.Response, path: str) -> None:
        """
        Сохраняет изображение в файл.
        """
        with open(path, 'wb', buffering=0) as f_obj:
            for block in data.iter_content(chunk_size=64 * 1024):
                f_obj.write(block)

    @timer
    # @console_log(info={'attr': 'link', 'm': 'загружено'})
    @retry(retry=5)
    def download_img(self, path: str) -> None:
        """
        Загружает изображение.
        """
        try:
            data = requests.get(self.link, headers=self.headers, stream=True, timeout=10)
        except requests.exceptions.ConnectionError:
            raise TimeoutError(f"Сервер не отвечает на запрос по адресу {self.link}.")

        self.__is_status_code_ok(data)

        try:
            self.__save_img(data, path)
        except requests.exceptions.ConnectionError:
            raise TimeoutError(f"Сервер не отвечает на запрос по адресу {self.link}.")
