import scrapy
filepath = 'C:/Users/harsh/PycharmProjects/IR Project/pages/'
urlpath = 'C:/Users/harsh/PycharmProjects/IR Project/'
class ToScrapeCSSSpider(scrapy.Spider):
    name = "toscrape"
    allowed_domains = ["uic.edu"]
    start_urls = [
        "https://www.cs.uic.edu/"
    ]
    custom_settings = {'DEPTH_PRIORITY':1, 'SCHEDULER_DISK_QUEUE': 'scrapy.squeues.PickleFifoDiskQueue',
                       'SCHEDULER_MEMORY_QUEUE': 'scrapy.squeues.FifoMemoryQueue'}
    count = 0;
    count_max = 3000;
    url_list = dict()
    def parse(self, response):
        if self.count < self.count_max:
            if response.url not in self.url_list.keys():
                self.url_list[response.url] = 1
                self.count += 1;
                filename = str(self.count) + '.html'
                global filepath
                with open(filepath + filename, 'wb') as f:
                    f.write(response.body);
                with open(urlpath +'urlList.txt', 'a') as x:
                    x.write(response.url + "\n");
                urls = response.css('a::attr(href)')
                for url in urls:
                    yield response.follow(url, callback=self.parse)
        else:
            raise scrapy.exceptions.CloseSpider(reason='Page Count Reached');
            return;