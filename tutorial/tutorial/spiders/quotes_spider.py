import scrapy
import time
from scrapy.selector import Selector
from ..items import StandingItem, BooruItem, MangaItem


class StandingsSpider(scrapy.Spider):
    name = "standings"
    start_urls = ['']

    def parse(self, response):

        query_sql = "SELECT g.id, g.gamename, g.sellday, 'www.getchu.com/soft.phtml?id =' || g.comike as links\
                FROM gamelist g\
                WHERE g.comike is NOT NULL\
                ORDER BY g.sellday\
                "
        return scrapy.FormRequest.from_response(
            response,
            formdata={'sql': query_sql},
            callback=self.after_post
        )

    def after_post(self, response):
        url_lst = response.css("td:contains(getchu)::text").extract()
        # print('urllst----------------------------', url_lst)

        for url in url_lst:
            url = url.strip()
            url = 'http://' + url
            url = url.replace(' =', '=')
            # url = url + '?timestamp={}'.format(time.time())
            yield scrapy.Request(url=url, callback=self.get_standings)

    def redirect(self, response):
        redirect_url = response.css("a:contains('は い')::attr(href)").extract_first()
        if redirect_url is not None:
            url = redirect_url + '?timestamp={}'.format(time.time())
        else:
            url = response.url + '?timestamp={}'.format(time.time())
        yield scrapy.Request(url=url, callback=self.get_standings)

    def get_standings(self, response):
        redirect_url = response.css("a:contains('は い')::attr(href)").extract_first()
        if redirect_url is not None:
            # url = redirect_url + '?timestamp={}'.format(time.time())
            url = redirect_url
            yield scrapy.Request(url=url, callback=self.get_standings)
        else:
            standing = StandingItem()
            # print('==============================')
            relative_img_urls = response.css("img[width='250']::attr(src)").extract()
            absolute_img_urls = self.url_join(relative_img_urls, response)
            # print('-----------------------img------------', absolute_img_urls)
            standing["image_urls"] = absolute_img_urls

            yield standing

    def url_join(self, urls, response):
        joined_urls = []
        for url in urls:
            joined_urls.append(response.urljoin(url))

        return joined_urls


class BooruSpider(scrapy.Spider):
    name = "booru"
    start_urls = ['https://safebooru.org/index.php?page=post&s=list&tags=+1girl+white_background&pid=0']

    def parse(self, response):
        url_lst = response.css("a[href*='&id']::attr(href)").extract()
        # print('urllst----------------------------', url_lst)
        for url in url_lst:
            url = response.urljoin(url)
            yield scrapy.Request(url=url, callback=self.get_standings)
        next_page_url = response.css("a[alt='next']::attr(href)").extract_first()
        if next_page_url is not None:
            yield scrapy.Request(response.urljoin(next_page_url))

    def get_standings(self, response):
        standing = BooruItem()
        relative_img_url = response.css("img[alt*='1girl']::attr(src)").extract_first()
        absolute_img_url = response.urljoin(relative_img_url)
        # print('-----------------------img------------', absolute_img_urls)
        standing["image_urls"] = [absolute_img_url]
        yield standing


class MangaSpider(scrapy.Spider):
    name = "manga"
    start_urls = ['']

    def parse(self, response):
        url_lst = response.css("a[class='gallerythumb']::attr(href)").extract()
        # print('urllst----------------------------', url_lst)
        for url in url_lst:
            url = response.urljoin(url)
            yield scrapy.Request(url=url, callback=self.get_manga)

    def get_manga(self, response):
        manga = MangaItem()
        relative_img_url = response.css("img[src*='galleries']::attr(src)").extract_first()
        absolute_img_url = response.urljoin(relative_img_url)
        # print('-----------------------img------------', absolute_img_urls)
        manga["image_urls"] = [absolute_img_url]
        yield manga


class FullcolorMangaCollectionSpider(scrapy.Spider):
    name = "fullcolor_manga_collection"
    start_urls = ['']

    def parse(self, response):
        url_lst = response.css("a[href*='/g/']::attr(href)").extract()
        # print('urllst----------------------------', url_lst)
        for url in url_lst:
            url = response.urljoin(url)
            yield scrapy.Request(url=url, callback=self.parse_single_manga)
        next_page_url = response.css("a[class='next']::attr(href)").extract_first()
        if next_page_url is not None:
            yield scrapy.Request(response.urljoin(next_page_url))

    def parse_single_manga(self, response):
        manga_type = response.css("a[href='/tag/full-color/']::attr(href)").extract()
        if manga_type != []:
            url_lst = response.css("a[class='gallerythumb']::attr(href)").extract()
            page_start = 4
            page_end = -4
            url_lst = url_lst[page_start:page_end]
            # print('urllst----------------------------', url_lst)
            for url in url_lst:
                url = response.urljoin(url)
                yield scrapy.Request(url=url, callback=self.get_manga_image)

    def get_manga_image(self, response):
        manga = MangaItem()
        relative_img_url = response.css("img[src*='galleries']::attr(src)").extract_first()
        absolute_img_url = response.urljoin(relative_img_url)
        # print('-----------------------img------------', absolute_img_urls)
        manga["image_urls"] = [absolute_img_url]
        yield manga

class BwMangaCollectionSpider(scrapy.Spider):
    name = "bw_manga_collection"
    start_urls = ['']

    def parse(self, response):
        url_lst = response.css("a[href*='/g/']::attr(href)").extract()
        # print('urllst----------------------------', url_lst)
        for url in url_lst:
            url = response.urljoin(url)
            yield scrapy.Request(url=url, callback=self.parse_single_manga)
        next_page_url = response.css("a[class='next']::attr(href)").extract_first()
        if next_page_url is not None:
            yield scrapy.Request(response.urljoin(next_page_url))

    def parse_single_manga(self, response):
        manga_type = response.css("a[href*='/tag/full-color/']::attr(href)").extract()
        if manga_type == []:
            url_lst = response.css("a[class='gallerythumb']::attr(href)").extract()
            page_num = len(url_lst)
            tmp = page_num // 2
            page_start = tmp
            page_end = -10
            url_lst = url_lst[page_start:page_end]
            # print('urllst----------------------------', url_lst)
            for url in url_lst:
                url = response.urljoin(url)
                yield scrapy.Request(url=url, callback=self.get_manga_image)

    def get_manga_image(self, response):
        manga = MangaItem()
        relative_img_url = response.css("img[src*='galleries']::attr(src)").extract_first()
        absolute_img_url = response.urljoin(relative_img_url)
        # print('-----------------------img------------', absolute_img_urls)
        manga["image_urls"] = [absolute_img_url]
        yield manga
