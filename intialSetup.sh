#!/bin/bash

# Check if the current user's ID is 0 (root)
if [ "$EUID" -ne 0 ]; then
  echo "This script must be run as root."
  exit 1
else
  echo "This script is running as root."
fi

groupadd finance
groupadd sales
groupadd admin
groupadd security
groupadd sysadmin

mkdir /storage
mkdir /storage/finance
mkdir /storage/sales
mkdir /storage/admin
mkdir /storage/security
mkdir /storage/sysadmin

chgrp finance /storage/finance
chgrp sales /storage/sales
chgrp admin /storage/admin
chgrp security /storage/security
chgrp sysadmin /storage/sysadmin

chmod 770 /storage/finance
chmod 770 /storage/sales
chmod 770 /storage/admin
chmod 770 /storage/security
chmod 770 /storage/sysadmin