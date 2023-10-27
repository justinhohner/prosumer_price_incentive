#!/bin/bash
docker run -it --platform linux/amd64 \
    -v $(pwd):/code \
    -p 8888:8888 \
    --name sam-unscaled \
    sam-unscaled \
    bash

