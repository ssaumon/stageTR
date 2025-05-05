#!/bin/bash
 virsh destroy $1
 virsh undefine $1
 
 ./backend/deliphost.sh $1
 rm backend/cloudinit/user-data.d/$1
 rm backend/cloudinit/meta-data.d/$1
 rm /mnt/vms/$1.qcow2