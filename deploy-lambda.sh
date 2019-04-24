#!/usr/bin/env bash

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ (-z "${suffix}") || (-z "${url}") ]]; then
    echo "Please set the 'suffix' and 'url' env vars"
    exit
fi
cd "$SCRIPT_DIR"/serverless/lambda/scrapper
url="${url}" suffix="${suffix}" SLS_DEBUG=* AWS_DEFAULT_REGION=eu-west-2 AWS_PROFILE=courseXgit remote add origin git@github.com:krimsz/python-workshop-aws-serverless.git sls deploy
cd "$SCRIPT_DIR"/serverless/lambda/insert_to_db_consumer
url="${url}" suffix="${suffix}" SLS_DEBUG=* AWS_DEFAULT_REGION=eu-west-2 AWS_PROFILE=courseX sls deploy
cd "$SCRIPT_DIR"/serverless/lambda/error_consumer
url="${url}" suffix="${suffix}" SLS_DEBUG=* AWS_DEFAULT_REGION=eu-west-2 AWS_PROFILE=courseX sls deploy
