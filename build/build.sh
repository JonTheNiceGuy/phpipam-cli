#!/bin/bash
set -euo pipefail

REPO="ghcr.io/jontheniceguy/phpipam-cli"
TAG="${1:-latest}"
datetime=$(date +%Y%m%d%H%M)

echo "Building ${REPO}:${TAG} and ${REPO}:${datetime}"

docker build -t "${REPO}:${TAG}" -t "${REPO}:${datetime}" .

echo "Pushing ${REPO}:${TAG}"
docker push "${REPO}:${TAG}"

echo "Pushing ${REPO}:${datetime}"
docker push "${REPO}:${datetime}"

echo "Done"
