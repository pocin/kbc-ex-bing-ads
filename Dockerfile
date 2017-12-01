FROM alpine:3.6

MAINTAINER Robin robin@keboola.com
RUN apk add --no-cache python3 git && \
    python3 -m ensurepip && \
    rm -r /usr/lib/python*/ensurepip && \
    pip3 install --upgrade pip setuptools && \
    if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi && \
    rm -r /root/.cache

RUN pip install --no-cache-dir --ignore-installed \
		pytest==3.2.3\
		requests==2.18.4\
    bingads==11.5.6\
    pytest-cov==2.5.1\
    && pip install --upgrade --no-cache-dir --ignore-installed git+git://github.com/keboola/python-docker-application.git@2.0.0

RUN mkdir -p /data/out/tables /data/in/tables
COPY . /src/
WORKDIR /src
CMD python3 -u /src/main.py
