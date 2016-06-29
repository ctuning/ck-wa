#! /bin/bash

#
# Installation script for CK packages.
#
# See CK LICENSE for licensing details.
# See CK Copyright for copyright details.
#
# Developer(s): Grigori Fursin, 2016
#

# PACKAGE_DIR
# INSTALL_DIR

echo ""
echo "Cloning ARM Workload Automation from GitHub ..."

git clone ${WA_URL} ${INSTALL_DIR}/src
#git clone git@github.com:ARM-software/workload-automation.git ${INSTALL_DIR}/src

echo ""
echo "Checking python version (environment is set by CK):"
which python
python --version

echo ""
echo "Installing (with sudo) ..."
cd ${INSTALL_DIR}/src
#sudo -H pip install . --upgrade
sudo python setup.py install

 if [ "${?}" != "0" ] ; then
  echo "Error: Installation failed in $PWD!" 
  exit 1
 fi

exit 0
