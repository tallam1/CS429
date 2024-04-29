# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class Cs429ProjectItem(scrapy.Item):
    # define the fields for your item here like:
    url = scrapy.Field()
    review = scrapy.Field()
    title = scrapy.Field()
