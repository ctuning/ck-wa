FROM ubuntu:16.04
MAINTAINER Grigori Fursin <Grigori.Fursin@cTuning.org>
MAINTAINER Anton Lokhmotov <anton@dividiti.com>

# Install standard packages.
RUN apt-get update && apt-get install -y \
    python-all \
    python-pip \
    git \
    bzip2 \
    sudo \ 
    wget \
    zip \
    libjpeg8 libjpeg62-dev libfreetype6 libfreetype6-dev python-pillow

# Install Android SDK
RUN cd /opt ; \
    wget https://dl.google.com/android/android-sdk_r24.4.1-linux.tgz ; \
    gzip -d android-sdk_r24.4.1-linux.tgz ; \
    tar xvf android-sdk_r24.4.1-linux.tar ; \
    rm android-sdk_r24.4.1-linux.tar

# Set Android HOME
ENV ANDROID_HOME=/opt/Android/sdk

#    adb \
#    android-sdk-platform-tools \
#    android-sdk 

# Install the core Collective Knowledge (CK) module.
ENV CK_ROOT=/root/ck-master \
    CK_REPOS=/root/CK \
    CK_TOOLS=/root/CK-TOOLS \
    PATH=${CK_ROOT}/bin:${PATH}

RUN mkdir -p ${CK_ROOT} ${CK_REPOS} ${CK_TOOLS}
RUN git clone https://github.com/ctuning/ck.git ${CK_ROOT}
RUN cd ${CK_ROOT} && python setup.py install && python -c "import ck.kernel as ck"

# Install other CK modules.
RUN ck pull repo:ck-web

# Add CK-WA (and automatically unzip)
#ADD ck-wa.tar.bz2 ${CK_REPOS}
#RUN cd ${CK_REPOS}/ck-wa ; ck import repo --quiet

# Install WA via CK
#RUN ck install package:arm-wa-github

#Create and copy some existing keys (without pass)
# to allow access from this Docker client 
# to any given Android device

RUN mkdir -m 0750 /root/.android
ADD adbkey.pub /root/.android/adbkey.pub
ADD adbkey /root/.android/adbkey

# Check ADB
#CMD adb shell

# Check WA
#CMD ck run wa:dhrystone
#CMD which wa ; wa --help ; wa run dhrystone
CMD bash

# Set the CK web service defaults.
#ENV CK_PORT=3344 \
#    WFE_PORT=3344 

# Expose CK port
#EXPOSE ${CK_PORT}

# Start the CK web service.
# Note, that container will have it's own IP,
# that's why we need `hostname -i` below
#CMD export CK_LOCAL_HOST=`hostname -i` ; \
#    if [ "${CK_HOST}" = "" ]; then export CK_HOST=$CK_LOCAL_HOST ; fi ; \
#    if [ "${WFE_HOST}" = "" ]; then export WFE_HOST=$CK_LOCAL_HOST ; fi ; \
#    ck start web \
#    --host=${CK_HOST} --port=${CK_PORT} \
#    --wfe_host=${WFE_HOST} --wfe_port=${WFE_PORT}
