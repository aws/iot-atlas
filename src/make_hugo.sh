#!/bin/bash
# This script is used for both local testing and automated build process (CodeBuild)
set -e

# Local name of docker image to build and use
export IMAGE_NAME=temporary/hugo-ubuntu:latest

function usage {
    cat <<HELP_USAGE
    usage: $0 [-hd] [-s bucket]
    -d --develop      Run Hugo in interactive development mode
                      (asciidoc images will show broken)
    -s --sync=bucket  S3 bucket name to sync generate content
    -v --validate     Run validation on content
    -h --help         display help
HELP_USAGE
}

function hugo_build {
    echo "********** Building site content"

    # Empty public folder completely
    shopt -s dotglob
    rm -rf hugo/public/*
    shopt -u dotglob

    # Create local docker images for Hugo build and testing process
    if ! [[ $(docker images -q $IMAGE_NAME) ]]; then
        docker build -t $IMAGE_NAME --file Dockerfile-build .
    fi

    # Generate full content
    docker run --rm -v $PWD/hugo:/hugo-project $IMAGE_NAME hugo
}

function hugo_validate {
    echo "********** Validating content"
    # Test HTML local and external links
    # Start hugo locally, reference //host.docker.internal for other containers to use
    docker run -d --name hugo_checker --rm -p 1313:1313 -v $PWD/hugo:/hugo-project temporary/hugo-ubuntu:latest hugo server --bind 0.0.0.0 -b http://localhost:1313/ 1>/dev/null

    # Wait until the web server is up
    while [ "`docker inspect -f {{.State.Health.Status}} hugo_checker`" != "healthy" ]; do sleep 0.5; done

    # Check all links
    # unset shell exit to stop the container above before exiting
    set +e
    # Run for every translated language
    if ! uri_path_validate "en" || 
       ! uri_path_validate "zh" ||
       ! uri_path_validate "fr"; then
        echo "********** Validation errors, stopping local Hugo instance"
        docker stop hugo_checker 1>/dev/null
        echo "Link checks failed, exiting"
        exit 1
    fi
    set -e
    echo "********** Validation completed successfully, stopping local Hugo instance"
    docker stop hugo_checker 1>/dev/null
}

function uri_path_validate {
    # Run link checker for specific URI
    # Note - run the container on the host network to access Hugo running in a separate container
    #      - Exclude on github.com/aws in case of editURL changes. Will catch during automation   
    echo "********** Running link checks on language: $1"
    if ! docker run --net="host" raviqqe/muffet \
            "--exclude=https://github.com/aws/" \
            http://localhost:1313/$1/; then
        return 1   # 1 = failure
    fi
}

function sync_s3 {
    echo "********** Synching content to S3 bucket: $BUCKET"
    aws s3 rm s3://$BUCKET --recursive
    aws s3 sync hugo/public s3://$BUCKET
}

function hugo_develop {
    echo "********** Starting Hugo for local development"
    if ! [[ $(docker images -q $IMAGE_NAME) ]]; then
        docker build -t $IMAGE_NAME .
    fi
    docker run --rm -p 1313:1313 -v $PWD/hugo:/hugo-project $IMAGE_NAME
    exit 0
}

# Process arguments

for i in "$@"
do
case $i in
    -d|--develop)
    hugo_develop
    # Function exits - when in develop, not other tasks
    ;;
    -s=*|--sync=*)
    BUCKET="${i#*=}"
    shift # past arg=param
    ;;
    -v|--validate)
    VALIDATE=YES
    shift
    ;;
    -h|--help)
    usage
    exit
    ;;
    *)
    usage
    exit 1
    ;;
esac
done

# Build and optionally validate and sync
hugo_build

if [[ $VALIDATE ]]; then
    hugo_validate
fi

if [[ $BUCKET ]]; then
    sync_s3
fi



