#!/bin/bash
virsh attach-disk ats_vm /dev/sdb vdc --config --type disk
