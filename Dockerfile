FROM pandoc/core:2.19.2.0

RUN apk add python3
RUN pip3 install --upgrade pip
RUN pip3 install requests

COPY wiki_to_adoc.py /usr/local/bin/wiki_to_adoc
WORKDIR /data
ENTRYPOINT ["wiki_to_adoc"]
