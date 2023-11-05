#!/bin/bash
docker run -it --platform linux/amd64 \
    -v $(pwd):/code \
    -p 8888:8888 \
    -e "NREL_API_KEY=O5AIe0goSZaAEgixAw0zMAmtSEX1TXSQMu1hONwx" \
    -e "NREL_API_EMAIL=jhn37@umsystem.edu" \
    --name sam-unscaled \
    sam-unscaled \
    bash

