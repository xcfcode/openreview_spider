# OpenReview (Meta-review, Review, Rebuttal) Spider
This is a toy example that aims to extract ICLR [OpenReview](https://openreview.net/) reviews with associated author responses (rebuttal) and meta-review.
Recently, many researchers focus on **Scholarly Document Processing**. I have read some papers on [Review-related SDP](https://github.com/xcfcode/What-I-Have-Read/blob/master/Others.md#review-related-sdp).
I find that current works mainly consider original papers, peer reviews without dive into author response (rebuttal), which is also an important part of the life-cycle of the paper submission.
So I came out with this toy example (hasn't been carefully checked).

This repo may facilitate some downstream tasks like **meta-review generation** or **rebuttal-aware meta-review generation** (*Please pay attention to ethical issues*).

## Env
Install [feapder](https://github.com/Boris-code/feapder)
```
pip install feapder
```

## Main
* `python list_spider.py` Get all ICLR papers --> `txts/paper_list.txt`.
* `python content_spider.py` Get detailed contents for each paper --> `res/*.json`
* `python clean.py`
    * remove files published in 2013, 2014, 2015, 2016.
    * remove files without rebuttal.
    * remove files without meta-review.
    * removes files that meta-review contains no more than 40 words.
* `python construct_hierarchical_data.py` construct final data --> `data/*.json`

