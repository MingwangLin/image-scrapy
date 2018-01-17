# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class TutorialItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class StandingItem(scrapy.Item):
    images = scrapy.Field()
    image_urls = scrapy.Field()


class BooruItem(scrapy.Item):
    images = scrapy.Field()
    image_urls = scrapy.Field()

class MangaItem(scrapy.Item):
    images = scrapy.Field()
    image_urls = scrapy.Field()
