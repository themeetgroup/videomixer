FROM videomixer-base:latest
MAINTAINER Misha Nasledov <misha@themeetgroup.com>

ADD . /videomixer

RUN cd /videomixer && \
    pip3 install -r requirements.txt

CMD ["/videomixer/mix.py"]
