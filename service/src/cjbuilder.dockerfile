FROM ubuntu:bionic

ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.8-venv python3-pip python3.8-dev build-essential \
    binutils-multiarch nasm curl python automake flex bison vim-tiny strace \
    supervisor gnupg git wget netbase software-properties-common libtool-bin \
    glib2.0-dev

RUN apt-get install -y aria2 curl wget virtualenvwrapper && \
    /bin/bash -c "$(curl -sL https://git.io/vokNn) " && \
    apt-fast update && apt-fast -y upgrade && apt-fast update

# install all the ubuntu packages that we need
RUN apt-fast install -y unzip python-lzma git sudo make emacs vim iputils-ping \
              python3-crypto libqt4-opengl python3-opengl python3-pyqt4 python3-pyqt4.qtopengl python3-numpy python3-scipy   \
              mtd-utils gzip bzip2 tar arj lhasa p7zip p7zip-full cabextract cramfsswap squashfs-tools sleuthkit default-jdk \
              lzop srecord zlib1g-dev liblzma-dev liblzo2-dev \
              qemu-system libepoxy-dev libgbm-dev libgtk-3-dev \
              busybox-static bash-static fakeroot dmsetup kpartx netcat-openbsd nmap python3-psycopg2 snmp uml-utilities util-linux vlan \
              libpq-dev qemu-system-arm qemu-system-mips qemu-system-x86 qemu-utils \
              rsync socat busybox-static fakeroot git dmsetup kpartx netcat-openbsd nmap \
              python-psycopg2 python3-psycopg2 snmp uml-utilities util-linux vlan \
              supervisor postgresql python3-bs4 sudo iproute2 uml-utilities kpartx \
              libepoxy-dev libgbm-dev libgtk-3-dev libcurl4-nss-dev bc seabios vgabios rlwrap net-tools \
              build-essential patch ruby-bundler ruby-dev zlib1g-dev liblzma-dev \
              git autoconf build-essential libpcap-dev libpq-dev libsqlite3-dev \
              postgresql postgresql-contrib postgresql-client \
              ruby python dialog apt-utils nmap nasm  netcat tcpdump binwalk \
              libbrlapi-dev libpulse-dev libnuma-dev \
              afl netcat sudo iproute2 uml-utilities kpartx \
              libepoxy-dev libgbm-dev libgtk-3-dev libcurl4-nss-dev libbrlapi-dev libpulse-dev libnuma-dev \
              musl-tools cmake iptables socat net-tools iputils-ping nmap tcpdump

RUN apt update

RUN python3.8 -m venv /root/venv
RUN bash -c "source /root/venv/bin/activate && \
    pip install -U pip setuptools wheel keystone-engine>=0.9.2"

# Install all the python packages that we need
RUN bash -c "source /root/venv/bin/activate && \
    pip install ipython ipdb scapy jinja2 pyyaml bs4 nose coverage pyqtgraph capstone>=3.0.5rc2 cstruct python-magic selenium bs4 \
    progressbar cffi>=1.0.3 pefile sortedcontainers>=2.0 future requests paramiko pysnmp pycryptodome pygdbmi docker nclib>=1.0.0rc3 \
    patchelf-wrapper z3-solver>=4.8.5.0 cachetools decorator pysmt pycparser>=2.18 bitstring tqdm dpkt mulpyplexer networkx>=2.0 \
    progressbar2 rpyc GitPython psutil itanium_demangler CppHeaderParser timeout-decorator subprocess32 python-resources pyelftools \
    termcolor sqlalchemy marshmallow-sqlalchemy psycopg2-binary protobuf>=3.12.0 tabulate"

RUN dpkg --add-architecture i386 && apt-get update

ENV DEBIAN_FRONTEND noninteractive

# Install apt-fast to speed things up
RUN apt-get install -y aria2 curl wget virtualenvwrapper && \
    /bin/bash -c "$(curl -sL https://git.io/vokNn) " && \
    apt-fast update && apt-fast -y upgrade && apt-fast update

# Install all APT packages

RUN apt-fast install -y git build-essential  binutils-multiarch nasm \
                        #Libraries
                        libxml2-dev libxslt1-dev libffi-dev cmake libreadline-dev \
                        libtool debootstrap debian-archive-keyring libglib2.0-dev libpixman-1-dev \
                        libssl-dev qtdeclarative5-dev libcapnp-dev libtool-bin \
                        libcurl4-nss-dev libpng-dev libgmp-dev \
                        # x86 Libraries
                        libc6:i386 libgcc1:i386 libstdc++6:i386 libtinfo5:i386 zlib1g:i386 \
                        #Utils
                        sudo automake ccache make g++-multilib pkg-config coreutils \
                        ninja-build capnproto  software-properties-common zip unzip  \
                        libxss1 bison flex \
                        # utils
                        emacs
RUN apt-fast update

RUN apt-fast install -y  gcc-arm-linux-gnueabi g++-arm-linux-gnueabi  \
                         gcc-mipsel-linux-gnu g++-mipsel-linux-gnu \
                         gcc-mips-linux-gnu g++-mips-linux-gnu \
                         binutils-multiarch \
                         gawk texinfo cvs ncurses-dev help2man rsync


RUN sudo apt-fast install -y autoconf automake autotools-dev curl python3 libmpc-dev libmpfr-dev libgmp-dev gawk build-essential bison flex texinfo gperf libtool patchutils bc zlib1g-dev libexpat-dev

RUN cd /root; git clone https://github.com/riscv/riscv-gnu-toolchain ; cd riscv-gnu-toolchain; \
    ./configure --prefix=/opt/riscv --with-arch=rv32gc --with-abi=ilp32d && make -j$(nproc) linux && make install

RUN export TARGET=sparc-unknown-linux-gnu && export PREFIX="/opt/sparc" && export PATH="$PREFIX/bin:$PATH" && \
    cd /root; BINUTILS_VERSION=2.29.1; wget ftp://ftp.gnu.org/gnu/binutils/binutils-$BINUTILS_VERSION.tar.gz && \
    tar -xvzf binutils-$BINUTILS_VERSION.tar.gz; cd binutils-$BINUTILS_VERSION && \
    ./configure --target=$TARGET --prefix=$PREFIX --with-sysroot --disable-nls --disable-werror && \
    make -j$(nproc) && make install

RUN export TARGET=sparc-unknown-linux-gnu && export PREFIX="/opt/sparc" && export PATH="$PREFIX/bin:$PATH" && \
    export PATH=$PATH:/opt/sparc/bin && \
    cd /root && GCC_VERSION=7.2.0; wget ftp://ftp.gnu.org/gnu/gcc/gcc-$GCC_VERSION/gcc-$GCC_VERSION.tar.gz && \
    tar -xvzf gcc-$GCC_VERSION.tar.gz && cd gcc-$GCC_VERSION && ./contrib/download_prerequisites && \
    ./configure --target=$TARGET --prefix=$PREFIX --enable-languages=c,c++ --without-headers --disable-nls \
                --disable-shared --disable-decimal-float --disable-threads --disable-libmudflap --disable-libssp \
                --disable-libgomp --disable-libquadmath --disable-libatomic --disable-libmpx --disable-libcc1 && \
    make -j$(nproc) all-gcc && make install-gcc

RUN cd /root && git clone -q https://github.com/etrickel/docker_env.git && cp -r /root/docker_env/. . && \
    echo "export PATH=$PATH:/opt/sparc/bin:/opt/riscv/bin" >> /root/.bashrc && \
    echo "source /root/venv/bin/activate " >> /root/.bashrc

RUN bash -c "source /root/venv/bin/activate && \
             pip install ipython  "

COPY qemooo /root/qemooo

RUN cd /root/qemooo && rm -rf build-user && mkdir -p build-user && cd build-user && \
    ../configure --disable-system  --enable-linux-user --static \
                 --target-list=arm-linux-user,i386-linux-user,mipsel-linux-user,riscv32-linux-user,sparc32plus-linux-user \
                 --enable-debug --disable-werror --enable-debug-info --enable-debug-tcg --enable-trace-backends=simple

RUN cd /root/qemooo/build-user && ../qemooo-build.sh


RUN mkdir -p /tiamat/service/src/chal_builder/
COPY chal_builder /tiamat/service/src/chal_builder

WORKDIR /tiamat/service/src/chal_builder/
RUN bash -c "source /root/venv/bin/activate && \
             pip install -e . "



