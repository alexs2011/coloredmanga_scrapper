import functools
import os.path
import time
from datetime import datetime


class Retry:
    def __init__(self, func, retry=5):
        """
        Декорирующий класс, многократно выполняющий функцию func при условии, что внутри функции возникло исключение.
        Функция перестаёт выполняться либо после корректного завершения своей работы (не возникает исключений),
        либо по достижению лимита повторов выполнения (параметр retry, по умолчанию равен 5).
        Если достигнут лимит повторов выполнения, то информация об этом логгируется.
        """
        functools.update_wrapper(self, func)
        self.func = func

        self.retry_num = retry

        dt = datetime.now()
        cur_date_time = dt.strftime("%d_%m_%y %H_%M_%S")

        self.log_file_name = f"..\\coloredmanga_scrapper_sync\\log\\{cur_date_time}.log"

    def __call__(self, *args, **kwargs):
        for i in range(self.retry_num):
            try:
                val = self.func(*args, **kwargs)
                print(f"[INFO] Загружено: {args[1]}")
                return val
            except Exception:  # Перехватываем все исключения.
                print(
                    f"[WARNING] Ошибка загрузки {args[1]}.\n"
                    f"Пытаемся произвести загрузку повторно: {i + 1}/{self.retry_num}"
                )
                time.sleep(5)  # Ждём некоторое время перед очередной попыткой выполнить загрузку.
        else:  # Если полностью выполнился цикл for, т.е. данные загрузить так и не удалось.
            print(f"[ERR] Не удалось загрузить {args[1]}. См. {self.log_file_name}")
            with open(self.log_file_name, "a+", encoding='utf-8') as f_out:
                f_out.write(
                    f"from_link: {args[0].link}\n"
                    f"to_file: {args[1]}\n\n"
                )
        return None

    def __del__(self):
        """
        Проверяет, существует ли файл с логами (т.е. были ли ошибки). Если да, то в конце работы программы
        выводит информацию об этом в консоль.
        """
        if os.path.isfile(self.log_file_name):
            print("\n" + "#" * 20)
            print(f"[ERR] Не удалось загрузить часть файлов, смотри {self.log_file_name}")


def retry(retry=5):
    """
    Передаёт опциональный параметр retry (максимальное число повторов) в декорирующий класс Retry.
    """

    def _retry(func):
        return Retry(func, retry)

    return _retry
