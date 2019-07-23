FROM debian:jessie

ENV DEBIAN_FRONTEND noninteractive
ENV PATH $PATH:/usr/local/nginx/sbin

# create directories
RUN mkdir /src \
    && mkdir /logs

# curl is used for grabbing tarballs and other things.
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y --force-yes build-essential libpcre3-dev zlib1g-dev libssl-dev curl  \
    && apt-get clean -y

# get nginx source, compile, and cleanup.
RUN cd /src \
    && curl -sL http://nginx.org/download/nginx-1.9.11.tar.gz -o nginx-1.9.11.tar.gz \
    && tar zxf nginx-1.9.11.tar.gz \
    && rm nginx-1.9.11.tar.gz \
    && curl -sL https://github.com/arut/nginx-rtmp-module/archive/v1.1.10.tar.gz -o v1.1.10.tar.gz \
    && tar zxf v1.1.10.tar.gz \
    && rm v1.1.10.tar.gz \
    && cd /src/nginx-1.9.11 \
    && ./configure --add-module=/src/nginx-rtmp-module-1.1.10 \
       --error-log-path=/logs/error.log \
       --http-log-path=/logs/access.log \
    && make \
    && make install \
    && mkdir -p /usr/local/nginx/xsl/ \
    && cp /src/nginx-rtmp-module-1.1.10/stat.xsl  /usr/local/nginx/xsl/ \
    && rm -rf /src

ADD nginx.conf /usr/local/nginx/

CMD ["nginx", "-c", "/usr/local/nginx/nginx.conf"]
