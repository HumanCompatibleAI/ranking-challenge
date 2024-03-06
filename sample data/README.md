{\rtf1\ansi\ansicpg1252\cocoartf2709
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica-Bold;\f1\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
{\*\listtable{\list\listtemplateid1\listhybrid{\listlevel\levelnfc23\levelnfcn23\leveljc0\leveljcn0\levelfollow0\levelstartat1\levelspace360\levelindent0{\*\levelmarker \{disc\}}{\leveltext\leveltemplateid1\'01\uc0\u8226 ;}{\levelnumbers;}\fi-360\li720\lin720 }{\listlevel\levelnfc23\levelnfcn23\leveljc0\leveljcn0\levelfollow0\levelstartat1\levelspace360\levelindent0{\*\levelmarker \{hyphen\}}{\leveltext\leveltemplateid2\'01\uc0\u8259 ;}{\levelnumbers;}\fi-360\li1440\lin1440 }{\listlevel\levelnfc23\levelnfcn23\leveljc0\leveljcn0\levelfollow0\levelstartat1\levelspace360\levelindent0{\*\levelmarker \{hyphen\}}{\leveltext\leveltemplateid3\'01\uc0\u8259 ;}{\levelnumbers;}\fi-360\li2160\lin2160 }{\listname ;}\listid1}
{\list\listtemplateid2\listhybrid{\listlevel\levelnfc0\levelnfcn0\leveljc0\leveljcn0\levelfollow0\levelstartat1\levelspace360\levelindent0{\*\levelmarker \{decimal\})}{\leveltext\leveltemplateid101\'02\'00);}{\levelnumbers\'01;}\fi-360\li720\lin720 }{\listlevel\levelnfc23\levelnfcn23\leveljc0\leveljcn0\levelfollow0\levelstartat1\levelspace360\levelindent0{\*\levelmarker \{hyphen\}}{\leveltext\leveltemplateid102\'01\uc0\u8259 ;}{\levelnumbers;}\fi-360\li1440\lin1440 }{\listlevel\levelnfc23\levelnfcn23\leveljc0\leveljcn0\levelfollow0\levelstartat1\levelspace360\levelindent0{\*\levelmarker \{hyphen\}}{\leveltext\leveltemplateid103\'01\uc0\u8259 ;}{\levelnumbers;}\fi-360\li2160\lin2160 }{\listname ;}\listid2}
{\list\listtemplateid3\listhybrid{\listlevel\levelnfc23\levelnfcn23\leveljc0\leveljcn0\levelfollow0\levelstartat1\levelspace360\levelindent0{\*\levelmarker \{disc\}}{\leveltext\leveltemplateid201\'01\uc0\u8226 ;}{\levelnumbers;}\fi-360\li720\lin720 }{\listname ;}\listid3}
{\list\listtemplateid4\listhybrid{\listlevel\levelnfc23\levelnfcn23\leveljc0\leveljcn0\levelfollow0\levelstartat1\levelspace360\levelindent0{\*\levelmarker \{disc\}}{\leveltext\leveltemplateid301\'01\uc0\u8226 ;}{\levelnumbers;}\fi-360\li720\lin720 }{\listname ;}\listid4}
{\list\listtemplateid5\listhybrid{\listlevel\levelnfc23\levelnfcn23\leveljc0\leveljcn0\levelfollow0\levelstartat1\levelspace360\levelindent0{\*\levelmarker \{disc\}}{\leveltext\leveltemplateid401\'01\uc0\u8226 ;}{\levelnumbers;}\fi-360\li720\lin720 }{\listname ;}\listid5}}
{\*\listoverridetable{\listoverride\listid1\listoverridecount0\ls1}{\listoverride\listid2\listoverridecount0\ls2}{\listoverride\listid3\listoverridecount0\ls3}{\listoverride\listid4\listoverridecount0\ls4}{\listoverride\listid5\listoverridecount0\ls5}}
\paperw11900\paperh16840\margl1440\margr1440\vieww34000\viewh21380\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\b\fs48 \cf0 INTRODUCTION
\f1\b0\fs24 \
\
Our sample data folder consists of two .py files:\
\pard\tx220\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\li720\fi-720\pardirnatural\partightenfactor0
\ls1\ilvl0\cf0 {\listtext	\uc0\u8226 	}
\f0\b Data_Pull.py:
\f1\b0 \
\pard\tx940\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\li1440\fi-1440\pardirnatural\partightenfactor0
\ls1\ilvl1\cf0 {\listtext	\uc0\u8259 	}This defines our function \'91Data Puller\'92 which takes a single argument (\'91platform\'92) and returns a sample of our data in the required json format\
\pard\tx220\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\li720\fi-720\pardirnatural\partightenfactor0
\ls1\ilvl0\cf0 {\listtext	\uc0\u8226 	}
\f0\b Preprocessing.py:
\f1\b0 \
\pard\tx940\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\li1440\fi-1440\pardirnatural\partightenfactor0
\ls1\ilvl1\cf0 {\listtext	\uc0\u8259 	}Here is where we preprocess our data, specifically:\
\pard\tx1660\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\li2160\fi-2160\pardirnatural\partightenfactor0
\ls1\ilvl2\cf0 {\listtext	\uc0\u8259 	}Removing errors where found \
{\listtext	\uc0\u8259 	}Merging sets and removing irrelevant columns\
{\listtext	\uc0\u8259 	}Hashing columns that require hashing\
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0
\cf0 \

\f0\b\fs48 PROCESS
\fs24 \

\f1\b0 This file should run as is, and only requires a few steps in order to work.\
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\b \cf0 \
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f1\b0 \cf0 All data has been saved in the respective folders, i.e Twitter data is stored in \'91Twitter Data\'92. \
\
When running the file, all the users need to set is the platform and when prompted, input a seed number and their username.\
\
\

\f0\b\fs48 IMPORTANT NOTES\

\f1\b0\fs24 There are several important things to consider before running this file:\
\pard\tx220\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\li720\fi-720\pardirnatural\partightenfactor0
\ls2\ilvl0\cf0 {\listtext	1)	}Our data 
\f0\b is not perfect, 
\f1\b0 and there may be erroneous values and data points that we currently do not have data for. We are in the process of fixing each of these:\
\pard\tx940\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\li1440\fi-1440\pardirnatural\partightenfactor0
\ls2\ilvl1\cf0 {\listtext	\uc0\u8259 	}
\f0\b Erroneous values: 
\f1\b0 We have filtered for a number of these but we may miss some. If you find anything that seems incorrect or causes errors, please let us know! We will endeavour to fix it as quickly as possible\
{\listtext	\uc0\u8259 	}
\f0\b Missing fields: 
\f1\b0 Each of our platforms has some data fields that are missing. We will aim to get data that matches all fields, so our sample data may update over time to incorporate additional fields\
\pard\tx1660\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\li2160\fi-2160\pardirnatural\partightenfactor0
\ls2\ilvl2\cf0 {\listtext	\uc0\u8259 	}
\f0\b Reddit: 
\f1\b0 Missing posts 
\f0\b \
\ls2\ilvl2
\f1\b0 {\listtext	\uc0\u8259 	}
\f0\b Facebook: 
\f1\b0 Missing comment threads and care reacts. Additionally posts are not easily linked to their comments
\f0\b \
\ls2\ilvl2
\f1\b0 {\listtext	\uc0\u8259 	}
\f0\b Twitter: 
\f1\b0 Missing threads and views. Currently includes quotes as a substitute. However, all of these appear blank.\
\pard\tx220\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\li720\fi-720\pardirnatural\partightenfactor0
\ls2\ilvl0\cf0 {\listtext	2)	}Our data is also from various times, but should be fairly general thematically i.e Not leaning towards particular demographics\
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0
\cf0 \
\

\f0\b\fs48 DATA 
\f1\b0\fs24 \
\
The datasets used are:\
\
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\b\fs40 \cf0 \ul \ulc0 Twitter
\f1\b0\fs24 \ulnone \
\
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\b \cf0 Tweets from Jan 1st 2023:\
\pard\tx220\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\li720\fi-720\pardirnatural\partightenfactor0
\ls3\ilvl0
\f1\b0 \cf0 {\listtext	\uc0\u8226 	}Our dataset consists of randomly selected tweets from the millions of tweets that were posted on the 1st of Jan 2023. \
{\listtext	\uc0\u8226 	}Tweets were randomly selected at ~5 different intervals across the day\
{\listtext	\uc0\u8226 	}Future data updates may incorporate random samples of tweets from different months in the 2022-2023 period. The full dataset is not in the repository due to size restrictions\
{\listtext	\uc0\u8226 	}Unfortunately this set does not contain views per individual tweets. We will assess additional sources for this information. Additionally, lots of quotes, replies, reposts are all 0\
\pard\tx220\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\li720\fi-720\pardirnatural\partightenfactor0
\ls3\ilvl0
\f0\b \cf0 {\listtext	\uc0\u8226 	}Sourced from:
\f1\b0  https://archive.org/download/archiveteam-twitter-stream-2023-01\
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\b \cf0 \
\
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\fs40 \cf0 \ul \ulc0 Reddit
\f1\b0\fs24 \ulnone \
\
\
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\b \cf0 May 2015 Reddit Comments
\f1\b0 : \
\pard\tx220\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\li720\fi-720\pardirnatural\partightenfactor0
\ls4\ilvl0\cf0 {\listtext	\uc0\u8226 	}Consists of over ~50m comments taken from May 2015. Includes parent_Ids but does not include post types\
{\listtext	\uc0\u8226 	}No specific subreddits are chosen, and a subset of ~100,000 has been chosen as our dataset to sample from.\
{\listtext	\uc0\u8226 	}As with our twitter set, our dataset is too large to fully upload to the repository\
{\listtext	\uc0\u8226 	}Unfortunately, this set does not contain posts. We have struggled to find data that meets all requirements and is recent. We are working on fixing this\
\pard\tx220\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\li720\fi-720\pardirnatural\partightenfactor0
\ls4\ilvl0
\f0\b \cf0 {\listtext	\uc0\u8226 	}Sourced From: 
\f1\b0 https://www.kaggle.com/datasets/kaggle/reddit-comments-may-2015\
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\b\fs40 \cf0 \ul \ulc0 \
Facebook\

\fs24 \ulnone \

\f1\b0 2017 News Data:\
\pard\tx220\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\li720\fi-720\pardirnatural\partightenfactor0
\ls5\ilvl0\cf0 {\listtext	\uc0\u8226 	}Consists of ~20,000 posts from 83 pages, with approximately ~1m comments\
{\listtext	\uc0\u8226 	}Dataset is entirely news focused. We may seek to find more general content or posts to improve the diversity of our data\
{\listtext	\uc0\u8226 	}Our data does not include comments that are in threads, only referencing the post_id to which these comments are attached. Additionally, \'91care\'92 reacts are missing and all reacts are only applicable to posts. \
\ls5\ilvl0{\listtext	\uc0\u8226 	}Additionally, comments are not easily linked to posts\
{\listtext	\uc0\u8226 	}
\f0\b Sourced from
\f1\b0 : https://github.com/jbencina/facebook-news/blob/master/README.md\
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\b \cf0 \

\f1\b0 \
}