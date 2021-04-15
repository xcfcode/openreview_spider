# -*- coding: utf-8 -*-
# @Time    : 2021/3/21 10:03
# @Author  : Xiachong Feng
# @File    : construct_hierarchical_data.py
# @Software: PyCharm


import codecs
import json


def read_paper_list():
    paper_list = []
    with codecs.open("./txts/clean_paper_list.txt", "r", "utf-8") as f:
        papers = f.readlines()
        for p in papers:
            id = p.split("\t")[0].strip()
            title = p.split("\t")[1].strip()
            year = p.split("\t")[2].strip()
            paper_list.append([id, title, year])
    return paper_list


ICLR_2020_experience_assessment_to_score = {"I have published in this field for several years.": 4,
                                            "I have published one or two papers in this area.": 3,
                                            "I have read many papers in this area.": 2,
                                            "I do not know much about this area.": 1}


def process_reviews_2017(reviews):
    id2review = {}
    temp = {}
    for review in reviews:
        if "Reviewer" in review["signatures"][0]:
            if "comment" not in review["content"].keys():
                if "rating" in review["content"].keys():
                    temp[review["signatures"][0]] = review

    for review in reviews:
        if "Reviewer" in review["signatures"][0]:
            if "comment" not in review["content"].keys():
                if "review" in review["content"].keys():
                    continue
                elif "question" in review["content"].keys():
                    if review["signatures"][0] in temp.keys():
                        pre_review = temp[review["signatures"][0]]
                        if "confidence" in pre_review["content"].keys():
                            #  需要存两个 因为不知道回复的是哪个id，后面查找
                            id2review[review["id"]] = {"type": "review",
                                                       "replyto": review["replyto"],
                                                       "review": review["content"]["question"] + pre_review["content"][
                                                           "review"],
                                                       "title": review["content"]["title"],
                                                       "rating": pre_review["content"]["rating"],
                                                       "confidence": pre_review["content"]["confidence"]}
                            id2review[pre_review["id"]] = {"type": "review",
                                                           "replyto": review["replyto"],
                                                           "review": review["content"]["question"] +
                                                                     pre_review["content"][
                                                                         "review"],
                                                           "title": review["content"]["title"],
                                                           "rating": pre_review["content"]["rating"],
                                                           "confidence": pre_review["content"]["confidence"]}
                    # else:
                    #     print("no")
        else:
            print(review)
            if "comment" in review["content"].keys():
                if "title" in review["content"].keys():
                    title = review["content"]["title"]
                else:
                    title = ""
                id2review[review["id"]] = {"type": "rebuttal", "replyto": review["replyto"],
                                           "comment": review["content"]["comment"],
                                           "title": title}
    return id2review


def process_reviews(reviews):
    # 提取review中的数据，包括review和rebuttal
    if "ICLR.cc/2017" in reviews[0]["invitation"]:
        id2review = process_reviews_2017(reviews)
    else:
        id2review = {}
        for review in reviews:
            if "Reviewer" in review["signatures"][0]:  # review

                if "comment" not in review[
                    "content"].keys():  # review会跟在后面进行comment 已经没有用了 author也会继续跟着后面，但是之后需要删除，需要串起来
                    if "ICLR.cc/2020" in review["signatures"][0]:
                        confidence = ICLR_2020_experience_assessment_to_score[
                            review["content"]["experience_assessment"]]
                        id2review[review["id"]] = {"type": "review", "replyto": review["replyto"],
                                                   "review": review["content"]["review"],
                                                   "title": review["content"]["title"],
                                                   "rating": review["content"]["rating"],
                                                   "confidence": confidence}
                    else:
                        # print(review)
                        id2review[review["id"]] = {"type": "review", "replyto": review["replyto"],
                                                   "review": review["content"]["review"],
                                                   "title": review["content"]["title"],
                                                   "rating": review["content"]["rating"],
                                                   "confidence": review["content"]["confidence"]}
            elif "Authors" in review["signatures"][0]:  # rebuttal

                if "withdrawal confirmation" not in review["content"].keys():  # author会有撤稿信息，不需要考虑
                    id2review[review["id"]] = {"type": "rebuttal", "replyto": review["replyto"],
                                               "comment": review["content"]["comment"],
                                               "title": review["content"]["title"]}
            else:
                pass
    return id2review


def process_paper(item):
    if "TL;DR" in item["content"].keys():
        paper_info = {"title": item["content"]["title"], "authors": item["content"]["authors"],
                      "authorids": item["content"]["authorids"],
                      "summary": item["content"]["TL;DR"],
                      "abstract": item["content"]["abstract"], "keywords": item["content"]["keywords"]}

    elif "one-sentence_summary" in item["content"].keys():
        paper_info = {"title": item["content"]["title"], "authors": item["content"]["authors"],
                      "authorids": item["content"]["authorids"],
                      "summary": item["content"]["one-sentence_summary"],
                      "abstract": item["content"]["abstract"], "keywords": item["content"]["keywords"]}
    else:
        paper_info = {"title": item["content"]["title"], "authors": item["content"]["authors"],
                      "authorids": item["content"]["authorids"],
                      "summary": "",
                      "abstract": item["content"]["abstract"], "keywords": item["content"]["keywords"]}
    return paper_info


def process_meta(item):
    if "metareview" in item["content"].keys():
        meta_info = {"decision": item["content"]["recommendation"], "comment": item["content"]["metareview"]}
    else:
        meta_info = {"decision": item["content"]["decision"], "comment": item["content"]["comment"]}
    return meta_info


def process_items(items):
    reviews = []
    paper_info = None
    meta_info = None
    for item in items:
        if "authors" in item["content"].keys():
            # paper information
            if not paper_info:
                item = process_paper(item)
                paper_info = item
            else:  # 如果在已经有了paper info的情况下又有了paper info那就是有问题的
                print("paper info error")
                print(item)
                exit()
        elif "decision" in item["content"].keys() or "metareview" in item[
            "content"].keys():
            if "ethics_review" not in item["content"].keys():
                # meta review information
                if not meta_info:
                    item = process_meta(item)
                    meta_info = item
                else:
                    print("meta info error")
                    print(item)
                    exit()
        else:
            # review information
            if "ICLR" in item["signatures"][0] or "ICLR.cc/2017" in item[
                "invitation"]:  # 只考虑匿名（官方的reviewer） ICLR17的rebuttal是特殊的
                reviews.append(item)

    # process reviews
    # print(reviews)

    id2review = process_reviews(reviews)


    assert paper_info is not None
    assert meta_info is not None
    assert reviews is not None

    data = {"paper": paper_info, "meta": meta_info, "review": id2review}
    return data


def process_one_paper(paper):
    id, title, year = paper
    f = codecs.open("./res/{}.json".format(id), "r", "utf-8")
    data = json.load(f)  # 读取每一篇论文的数据
    items = data["notes"]  # 读取元组数据
    new_data = process_items(items)
    return new_data


if __name__ == "__main__":
    paper_list = read_paper_list()  # 读取已经经过清理之后的paper list
    print("total {} papers".format(len(paper_list)))

    for paper in paper_list:
        if paper[0] != "HJ5PIaseg":
            print(paper)
            data = process_one_paper(paper)

        with codecs.open("./data/{}.json".format(paper[0]), "w", "utf-8") as f:
            json.dump(data, f)
