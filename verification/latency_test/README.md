# Ranker latency test

A test to ensure that the ranker is running and returning requests at a reasonable speed. The limit that we are requesting of participants is a latency of 500ms at p95. 

## What is this testing for?

### Latency 
Our goal is to ensure that the ranker can handle a realistic data set at a reasonable rate--this test is designed to send requests from all three platforms, and should take around 5 minutes to run. The threshold we are testing for is 500 ms p95.

### Validity
The test also checks that the output for each request is valid and json-parsable. 

## Running the test

You can run this test on a ranking endpoint using the following command: 

```
python latency_testing.py <url>
```

Replace "<url>" above with the location of your application--feel free to also try this out with any of the code examples in the repo! 

Note: This repo also contains a sample dataset for each platform for public testing purposes, but the rankers will be tested on a separate dataset internally. The internal dataset will be similar in composition and size to the public version, so if the ranker is passing with this repo's version, you should be in the clear! 
