# Base Arch Linux image
FROM archlinux:base

# Prevent interactive prompts
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=


# Install system dependencies required for pyenv + Python build
RUN pacman -Syu --noconfirm && \
    pacman -S --noconfirm \
    git base-devel openssl zlib xz tk bzip2 libffi readline sqlite gdbm ncurses \
    libnsl libtirpc ca-certificates && \
    pacman -Scc --noconfirm

# Install pyenvn and Python 3.12
ENV PYENV_ROOT="/root/.pyenv"
ENV PATH="$PYENV_ROOT/bin:$PYENV_ROOT/shims:$PATH"
RUN git clone https://github.com/pyenv/pyenv.git $PYENV_ROOT && \
    pyenv install 3.12.7 && \
    pyenv global 3.12.7 && \
    echo 'eval "$(pyenv init -)"' >> ~/.bashrc


# Upgrade pip and install sciunit
RUN pip3 install --upgrade pip && \
    pip3 install sciunit2 --break-system-packages

# Copy test script
COPY files/utility/test_sciunit.sh /test_sciunit.sh
RUN chmod +x /test_sciunit.sh

CMD ["bash"]
