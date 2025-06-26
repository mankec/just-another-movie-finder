from pathlib import Path

from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand

from core.files.utils import write_to_json_file
from languages.services.base import Wiki

class Command(BaseCommand):
    # https://en.wikipedia.org/wiki/List_of_official_languages_by_country_and_territory
    help = "Collect from Wikipedia official languages by country and territory."

    def handle(self, *_args, **_options):
        try:
            languages_file = Path("languages/official_languages_by_country_and_region.json")
            content = Wiki.fetch_page_content(
                page="List_of_official_languages_by_country_and_territory"
            )
            soup = BeautifulSoup(content, "html.parser")
            table = soup.div.find("h2", string="List").find_next("table")
            rows = table.tbody.find_all("tr")
            data = {}
            mismatched = []
            for row in rows:
                if row == rows[0]:
                    # For some reason thead doesn't exist and table headers are found in first row of tbody instead.
                    continue
                cells = row.find_all("td")
                cell_country_region = cells[0]
                country_region = cell_country_region.find_next("a").text
                cell_number_of_langs = cells[1]

                if self._has_unicode_chars(country_region):
                    country_region = (country_region.encode("utf-8")
                        .decode("unicode_escape")
                    )

                cell_languages = cells[2]

                languages = []
                if language_ol_list := cell_languages.ol:
                    for li in language_ol_list.find_all("li"):
                        lang = li.find(text=True)
                        if self._has_unicode_chars(lang):
                            lang = lang.encode("utf-8").decode("unicode_escape")
                        languages.append(lang)

                if not languages and (language_ul_list := cell_languages.ul):
                    for li in language_ul_list.find_all("li"):
                        lang = li.find(text=True)
                        if self._has_unicode_chars(lang):
                            lang = lang.encode("utf-8").decode("unicode_escape")
                        languages.append(lang)

                if not languages and (language_links := cell_languages.find_all("a")):
                    for link in language_links:
                        if "[" in link.text:
                            continue
                        if self._has_unicode_chars(link):
                            link = link.encode("utf-8").decode("unicode_escape")
                        languages.append(link.text)

                if not languages and (
                    language_link := cell_languages.find(text=True)
                        .replace("\\n", "")
                        .strip()
                ):
                    languages.append(language_link)
                num = cell_number_of_langs.text.replace("\\n", "")
                if len(languages) != int(num):
                    mismatched.append(country_region)
                data[country_region] = languages
            print(mismatched)
            # write_to_json_file(data, languages_file)
        except Exception as error:
            print(error)

    def _has_unicode_chars(self, string):
        return "\\u" in string
