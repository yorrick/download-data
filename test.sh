#!/usr/bin/env bash

echo "toto"

if [ ! -z "$TRAVIS_TAG" ]; 
then echo "$DOCKER_IMAGE_NAME:latest $DOCKER_IMAGE_NAME:$TRAVIS_TAG"; 
else echo "$TRAVIS_BRANCH-latest" ;
fi

