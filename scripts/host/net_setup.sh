while ! ip addr | grep tap100 > /dev/null; do
    :
done

sudo ip addr add 192.168.100.1/24 dev tap100 
sudo ip link set tap100 up

if [ "$1" = "nat" ]; then
    sudo iptables -t nat -A POSTROUTING -o enp37s0 -j MASQUERADE
    sudo iptables -A FORWARD -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
    sudo iptables -A FORWARD -i tap100 -o enp37s0 -j ACCEPT
fi