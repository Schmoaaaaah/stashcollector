FROM ghcr.io/marcopeocchi/yt-dlp-vue:main

RUN mkdir -p /app
RUN mkdir -p /temp
RUN mkdir -p /media
RUN apk add --no-cache ffmpeg python3 py3-pip
WORKDIR /bin

RUN /usr/src/yt-dlp-rpc/fetch-yt-dlp.sh

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

COPY ./downloader.py /app/downloader.py
COPY ./main.py /app/main.py
COPY ./test.py /app/test.py


EXPOSE 5000


CMD ["python3", "test.py"]