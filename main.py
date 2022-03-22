import requests
import requests_cache
from bs4 import BeautifulSoup

requests_cache.install_cache('demo_cache')


class Scraper(object):

    def __init__(self, current_url):
        self.url = current_url
        self.data = {}

    def make_request(self):
        return requests.get(self.url).text

    def make_soup(self):
        return BeautifulSoup(self.make_request(), 'html.parser')

    @staticmethod
    def clean(dirty_item):
        return dirty_item.text.strip().replace('\n', '')

    def get_title(self):
        soup = self.make_soup()
        page = soup.find(class_='page__main')
        return self.clean(page.h1)

    def get_content(self):
        return self.make_soup().find(class_="mw-parser-output")

    def get_intro(self, content):
        return self.clean(content.p)

    def get_links(self, content):
        links = []
        ul = content.find(id="toc").ul.find_all(class_="toctext")
        for link in ul:
            li = self.clean(link)
            links.append(li)
        return(links)

    def get_color_key(self, content):
        color_table = {}
        colors_tr = content.find(class_='wikitable champions-list-legend').tbody.find_all('tr')
        for item in colors_tr[1:]:
            color = list(map(self.clean, item))
            # print(color)
            color_table[color[1]] = color[3]
        return color_table

    def get_champions(self, content):
        champ_table = {}
        champs_tr = content.find(class_='article-table').tbody.find_all('tr')
        for item in champs_tr[1:]:
            champ = list(map(self.clean, item))
            champ_table[champ[1]] = {
                'classes': champ[3],
                'release date': champ[5],
                'last changed': champ[7],
                'bue essence': champ[9],
                'rp': champ[11],
            }
        return champ_table

    def get_list_scrapped_champions(self, content):
        data = []
        ul = content.find(class_="columntemplate").ul.find_all("li")
        for li in ul:
            data.append(li.text)
        return data

    def get_all_data(self):
        content = self.get_content()
        self.get_list_scrapped_champions(content)
        self.data = {
            "Title": self.get_title(),
            "Intro": self.get_intro(content),
            "Links": self.get_links(content),
            "Keys": self.get_color_key(content),
            "Champions": self.get_champions(content),
            "Scrapped_champions": self.get_list_scrapped_champions(content),
        }
        return self.data


if __name__ == "__main__":
    page = Scraper(r'https://leagueoflegends.fandom.com/wiki/List_of_champions').get_all_data()
    for key, value in page.items():
        print(key, ": ", value)