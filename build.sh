docker buildx build --platform linux/amd64 -t sam-base -f Dockerfile.base .
docker buildx build --platform linux/amd64 -t sam-scaled -f Dockerfile.scaled .
docker buildx build --platform linux/amd64 -t sam-unscaled -f Dockerfile.unscaled .
