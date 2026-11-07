#!/bin/bash

slcand -F -o -c -s5 /dev/serial/by-id/usb-Openlight_Labs_CANable2_b158aa7_github.com_normaldotcom_canable2.git_3670335A3036-if00 slcan0 &

sleep 1
ip link set dev slcan0 up || exit 1

while ip -o link show up dev slcan0 | grep -q .; do
    sleep 1
done

echo "slcan0 is missing or down"
exit 1
