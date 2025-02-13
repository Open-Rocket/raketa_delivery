import os
import sys
import json
from lxml.html import fromstring
from parselab.parsing import BasicParser
from parselab.network import NetworkManager
from parselab.cache import FileCache
from config import log


class CityParser(BasicParser):

    data = []

    def __init__(self):
        self.cache = FileCache(
            namespace="russian-cities", path=os.environ.get("CACHE_PATH")
        )
        self.net = NetworkManager()

    def get_coords(self, url):
        try:
            page = self.get_page(url)
            html = fromstring(page)
            span = html.xpath(
                '//span[contains(@class, "coordinates")]//a[@class="mw-kartographer-maplink"]'
            )[0]
            return {"lat": span.get("data-lat"), "lon": span.get("data-lon")}
        except Exception as e:
            log.info(f"Ошибка при получении координат: {e}", file=sys.stderr)
            return {"lat": "", "lon": ""}

    def run(self):
        page = self.get_page("https://ru.wikipedia.org/wiki/Список_городов_России")
        html = fromstring(page)

        for tr in html.xpath("//table/tbody/tr"):
            columns = tr.xpath(".//td")
            if len(columns) != 9:
                continue
            name = columns[2].xpath("./a")[0].text_content().strip()
            url = columns[2].xpath("./a")[0].get("href")
            subject = columns[3].text_content().strip()
            district = columns[4].text_content().strip()
            population = int(columns[5].get("data-sort-value"))

            city = {
                "name": name,
                "subject": subject,
                "district": district,
                "population": population,
            }
            city.update({"coords": self.get_coords("https://ru.wikipedia.org%s" % url)})
            self.data.append(city)

            log.info(name, file=sys.stderr)

        output = sorted(
            self.data,
            key=lambda k: "%s|%s|%s" % (k["name"], k["subject"], k["district"]),
        )

        # Сохранение в файл
        with open("cities.json", "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    city_parser = CityParser()
    city_parser.run()


__all__ = ["city_parser"]
