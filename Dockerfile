FROM debian:sid
MAINTAINER Misha Nasledov <misha@themeetgroup.com>

# Note this requires GStreamer 1.0 and for the Python 3 gi (GObject Introspection) library to match versions.
# Unfortunately this installs a lot of stuff. Try not to change this step :)
# TODO: Make a base image.
RUN apt-get update && \
    apt-get install -y python3 python3-gi python3-pip gstreamer1.0-plugins-good gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly gstreamer1.0-libav gir1.2-gstreamer-1.0 && \
    apt-get clean

ADD . /videomixer

RUN cd /videomixer && \
    pip3 install -r requirements.txt

CMD ["/videomixer/mix.py"]
