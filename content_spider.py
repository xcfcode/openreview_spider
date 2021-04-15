import feapder
import codecs
import json


def read_paper_list():
    ids = []
    with codecs.open("txts/paper_list.txt", "r", "utf-8") as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip()
            if line:
                url = line.split("\t")[0].strip()
                id = url.split("id=")[-1]
                ids.append(id)
    return ids


class ContentSpider(feapder.AirSpider):

    def start_requests(self):
        ids = read_paper_list()
        for id in ids:
            yield feapder.Request("https://api.openreview.net/notes?forum={}".format(id))

    def parse(self, request, response):
        content = response.json
        id = content["notes"][0]["forum"]
        with codecs.open("res/{}.json".format(id), "w", "utf-8") as f:
            json.dump(content, f)


if __name__ == "__main__":
    ContentSpider(thread_count=15).start()
