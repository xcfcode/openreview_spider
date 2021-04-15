import os
import json
import codecs
from itertools import groupby


def read_paper_list():
    paper_dict = {}
    with codecs.open("./txts/paper_list.txt", "r", "utf-8") as f:
        papers = f.readlines()
        print("spider get {} papers".format(len(papers)))
        for p in papers:
            url = p.split("\t")[0].strip()
            id = url.split("id=")[-1].strip()
            title = p.split("\t")[1].strip()
            year = p.split("\t")[2].strip()
            paper_dict[id] = [title, year]
    return paper_dict


def remove_years(files, paper_dict):
    print("------")
    clean = []
    for file in files:
        id = file.split(".")[0]
        if "ICLR 2013" not in paper_dict[id][1] and "ICLR 2014" not in paper_dict[id][1] and "ICLR 2015" not in \
                paper_dict[id][
                    1] and "ICLR 2016" not in paper_dict[id][1]:
            clean.append(id)
        # else:
        #     print("year", paper_dict[id][1], id)
    print("after clean years: {}".format(len(clean)))
    return clean


def remove_no_reply(files):
    print("------")
    clean = []
    for file in files:
        with codecs.open("./res/{}.json".format(file), "r", "utf-8") as f:
            data = json.load(f)
            items = data["notes"]
            main_id = items[0]["id"]
            flag = False
            for item in items[1:]:
                if "replyto" in item.keys():
                    if item["replyto"] != main_id:
                        flag = True
                        break
                else:
                    break
            if flag:
                clean.append(file)
            # else:
            #     print("noreply", file)
    print("after clean no_reply: {}".format(len(clean)))
    return clean


def remove_no_meta(files, paper_dict):
    print("------")
    clean = []
    for file in files:
        with codecs.open("./res/{}.json".format(file), "r", "utf-8") as f:
            data = json.load(f)
            items = data["notes"]
            flag = False  # no meta review

            if "ICLR 2019" not in paper_dict[file][1]:
                for item in items:
                    if "content" in item.keys():
                        if "decision" in item["content"].keys() and "comment" in item["content"].keys():
                            flag = True
                            break
                if flag:
                    clean.append(file)
                # else:
                #     print("nometa ", file)
            else:
                for item in items:
                    if "content" in item.keys():
                        if "metareview" in item["content"].keys():
                            flag = True
                            break
                if flag:
                    clean.append(file)
                # else:
                #     print("nometa ", file)
    print("after clean no_meta: {}".format(len(clean)))
    return clean


def remove_meta_tooshort(files):
    print("------")
    clean = []
    lens = []
    for file in files:
        with codecs.open("./res/{}.json".format(file), "r", "utf-8") as f:
            data = json.load(f)
            items = data["notes"]
            if "ICLR 2019" not in paper_dict[file][1]:
                for item in items:
                    if "content" in item.keys():
                        if "decision" in item["content"].keys() or "Decision" in item["content"].keys():
                            if "ethics_review" not in item["content"].keys():
                                meta_review = item["content"]["comment"].strip().replace("\r", " ").replace("\n", " ")
            else:
                for item in items:
                    if "content" in item.keys():
                        if "metareview" in item["content"].keys() or "Metareview" in item["content"].keys():
                            meta_review = item["content"]["metareview"].strip().replace("\r", " ").replace("\n", " ")

            if len(meta_review.split()) >= 40:
                clean.append(file)
                lens.append(len(meta_review.split()))

    for k, g in groupby(sorted(lens), key=lambda x: x // 20):
        print('{}-{}: {}'.format(k * 20, (k + 1) * 20 - 1, len(list(g))))

    print("after clean too_short: {}".format(len(clean)))

    return clean


def write(files, paper_dict):
    with codecs.open("./txts/clean_paper_list.txt", "w", "utf-8") as f:
        for file in files:
            f.write(file + "\t" + paper_dict[file][0] + "\t" + paper_dict[file][1] + "\n")


if __name__ == "__main__":
    paper_dict = read_paper_list()
    files = os.listdir("./res/")
    print("have content {} papers".format(len(files)))
    files = remove_years(files, paper_dict)
    files = remove_no_reply(files)
    files = remove_no_meta(files, paper_dict)
    files = remove_meta_tooshort(files)

    write(files, paper_dict)
