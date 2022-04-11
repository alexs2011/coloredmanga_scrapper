import json
import os

from classes.manga import Manga
from utility.decorators import console_log, timer

# Название манги и глав могут содержать символы, запрещённые в именах папок Windows.
# В этом случае они должны быть удалены при создании папок.
WINDOWS_PROHIBITED_DIR_NAME_CHARS = ["<", ">", "*", "?", "/", "\\", "|", ":", '"']

# Параметры для запросов.
headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.60 Safari/537.36"
}


@timer
def build_contents(link: str, from_file: bool = False) -> Manga:
    """
    Создаёт и возвращает экземпляр класса Manga.
    В процессе создания происходит загрузка иерархии файлов манги по ссылке link (т.е. томов, глав и страниц) с сайта
    или из предварительно сохранённого файла JSON в зависимости от параметра from_file.
    """
    return Manga(link, from_file)


@console_log(info='Данные сохранены')
def save_contents(manga: Manga, filename: str = "..\\coloredmanga_scrapper_async\\data\\contents.json") -> None:
    """
    Сохраняет содержимое, то есть иерархию томов, глав и страниц, класса Manga в файл в формате JSON.
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f_out:
            json.dump(manga.to_JSON(), f_out, indent=2, ensure_ascii=False)
    except PermissionError:
        raise PermissionError("Файл доступен только для чтения. Измените атрибуты доступа.")


@timer
def download_manga(contents: Manga, dir_root: str, is_flatten: bool = False, start_with: int = 0,
                   end_with: int = 0) -> None:
    """
    Загружает и сохраняет в корневую директорию dir_root мангу, сохраняя при этом иерархию томов и глав на основе
    contents.
    Параметр is_flatten позволяет создавать при сохранении упрощённую иерархию файлов (без папок для глав, т.е. 
    все страницы хранятся просто в папке тома):

    Иерархия при is_flatten=False                   Иерархия при is_flatten=True
    Manga_name.                                     Manga_name.
    +---Volume...                                   \---Volume...
    |   \---Chapter...                                      0001.jpg
    |           001.jpg                                     0002.jpg
    |           002.jpg                                     0003.jpg
    |           003.jpg

    Если у манги есть тома, то параметры start_with и end_with позволяют задать начальный и конечный тома для
    скачивания. Если значение равно 0, то ограничений нет. Если параметр end_with задан, то производится скачивание
    томов до него не включительно, т.е. при start_with=5, end_with=9 будут скачаны тома 5, 6, 7, 8.
    Если томов у манги на сайте нет (только список глав), то данные параметры будут применены к главам.
    """
    contents.download(dir_root, is_flatten, start_with, end_with)


def create_dir(path: str) -> str:
    """
    Создаёт директорию по пути path, при этом из пути удаляются все неподдерживаемые Windows символы. Возвращает 
    путь, по которому была создана директория.
    """
    *path_lst, name = filter(None, path.split("\\"))
    for ch in WINDOWS_PROHIBITED_DIR_NAME_CHARS:
        name = name.replace(ch, "")
    path_lst.append(name)
    new_path = '\\'.join(path_lst) + "\\"
    os.makedirs(new_path, exist_ok=True)
    return new_path
