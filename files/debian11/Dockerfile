FROM debian:bullseye

RUN apt-get update

# Install pyenv requirements
RUN apt update && apt install -y build-essential libssl-dev zlib1g-dev libbz2-dev \
libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev \
xz-utils tk-dev libffi-dev liblzma-dev python3-openssl git

# Install pyenv and Python 3.12.7 since Python13 removed pipes module
ENV PYENV_ROOT="/root/.pyenv"
ENV PATH="$PYENV_ROOT/bin:$PYENV_ROOT/shims:$PATH"
RUN git clone https://github.com/pyenv/pyenv.git $PYENV_ROOT && \
    pyenv install 3.12.7 && \
    pyenv global 3.12.7



ENV PATH="$PATH:~/.local/bin"

COPY ./test_sciunit.sh /test_sciunit.sh
RUN chmod +x ./test_sciunit.sh

RUN pip3 install --user sciunit2 --break-system-packages


CMD ["bash"]