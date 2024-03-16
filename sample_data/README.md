# Introduction

Our sample data folder consists of two .py files:

## `data_pull.py`

- This defines our function ‘Data Puller’ which takes a single
argument (‘platform’) and returns a sample of our data in the
required json format

## `preprocessing.py`

- Here is where we preprocess our data, specifically:

- Removing errors where found

- Merging sets and removing irrelevant columns

- Hashing columns that require hashing

## To Use

### In short
```
python preprocess.py
python data_pull.py -p reddit -n 50
```
will get you json for a batch of 50 reddit posts, to stdout. 


### Longer
Clone the repository and run the `preprocessing.py` file. You should only have to do this once. This
should take our data sources, clean them and then create the
processed files which you will create a sample feed from
All data has been saved in the respective folders, i.e Twitter
data is stored in `twitter_data`.

Once this has been run, you can run the  `data_pull.py` file.
This contains the single function `data_puller` which takes a
required platform argument and three optional arguments

- -p --platform, required, must be ‘reddit’, ‘facebook’ or ’twitter’. It is
not case sensitive

- -n or --numposts, number of posts to generate

- -r or --randomseed, set this to different values to get different pots

- -u or --username, This is whatever you like, it will be hashed

It outputs to stdout.

## Notes

There are several important things to consider before running this
file:

1. Our data _is not perfect,_ and there may be erroneous values and
data points that we currently do not have data for. We are in the
process of fixing each of these:

    - **Erroneous values:** We have filtered for a number of these but
        we may miss some. If you find anything that seems incorrect or
        causes errors, please let us know! We will endeavour to fix it as
        quickly as possible

    - **Missing fields:** Each of our platforms has some data fields
        that are missing. We will aim to get data that matches all fields,
        so our sample data may update over time to incorporate additional
        fields

        - **Facebook:** Missing care reacts.

        - **Twitter:** Missing threads and views. Currently includes
        quotes as a substitute. However, all of these appear blank. We
        have subsequently simulated threads with random assignment.

1. Our data is also from various times, but should be fairly general
thematically i.e Not leaning towards particular demographics

## Data

The datasets used are:

### Twitter

Tweets from Jan 1st 2023

- Our dataset consists of randomly selected tweets from the millions of
  tweets that were posted on the 1st of Jan 2023.

- Tweets were randomly selected at ~5 different intervals across the day

- Future data updates may incorporate random samples of tweets from
  different months in the 2022-2023 period. The full dataset is not in
  the repository due to size restrictions

- Unfortunately this set does not contain views per individual tweets.
  We will assess additional sources for this information. Additionally,
  lots of quotes, replies, reposts are all 0

Sourced from

  https://archive.org/download/archiveteam-twitter-stream-2023-01


### Reddit

  **Pushshift.io**:

- Dataset has been sampled from all possible comments and posts for
  April 2023

- No specific subreddits are chosen, and a subset of ~200,000 has been
  chosen as our dataset to sample from.

- As with our twitter set, our dataset is too large to fully upload to
  the repository

- Comments have been linked to posts randomly.

Sourced From:

  https://academictorrents.com/details/9c263fc85366c1ef8f5bb9da0203f4c8c8db75f4

### Facebook

  2017 News Data:

- Consists of ~20,000 posts from 83 pages, with approximately ~1m
  comments

- Dataset is entirely news focused. We may seek to find more general
  content or posts to improve the diversity of our data

- Our data does not include comments that are in threads, only
  referencing the post_id to which these comments are attached.
  Additionally, ‘care’ reacts are missing and all reacts are only
  applicable to posts.

- Comments have been linked where possible to posts (Due to random
  sampling, comments may be selected without the post being selected)

Sourced from

  https://github.com/jbencina/facebook-news/blob/master/README.md
