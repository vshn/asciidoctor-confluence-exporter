FROM docker.io/pandoc/core:3.5.0.0

ENV PYTHONUNBUFFERED=1
RUN apk add python3
RUN python3 -m ensurepip
RUN pip3 install --upgrade pip
RUN pip3 install requests

RUN addgroup -S appgroup && adduser -S appuser -G appgroup
USER appuser

COPY --chown=appuser wiki_to_adoc.py /home/appuser/wiki_to_adoc
WORKDIR /home/appuser/data
ENTRYPOINT ["/home/appuser/wiki_to_adoc"]
