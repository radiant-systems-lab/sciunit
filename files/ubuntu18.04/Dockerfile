FROM ubuntu:18.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update

RUN apt-get install -y cmake \
    software-properties-common \
    python3.7 \
    python3-pip \
    git

RUN pip3 install --upgrade pip

RUN useradd -m -s /bin/bash testuser

WORKDIR /home/testuser/

USER root

ENV PATH="$PATH:~/.local/bin"

COPY ./test_sciunit.sh /home/testuser/test_sciunit.sh
RUN chmod +x ./test_sciunit.sh

USER testuser

RUN pip3 install --user sciunit2

CMD ["bash"]
