#!/bin/bash
echo 1 > /sys/class/net/enp24s0f0/device/sriov_numvfs
echo 1 > /sys/class/net/enp24s0f1/device/sriov_numvfs
echo 1 > /sys/class/net/enp175s0f0/device/sriov_numvfs
echo 1 > /sys/class/net/enp175s0f1/device/sriov_numvfs
ip link set enp24s0f0 vf 0 spoofchk off
ip link set enp24s0f1 vf 0 spoofchk off
ip link set enp175s0f0 vf 0 spoofchk off
ip link set enp175s0f1 vf 0 spoofchk off
