#!/bin/bash
set -e


#checking if vcan already exists, if not create one
if ! ip link show vcan0 >/dev/null 2>&1; then
   echo "Loading vcan0 kernal module..."
   #sudo modprobe vcan
   #echo "Creating vcan0 interface..."

   ip link add dev vcan0 type vcan
   echo "ip link add"

   ip link set vcan0 mtu 72
   echo "ip link set vcan0"

   ip link set up vcan0
   echo "ip link set up vcan0"

   #bitrate 250000 (use for physical can)
   echo "vcan0 set up is complete."
else
   echo "vcan0 already exists"


fi
echo "Verifying module loaded succesfully..."
lsmod | grep vcan
#output should be similar to: vcan         16384 0


echo "Running app..."
exec /app/build/onboard-can-deserializer