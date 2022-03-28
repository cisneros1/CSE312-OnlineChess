# syntax=docker/dockerfile:1
FROM python:3.8-slim-buster

ENV HOME /root
WORKDIR /root

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
RUN pip install requests
RUN python3 -m pip install pymongo[srv]
COPY . .

EXPOSE 8000

ADD https://github.com/ufoscout/docker-compose-wait/releases/download/2.2.1/wait /wait
RUN chmod +x /wait

CMD /wait && python3 server.py