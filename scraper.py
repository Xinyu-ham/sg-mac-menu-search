from bs4 import BeautifulSoup
import requests
import json 



class Srcaper:
    def __init__(self, url: str, output_file: str, img_dir: str = 'images'):
        self.url = url
        self.output_file = output_file
        self.img_dir = img_dir

    def get_page(self) -> str:
        '''
        Get HTML page from the URL
        '''
        response = requests.get(self.url)
        return response.text

    def get_menu_items(self, page: str) -> list[dict[str, str | float]]:
        soup = BeautifulSoup(page, 'html.parser')
        divs = soup.find_all('div', class_='kt-inside-inner-col')

        menu_items = []
        seen = set()
        for div in divs:
            if len(div.find_all('p')) == 3:
                # Find the name, description and price of the item
                name, description, price = (p.text for p in div.find_all('p') if p.text)
                name = self._clean_name(name)
                price = self._clean_price(price)
                # Find the img and download it
                img_src = div.find('img').get('src')
                img_file = self._get_img_name(name)
                self._save_img(img_src, img_file)

                self._append_menu_item(menu_items, seen, name, description, price, img_file)
        return menu_items

    def run(self):
        page = self.get_page()
        menu_items = self.get_menu_items(page)
        self._write_to_file(menu_items)

    def _write_to_file(self, menu_items: list[dict[str, str | float]]) -> None:
        '''
        Write the menu items to the output file as JSON
        '''
        with open(self.output_file, 'w') as f:
            json.dump(menu_items, f, indent=4)

    def _clean_name(self, name: str) -> str:
        '''
        Remove leading spaces and replace non-breaking spaces with regular spaces
        '''
        if name.startswith(' '):
            name = name[1:]
        return name.replace('\u00a0', '')
    
    def _clean_price(self, price: str) -> float:
        '''
        Remove leading spaces and the Price: S$ prefix
        '''
        return float(price[15:])

    def _get_img_name(self, name: str) -> str:
        '''
        Lower case, removed spaces with underscores and remove colons from the name
        '''
        return f"{self.img_dir}/{name.lower().replace(':', '').replace(' ', '_')}.jpg"
    
    def _save_img(self, img_src: str, img_name: str) -> None:
        '''
        Save the image from img_src to img_name
        '''
        with open(img_name, 'wb') as f:
            f.write(requests.get(img_src).content)

    def _append_menu_item(self, menu_items: list[dict[str, str | float]], seen: set[str], name: str, description: str, price: float, img_file: str) -> None:
        if name not in seen:
            seen.add(name)
            menu_items.append({'name': name, 'description': description, 'price': price, 'img': img_file})
    
    if __name__ == '__main__':
        URL = 'https://mcdonaldsmenusg.com/'
        OUTPUT_FILE = 'data/menu.json'
        scraper = Srcaper(URL, OUTPUT_FILE, img_dir='images')
        scraper.run()
    