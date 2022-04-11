import functools
import time


def timer(func):
    """
    Выводит в консоль время выполнения декорированной функции.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        val = func(*args, **kwargs)
        end = time.time()
        print(f"[INFO] Время выполнения {func.__name__}: {end - start:4f} c.")

        return val

    return wrapper


def console_log(_func=None, *, info=None):
    """
    Выводит в консоль факт выполнения декорированной функции.
    Аргумент info является опциональным и служит для вывода дополнительной информации.
    Пример:
        @console_log(info='Данные сохранены')
        def save_contents(...):...
    Вывод:
        Выполнено: save_contents с сообщением: Данные сохранены
    Если в info передан словарь со структурой
        {'attr': str, 'm': Any}
    то в этом случае значение ключа 'attr' будет расценено как имя атрибута экземпляра класса,
    у которого была вызвана декорированная функция, и будут получены данные этого аттрибута.
    При отсутствии такого аттрибута будет вызван AttributeError.
    Пример:
        @console_log(info={'attr': 'name', 'm': 'обработано'})
        def __build_pages(...):...
    Вывод:
        Выполнено: __build_pages с сообщением: обработано Chapter 17 - High Level, Low Level
    """
    def dec(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            val = func(self, *args, **kwargs)

            print(f"[INFO] Выполнено: {func.__name__}", end=' ')
            allowed_keys = {"attr", "m"}
            if isinstance(info, dict) and set(info.keys()) == allowed_keys:
                try:
                    attr_val = getattr(self, info['attr'])
                except AttributeError:
                    raise AttributeError(f"У класса {self.__class__} отсутствует аттрибут {info['attr']}.")
                print(f"с сообщением: {info['m']} {attr_val}")
            else:
                print(f"с сообщением: {info}" if info else "")

            return val
        return wrapper

    if _func is None:
        return dec
    else:
        return dec(_func)
