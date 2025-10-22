FROM fedora:42

# Install pyenv dependecies
RUN dnf update -y && \
    dnf install -y git gcc make zlib-devel bzip2-devel readline-devel \
                   sqlite-devel openssl-devel tk-devel libffi-devel xz-devel \
                   findutils && \
    dnf clean all && rm -rf /var/cache/dnf

# Install pyenv and Python 3.12.7 since Python13 removed pipes module
ENV PYENV_ROOT="/root/.pyenv"
ENV PATH="$PYENV_ROOT/bin:$PYENV_ROOT/shims:$PATH"
RUN git clone https://github.com/pyenv/pyenv.git $PYENV_ROOT && \
    pyenv install 3.12.7 && \
    pyenv global 3.12.7

# Install sciunit
RUN python3 -m pip install --upgrade pip && \
    python3 -m pip install sciunit2

# Copy test script
COPY files/utility/test_sciunit.sh /test_sciunit.sh
RUN chmod +x /test_sciunit.sh

CMD ["bash"]
