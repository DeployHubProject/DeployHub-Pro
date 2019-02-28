#!/bin/sh
set -x
sudo chown -R postgres:postgres /var/lib/pgsql
chmod -R 777 /opt/deployhub

pkill postgres

if sudo test -f "/var/lib/pgsql/data/pg_hba.conf"; then
 echo "Database already initialized"
else
 mkdir /tmp/data
 sudo chown postgres:postgres /tmp/data
 sudo -u postgres pg_ctl initdb --pgdata=/tmp/data
 sudo cp -rp /tmp/data /var/lib/pgsql
 sudo chown -R postgres:postgres /var/lib/pgsql
fi

sudo -u postgres pg_ctl start --pgdata=/var/lib/pgsql/data
sleep 10
sudo -u postgres pg_ctl status --pgdata=/var/lib/pgsql/data

if [ ! -e /opt/deployhub/logs ]; then
 mkdir /opt/deployhub/logs
fi

cd /opt/deployhub/engine
export LD_LIBRARY_PATH=$PWD/lib:$PWD/bin
export PATH=$PWD/lib:$PWD/bin:$PATH
export HOME=$(getent passwd `whoami` | cut -d: -f6)

cp -r /keys/* $HOME/.ssh
cp -r /keys/* /root/.ssh

sudo chmod 700 /root/.ssh
sudo chmod 700 /root/.ssh/*
sudo chmod 600 /root/.ssh/authorized_keys

chown -R omreleng $HOME/.ssh 
chmod 700 $HOME/.ssh
chmod 700 $HOME/.ssh/*
chmod 600 $HOME/.ssh/authorized_keys

echo Running DeployHub Processes

/opt/deployhub/engine/trilogyd 1>/opt/deployhub/logs/engine.out 2>/opt/deployhub/logs/engine.err &
java -jar /opt/deployhub/webadmin/webapp-runner.jar --path /dmadminweb /opt/deployhub/webadmin/deployhub-webadmin.war 1>/opt/deployhub/logs/deployhub.log 2>&1
