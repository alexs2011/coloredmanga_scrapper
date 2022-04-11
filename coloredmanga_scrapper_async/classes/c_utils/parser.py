import lxml.html

from utility.decorators import timer


class Parser:
    def __init__(self, data: str) -> None:
        """
        Класс, вычленяющий необходимую информацию из данных формата html.
        """
        self.data = data

    @timer
    def parse_manga_page(self) -> tuple[str, dict[str, dict[str, str]]]:
        """
        Разбирает главную страницу манги и находит название манги, а так же тома и главы для соответствующих томов.
        """
        parsed_data: dict[str, dict[str, str]] = {}

        tree = lxml.html.document_fromstring(self.data)

        title: str = tree.xpath("//head/title/text()")[0].split('|')[0].strip()[5:]

        # У некоторых манг на сайте нет томов, только список глав. Обрабатываем такой случай.
        no_volumes = tree.xpath("//*[starts-with(@class, 'main version-chap no-volumn')]")

        vols = no_volumes if no_volumes else tree.xpath("//*[starts-with(@class, 'parent has-child')]")

        for vol in vols:
            vol_name = vol.xpath(".//a/text()")[0].strip()
            if no_volumes:
                vol_name = "No Volumes"
            chapters_names = vol.xpath(".//*[starts-with(@class, 'wp-manga-chapter')]/a/text()")
            chapters_links = vol.xpath(".//*[starts-with(@class, 'wp-manga-chapter')]/a//@href")

            parsed_data[vol_name] = parsed_data.setdefault(vol_name, {})

            for chapter_name, chapter_link in zip(chapters_names, chapters_links):
                parsed_data[vol_name][chapter_name.strip()] = chapter_link

        return title, parsed_data

    # @timer
    def parse_chapter_page(self) -> list[str]:
        """
        Разбирает html-страницу главы и находит ссылки на страницы манги (т.е. изображения).
        """
        parsed_data = []

        tree = lxml.html.document_fromstring(self.data)

        for el in tree.xpath("//*[starts-with(@class, 'page-break')]"):
            parsed_data.append(el.xpath(".//img//@src")[0].strip())

        return parsed_data
