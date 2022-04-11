class Page:
    def __init__(self, page_url: str) -> None:
        """
        Класс, хранящий url-адрес страницы и путь, по которому она будет сохранена.
        """
        self.url = page_url

        # путь есть не у всех страниц, а только у тех, которые будут сохранены.
        self.path = None

    def __repr__(self):
        """
        Строковое представление класса.
        """
        return f'\n\t\t\t{self.url}'

    def to_JSON(self):
        return self.url

    def pages_preparation(self, path: str, page_number: str) -> None:
        """
        Определяет расширение у страницы манги и записывает путь, по которому будет сохранена загруженная страница.
        """
        extension = self.url.split(".")[-1]  # Определяем расширение файла.
        self.path = f"{path}{page_number}.{extension}"
