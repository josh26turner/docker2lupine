#!/bin/bash -e

TAP_DEV="tap100"

GUEST_IP="192.168.100.2"
HOST_IP="192.168.100.1"
GUEST_MAC="02:FC:00:00:00:05"

ip link del $TAP_DEV 2> /dev/null || true
ip tuntap add dev $TAP_DEV mode tap
ip addr add $HOST_IP/24 dev $TAP_DEV
ip link set dev $TAP_DEV up

{
  iptables -t nat -A POSTROUTING -o `route | grep default | sed 's/  */ /g' | cut -d' ' -f 8` -j MASQUERADE
  iptables -A FORWARD -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
  iptables -A FORWARD -i tap100 -o `route | grep default | sed 's/  */ /g' | cut -d' ' -f 8` -j ACCEPT
} &

cat <<EOF > /tmp/vmconfig.json
{
  "boot-source": {
    "kernel_image_path": "kernelbuild/$1",
    "boot_args": "console=ttyS0 noapic reboot=k panic=1 pci=off ipv6.disable=1 nomodules ip=$GUEST_IP::$HOST_IP:255.255.255.0:$1:eth0:off init=$2"
  },
  "drives": [
    {
      "drive_id": "rootfs",
      "path_on_host": "rootfsbuild/$1.ext4",
      "is_root_device": true,
      "is_read_only": false
    }
  ],
  "network-interfaces": [
      {
        "iface_id": "eth0",
        "guest_mac": "$GUEST_MAC",
        "host_dev_name": "$TAP_DEV"
      }
  ],
  "machine-config": {
    "vcpu_count": 1,
    "mem_size_mib": 1024,
    "ht_enabled": false
  }
}
EOF

firecracker --no-api --config-file /tmp/vmconfig.json
