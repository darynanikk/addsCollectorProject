from datetime import datetime

from parsel import Selector


class AddExtractor:

    def __init__(self, html):
        self.tree = Selector(html)

    def extract_image(self):
        return self.tree.css('img').attrib['src']

    def extract_title(self):
        return self.tree.css('.info-container .title .title::text').get().strip()

    def extract_location(self):
        return self.tree.css('.info-container .location span::text').get().strip()

    def extract_date_posted(self):
        return self.tree.css('.info-container .location .date-posted::text').get().strip()

    def extract_description(self):
        return self.tree.css('.info-container .description::text').get().strip()

    def extract_currency(self):
        return self.tree.css('.info-container .price::text').get().strip()

    def get_all_adds(self):
        return self.tree.css('.regular-ad').getall()

    def extract_number_of_beds(self):
        return self.tree.css('.rental-info .bedrooms::text').re_first(r'Beds:\s*(.*)')


class UtilsExtractor:
    def __init__(self, html):
        self.tree = Selector(html)

    def is_next_element_present(self):
        return self.tree.css('.pagination [title="Next"]').get() is not None
