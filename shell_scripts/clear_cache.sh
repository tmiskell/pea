#!/bin/bash
ats_dir=/opt/ats/bin

echo "[Stopping ATS]"
sudo $ats_dir/trafficserver stop
echo "[Clearing ATS Cache]"
sudo $ats_dir/traffic_server -Cclear
echo "[Clearing Host Cache]"
echo 3 | sudo tee /proc/sys/vm/drop_caches
echo "[Removing ATS Logs]"
sudo rm -v /opt/ats/var/log/trafficserver/*
echo "[Changing permissions to storage drives]"
sudo chown -v nobody:nobody /dev/nvme*
sudo chown -v nobody:nobody /dev/pmem*
echo "[Starting ATS]"
sudo $ats_dir/trafficserver start
echo "[Checking ATS Status]"
sudo $ats_dir/trafficserver status

sleep 10

tail /opt/ats/var/log/trafficserver/diags.log
