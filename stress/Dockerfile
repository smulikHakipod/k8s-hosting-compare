FROM ghcr.io/colinianking/stress-ng:10d6a0e7007080bf2d5f2bf7759f2b73c407ee86

COPY ./requirements.txt /app/requirements.txt

RUN apk add --no-cache python3 py3-pip bash

RUN pip3 install -r /app/requirements.txt

COPY ./stress-cpu.py /app/stress-cpu.py

ENTRYPOINT ["/app/stress-cpu.py"]
