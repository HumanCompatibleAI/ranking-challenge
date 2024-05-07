#!/usr/bin/env bash

export PROJECT_ROOT=$(git rev-parse --show-toplevel)
export TEST_POSTS_DB=sample_posts_test.db
export POSTS_DB_PATH=${PROJECT_ROOT}/sample_data/${TEST_POSTS_DB}
cd ${PROJECT_ROOT}/sample_data
python seed_post_db.py --no-user-pool --dbname=${TEST_POSTS_DB}
python -m nltk.downloader maxent_ne_chunker words punkt averaged_perceptron_tagger
cd ${PROJECT_ROOT}/examples/worker_sqlite_redis
make test
rm ${POSTS_DB_PATH}
