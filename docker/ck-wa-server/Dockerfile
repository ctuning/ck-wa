FROM ubuntu:16.04
MAINTAINER Grigori Fursin <Grigori.Fursin@cTuning.org>
MAINTAINER Anton Lokhmotov <anton@dividiti.com>

# Install min standard packages.
RUN apt-get update && apt-get install -y \
    git bzip2 sudo wget zip

# Install Android SDK
RUN cd /opt ; \
    wget https://dl.google.com/android/android-sdk_r24.4.1-linux.tgz ; \
    gzip -d android-sdk_r24.4.1-linux.tgz ; \
    tar xvf android-sdk_r24.4.1-linux.tar ; \
    rm android-sdk_r24.4.1-linux.tar

# Install standard packages.
RUN apt-get install -y \
    python-all \
    python-pip \
    default-jre \
    libjpeg8 libjpeg62-dev libfreetype6 libfreetype6-dev python-pillow

# Install the core Collective Knowledge (CK) module.
ENV CK_ROOT=/root/ck-master \
    CK_REPOS=/root/CK \
    CK_TOOLS=/root/CK-TOOLS

ENV ANDROID_HOME=/opt/android-sdk-linux

ENV PATH=${CK_ROOT}/bin:${ANDROID_HOME}/tools:${ANDROID_HOME}/platform-tools:${PATH}

RUN mkdir -p ${CK_ROOT} ${CK_REPOS} ${CK_TOOLS}
RUN git clone https://github.com/ctuning/ck.git ${CK_ROOT}
RUN cd ${CK_ROOT} && python setup.py install && python -c "import ck.kernel as ck"

# Install other CK modules.
RUN ck pull repo:ck-web

# Update Android SDK (extra deps) - need expect to automate license acceptance
#RUN android list sdk --extended --all
#RUN android list sdk --extended
RUN apt-get install -y expect

COPY update_android.sh /usr/bin/update_android.sh

RUN chmod 755 /usr/bin/update_android.sh
RUN /usr/bin/update_android.sh

# Install Android NDK
RUN cd /opt ; wget http://dl.google.com/android/repository/android-ndk-r11c-linux-x86_64.zip
RUN cd /opt ; unzip android-ndk-r11c-linux-x86_64.zip

# Add CK-WA (and automatically unzip)
RUN cd ${CK_REPOS} ; mkdir -p ck-wa ;
COPY ckr-ck-wa.zip ${CK_REPOS}/ck-wa/ckr-ck-wa.zip
RUN cd ${CK_REPOS}/ck-wa ; unzip ckr-ck-wa.zip ; rm ckr-ck-wa.zip ; ck import repo --quiet

# Install WA via CK
RUN ck install package:arm-wa-github

#Create and copy some existing keys (without pass)
# to allow access from this Docker client 
# to any given Android device
#RUN mkdir -m 0750 /root/.android
COPY adbkey.pub /root/.android/adbkey.pub
COPY adbkey /root/.android/adbkey

# interactive, if needed to debug
#CMD bash

# Check ADB
CMD adb devices

# Check WA
#CMD wa --help ; ck run wa:dhrystone --out=json

# Set the CK web service defaults.
ENV CK_PORT=3344 \
    WFE_PORT=3344 

# Expose CK port
EXPOSE ${CK_PORT}

# Start the CK web service.
# Note, that container will have it's own IP,
# that's why we need `hostname -i` below
CMD export CK_LOCAL_HOST=`hostname -i` ; \
    if [ "${CK_HOST}" = "" ]; then export CK_HOST=$CK_LOCAL_HOST ; fi ; \
    if [ "${WFE_HOST}" = "" ]; then export WFE_HOST=$CK_LOCAL_HOST ; fi ; \
    ck start web \
    --host=${CK_HOST} --port=${CK_PORT} \
    --wfe_host=${WFE_HOST} --wfe_port=${WFE_PORT}
