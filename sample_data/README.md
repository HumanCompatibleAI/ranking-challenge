**INTRODUCTION**

Our sample data folder consists of two .py files:

- **Data_Pull.py:**

  - This defines our function ‘Data Puller’ which takes a single
    argument (‘platform’) and returns a sample of our data in the
    required json format

- **Preprocessing.py:**

  - Here is where we preprocess our data, specifically:

    - Removing errors where found

    - Merging sets and removing irrelevant columns

    - Hashing columns that require hashing

      **PROCESS**
      This file should run as is, and only requires a few steps in order
      to work.

      Clone the repository and run the **Preprocessing.py** file. This
      should take our data sources, clean them and then create the
      processed** **files which you will create a sample feed from
      All data has been saved in the respective folders, i.e Twitter
      data is stored in ‘Twitter Data’.

      Once this has been run, you can run the** Data_Pull.py** file.
      This contains the single function **data_puller **which takes one
      argument and requires 3 inputs. Specifically:



- **Argument:**

  - Platform, which is either ‘reddit’, ‘facebook’ or ’twitter’. It is
    not case sensitive



- **Inputs:**

  - Sample Size (recommend ~30-50k)

  - Seed no

  - Username (This is whatever you like, it will be hashed)

    Once run, this will create a file named “**final\_{platform}\_data”
    **which will contain the sample feed.

    **IMPORTANT NOTES**
    There are several important things to consider before running this
    file:

1.  Our data **is not perfect, **and there may be erroneous values and
    data points that we currently do not have data for. We are in the
    process of fixing each of these:

    - **Erroneous values: **We have filtered for a number of these but
      we may miss some. If you find anything that seems incorrect or
      causes errors, please let us know! We will endeavour to fix it as
      quickly as possible

    - **Missing fields: **Each of our platforms has some data fields
      that are missing. We will aim to get data that matches all fields,
      so our sample data may update over time to incorporate additional
      fields

      - **Reddit: **Missing posts

      - **Facebook: **Missing comment threads and care reacts.
        Additionally posts are not easily linked to their comments

      - **Twitter: **Missing threads and views. Currently includes
        quotes as a substitute. However, all of these appear blank.



1.  Our data is also from various times, but should be fairly general
    thematically i.e Not leaning towards particular demographics


    **DATA **

    The datasets used are:

    **<u>Twitter</u>**

    **Tweets from Jan 1st 2023:**

- Our dataset consists of randomly selected tweets from the millions of
  tweets that were posted on the 1st of Jan 2023.

- Tweets were randomly selected at ~5 different intervals across the day

- Future data updates may incorporate random samples of tweets from
  different months in the 2022-2023 period. The full dataset is not in
  the repository due to size restrictions

- Unfortunately this set does not contain views per individual tweets.
  We will assess additional sources for this information. Additionally,
  lots of quotes, replies, reposts are all 0

- **Sourced from:**
  https://archive.org/download/archiveteam-twitter-stream-2023-01


  <u>Reddit</u>


  **Pushshift.io**:



- Dataset has been sampled from all possible comments and posts for
  April 2023

- No specific subreddits are chosen, and a subset of ~200,000 has been
  chosen as our dataset to sample from.

- As with our twitter set, our dataset is too large to fully upload to
  the repository

- Comments have been linked to posts randomly.

- **Sourced From:
  **https://academictorrents.com/details/9c263fc85366c1ef8f5bb9da0203f4c8c8db75f4

  **<u>Facebook</u>**

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

- **Sourced from**:
  https://github.com/jbencina/facebook-news/blob/master/README.md

