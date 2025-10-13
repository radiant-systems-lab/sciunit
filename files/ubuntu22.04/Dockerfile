FROM ubuntu:22.04

RUN useradd -m -s /bin/bash testuser

RUN apt-get update

RUN apt install -y python3-dev python3-pip software-properties-common

RUN pip3 install --upgrade pip

WORKDIR /home/testuser/

USER root

ENV PATH="$PATH:~/.local/bin"

COPY ./test_sciunit.sh /home/testuser/test_sciunit.sh
RUN chmod +x ./test_sciunit.sh

USER testuser

RUN pip3 install --user sciunit2 --break-system-packages

CMD ["bash"]