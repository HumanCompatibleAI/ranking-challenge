#!/usr/bin/env bash

# Postgres connection setup. This will depend on your specific port mappings
# and other settings.
PGHOST=localhost
PGPORT=5435

PGDB_PYTEST_TESTS=posts_test_db
PGDB_SAMPLE_DATA=posts

POSTS_DB_URI_PYTEST_TESTS=postgresql://postgres:postgres@${PGHOST}:${PGPORT}/${PGDB_PYTEST_TESTS}
export POSTS_DB_URI=postgresql://postgres:postgres@${PGHOST}:${PGPORT}/${PGDB_SAMPLE_DATA}


export PROJECT_ROOT=$(git rev-parse --show-toplevel)


# Check if 'poetry.lock' exists and 'poetry install' needs to run

if [ ! -f "${PROJECT_ROOT}/poetry.lock" ]; then
    echo "The Poetry environment is not set up. Please run 'poetry install' first."
    exit 1
fi

# Setup data for tests

cd "${PROJECT_ROOT}/sample_data" || exit 1

export TEST_POSTS_DB=test_posts.db

if [ -f "$TEST_POSTS_DB" ]; then
    : # echo "File is already unzipped."
elif [ -f "${TEST_POSTS_DB}.gz" ]; then
    gunzip -k "${TEST_POSTS_DB}.gz"
else
    echo "Error: File $TEST_POSTS_DB does not exist."
    exit 1
fi

POSTS_DB_URI=${POSTS_DB_URI_PYTEST_TESTS} poetry run python seed_post_db.py --dbname ${TEST_POSTS_DB} --seed-postgres

# Setup sample posts database
# This simulates a pool of 500 users with varying activity levels.

poetry run python seed_post_db.py --n-users=500 --activity-distribution=0.2:20,1:65,5:15
