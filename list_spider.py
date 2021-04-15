import feapder
import codecs

f = codecs.open("txts/paper_list.txt", "w", "utf-8")


class ListSpider(feapder.AirSpider):
    def start_requests(self):
        for i in range(1, 389):
            yield feapder.Request("https://openreview.net/submissions?page={}&venue=ICLR.cc".format(i))

    def parse(self, request, response):

        paper_list = response.xpath('//div[@class="note"]')
        for paper in paper_list:
            title = paper.xpath("./h4/a/text()").extract_first()
            url = paper.xpath("./h4/a/@href").extract_first()
            time = paper.xpath("./ul/li[2]/text()").extract_first()
            if "workshop reply" not in title and "conference review" not in title and "submission review" not in title and "review of" not in title and "workshop review" not in title and "conference reply" not in title and "submission reply" not in title:
                f.write(url + "\t" + title + "\t" + time + "\n")


if __name__ == "__main__":
    ListSpider(thread_count=20).start()
