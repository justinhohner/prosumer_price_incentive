FROM ubuntu:18.04

ENV GTEST /home/sam/sam_dev/googletest
ENV LKDIR /home/sam/sam_dev/lk
ENV WEXDIR /home/sam/sam_dev/wex
ENV SSCDIR /home/sam/sam_dev/ssc
ENV SAMNTDIR /home/sam/sam_dev/SAM
ENV RAPIDJSONDIR /home/sam/sam_dev/ssc
ENV PYSAMDIR /home/sam/sam_dev/pysam

RUN DEBIAN_FRONTEND=noninteractive apt-get update && \
    apt-get install -y \
    build-essential \
    freeglut3-dev \
    g++ \
    git \
    libcurl4-openssl-dev \
    libfontconfig-dev \
    libgl1-mesa-dev \
    libgtk2.0-dev \
    libjsoncpp-dev \
    mesa-common-dev \
    unzip \
    wget \
    rsync \
    python3-pip

RUN ln -s /usr/include/jsoncpp/json/ /usr/include/json

RUN mkdir -p /home/sam/sam_dev
WORKDIR /home/sam/sam_dev
COPY diffs/CMakeLists.txt /home/sam/sam_dev/CMakeLists.txt
COPY diffs/ssc-scaling.patch /home/sam/sam_dev/ssc-scaling.patch


#RUN wget https://cmake.org/files/v3.24/cmake-3.24.4-linux-x86_64.tar.gz -O /home/sam/cmake-3.24.4-linux-x86_64.tar.gz
#RUN tar -xzf /home/sam/cmake-3.24.4-linux-x86_64.tar.gz -C /home/sam/
#ENV PATH $PATH:/home/sam/cmake-3.24.4-linux-x86_64/bin/
#RUN ln -s /home/sam/cmake-3.24.4-linux-x86_64/bin/cmake /usr/bin/cmake
RUN pip3 install -U pip && pip3 install cmake && ln -s /opt/python/cp37-cp37m/bin/cmake /usr/bin/cmake

RUN wget -q https://github.com/wxWidgets/wxWidgets/releases/download/v3.2.0/wxWidgets-3.2.0.tar.bz2 -O /home/sam/wxWidgets-3.2.0.tar.bz2 && \
    tar jxf /home/sam/wxWidgets-3.2.0.tar.bz2 -C /home/sam/ && \
    cd /home/sam/wxWidgets-3.2.0 && \
    ./configure --prefix=/home/sam/wx-3.2.0 --enable-shared=no \
      --enable-stl=yes --enable-debug=no --with-gtk=2 --with-libjpeg=builtin \
      --with-libpng=builtin --with-regex=builtin --with-libtiff=builtin \
      --with-zlib=builtin --with-expat=builtin --without-libjbig \
      --without-liblzma --without-gtkprint --with-libnotify=no \
      --with-libmspack=no --with-gnomevfs=no --with-opengl=yes \
      --with-sdl=no --with-cxx=11 && \
    make -j2 all install && \
    ln -s /home/sam/wxWidgets-3.2.0/wx-config /usr/local/bin/wx-config-3

RUN git clone https://github.com/google/googletest.git && \
    cd ${GTEST} && git checkout b85864c64758dec007208e56af933fc3f52044ee -b build
RUN cd ${GTEST} && \
    mkdir ${GTEST}/build && \
    cd ${GTEST}/build && \
    cmake -DCMAKE_CXX_FLAGS=-std=c++11 .. && \
    cmake --build . -j4 && make install

RUN for repo in lk wex ssc SAM pysam ; do git clone https://github.com/nrel/$repo ; done

RUN cd ${SSCDIR} && git apply /home/sam/sam_dev/ssc-scaling.patch

RUN cd /home/sam/sam_dev && \
    mkdir build && \
    cd build && \
    cmake .. -DCMAKE_BUILD_TYPE=Release && \
    make -j4

RUN cd ${PYSAMDIR} && pip3 install numpy scipy pandas notebook matplotlib geopy imgkit
RUN cd ${PYSAMDIR} && python3 setup.py install
