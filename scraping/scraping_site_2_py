from .base_scraper import BaseScraper
import pandas as pd
from typing import List, Dict, Tuple
from bs4 import BeautifulSoup


class Site2Scraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.search_configs = [
            {
                'container_class': 'col-sm-7 cocInfo',
                'value_class': 'col-sm-5',
                'identifiers': [
                    '40 Length', '41 Width', '42 Height', '44 Distance axis 1-2',
                    '43 Überhange f/b', '52 Netweight', '55 Roof load',
                    '57 braked', '58 unbraked', '67 Support load',
                    '47 Track Axis 1', '48 Track Axis 2'
                ],
                'next_sibling': True
            },
            {
                'container_class': 'col-sm-5 cocInfo',
                'value_class': 'col-sm-7',
                'identifiers': [
                    '14 Axles/Wheels', '25 Brand / Type', '27 Capacity:',
                    '28 Power / n', '18 Transmission/IA'
                ],
                'next_sibling': True
            },
            {
                'container_class': 'col-sm-2 cocInfo',
                'value_class': 'col-sm-2',
                'identifiers': ['Wet Weigh Kg', 'Cylinder', 'Fuel code'],
                'next_sibling': True,
                'element_type': 'label'
            }
        ]

    def extract_data_by_config(self, soup: BeautifulSoup, config: Dict) -> List[Tuple[str, str]]:
        """Extrae datos según la configuración proporcionada."""
        data = []
        element_type = config.get('element_type', 'div')
        elements = soup.find_all(element_type, class_=config['container_class'])

        for element in elements:
            text = element.get_text(strip=True)
            if any(identifier in text for identifier in config['identifiers']):
                value_element = element.find_next(element_type, class_=config['value_class'])
                if value_element:
                    value = value_element.get_text(strip=True)
                    data.append((text, value))
        return data

    def extract_axle_guarantees(self, soup: BeautifulSoup) -> List[Tuple[str, str]]:
        """Extrae específicamente las garantías de ejes."""
        data = []
        main_element = soup.find('div', class_='col-sm-6 cocInfo', string='54 Axle guarantees')

        if main_element:
            # Extraer garantía delantera (v.)
            v_element = main_element.find_next('div', class_='col-sm-1 cocInfo', string='v.')
            if v_element:
                value_v = v_element.find_next('div', class_='col-sm-5')
                if value_v:
                    data.append((f"54 Axle guarantees v.", value_v.get_text(strip=True)))

            # Extraer garantía trasera (b.)
            b_element = main_element.find_next('div', class_='offset-sm-6 col-sm-1 cocInfo', string='b.')
            if b_element:
                value_b = b_element.find_next('div', class_='col-sm-5')
                if value_b:
                    data.append((f"54 Axle guarantees b.", value_b.get_text(strip=True)))

        return data

    def scrape(self, url: str) -> pd.DataFrame:
        """Método principal para realizar el scraping."""
        soup = self.fetch_page(url)
        all_data = []

        # Extraer datos según las configuraciones
        for config in self.search_configs:
            all_data.extend(self.extract_data_by_config(soup, config))

        # Extraer garantías de ejes
        all_data.extend(self.extract_axle_guarantees(soup))

        return pd.DataFrame(all_data, columns=['Key', 'Value'])
