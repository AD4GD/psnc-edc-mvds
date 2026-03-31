#!/usr/bin/env bash
set -euo pipefail

# image version
DOCKER_REPO="psncedcmvds" # username on DuckerHub

# DockerHub login
echo "${DOCKERHUB_PASS}" | docker login -u "${DOCKERHUB_USER}" --password-stdin

# Images to push
IMAGES=(
  "connector"
  "identity-hub"
  "consumer-backend"
  "data-dashboard"
  "federated-catalog"
  "identity-provider"
)

# Version tag
TAG=$(curl -s "https://gitlab.pcss.pl/api/v4/projects/daisd-public%2Fdpi-pipelines%2Fpsnc-edc-mvds%2Fpsnc-edc-mvds/repository/tags" \
  | jq -r '.[].name' \
  | sed 's/^v//' \
  | sort -V \
  | tail -n1 )

echo "Latest tag: ${TAG}"

# Private registry prefix
SRC_PREFIX="${CI_REGISTRY_DOMAIN}/demeter/edc-connector"

for IMG in "${IMAGES[@]}"; do
  SRC_IMAGE="${SRC_PREFIX}/${IMG}:${CI_IMAGE_TAG}"
  LATEST_TAG_IMAGE="${DOCKER_REPO}/${IMG}:${TAG}"
  DEFAULT_IMAGE="${DOCKER_REPO}/${IMG}:latest"

  echo "==> Tagging: ${SRC_IMAGE} as ${DEFAULT_IMAGE} and ${LATEST_TAG_IMAGE}"
  docker tag "${SRC_IMAGE}" "${LATEST_TAG_IMAGE}"
  docker tag "${SRC_IMAGE}" "${DEFAULT_IMAGE}"

  echo "==> Sending ${DEFAULT_IMAGE} and ${LATEST_TAG_IMAGE} to DockerHub..."
  docker push "${LATEST_TAG_IMAGE}"
  docker push "${DEFAULT_IMAGE}"
done

echo "All sent to DockerHub."