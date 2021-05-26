
FROM docker.io/library/python:3

LABEL org.opencontainers.image.source="https://github.com/ctron/mitemp-gateway"

RUN pip install pybluez
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY bluetooth_utils.py /
COPY main.py /

CMD [ "python", "main.py" ]
