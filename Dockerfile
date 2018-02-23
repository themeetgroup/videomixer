FROM dockerregistry.tagged.com/video/videomixer:1.0
MAINTAINER Misha Nasledov <misha@themeetgroup.com>

ADD . /videomixer

RUN cd /videomixer && \
    pip3 install -r requirements.txt

CMD ["/videomixer/mix.py"]
