#!/bin/bash

# Define vlans on a global matrix
vlans=(
    "110 192.168.11.10/24 AA:BB:CC:DD:00:0A 255.255.255.255"        # DTOOL - DoIP_Virgin_Mode_DoIP_Public_Address
    "2110 192.168.139.96/24 AA:BB:CC:DD:00:60 255.255.255.255"      # PCU_DMZ_Env_BackEnd -> DoIP_Normal_Mode_DoIP_Fixed_Address
    "2120 192.168.140.110/24 AA:BB:CC:DD:10:0A 255.255.255.255"     # DTOOL_1000BASE_T1 - DoIP_OBD2_Mode_DoIP_Fixed_Address
    "1500 192.168.114.98/24 AA:BB:CC:DD:20:60 255.255.255.255"      # PCU_PROXY_FrontEnd -> SOME_IP_Unsecure_Domain_01
)
# This script sets up VLAN on the eth1 network interface.
# Remove extra bridge docker interfaces
removeExtraBridgeInterfaces () {
    msg=$(ip -o link show | awk -F ': ' '{print $2}' | grep 'br-' | awk -F '-' '{print $2}')
    for i in $msg ; do
        docker network rm "$i"
    done
}

# Restart Docker daemon
restartDockerDaemon () {
    sleep 0.5
    systemctl restart docker
}

# Initialize docker file config
initDocker0File (){
    echo -e '{\n\t"bip": "172.18.0.1/24"\n}' > "$1"
}

# Check docker Network configuration
checkDockerNetwork () {
    removeExtraBridgeInterfaces
    if [ -f "$DOCKER0CONFIGFILE" ]; then
        msg=$(cat $DOCKER0CONFIGFILE | grep '"bip": "172.18.0.1/24"')
        if [[ $msg ]]; then
            msg2=$(ifconfig -a | grep '172.18.0.1' | awk '{print $2}')
            if [[ "$msg2" ]]; then
                echo -e "\t¬Docker network config is correct"
            else
                restartDockerDaemon
            fi
        else
            initDocker0File $DOCKER0CONFIGFILE
            restartDockerDaemon
        fi
    else
        initDocker0File $DOCKER0CONFIGFILE
        restartDockerDaemon
    fi
}
# Function that checks if the script is run as root by checking
# the effective user ID (EUID). It must be 0 for root.
check_root() { 
    if [ "$EUID" -ne 0 ]; then
        echo "This script must be run as root. Please use sudo."
        exit 1
    fi
}

# Initialize networks interfaces
initNetworks () {
    # Remove VLANs
    for interface in $(ip -o link show type vlan | awk '{gsub(/@.*/, "", $2); print $2}'); do
        sudo ip link delete dev "$interface"
        echo -e "\t  VLAN interface $interface succesfully removed"
        sleep 0.25s
    done

    # Remove macvlans
    macvlan_interfaces=("piu_mst" "pcu_cp_1" "pcu_cp_2")
    for interface in "${macvlan_interfaces[@]}"; do
        if ip link show "$interface" &> /dev/null; then
            echo -e "\t  Macvlan interface $interface removed"
            if ! ip link delete "$interface"; then
                echo -e "\t  Error removing macvlan interface $interface"
            fi
        fi
    done

    # Remove bridges
    for bridge in $(ip link show type bridge | awk -F: '/br[0-9]/{print $2}'); do
        if [ "$bridge" == "br0" ]; then
            sudo ip link delete dev "$bridge" type bridge
            echo -e "\t  Bridge $bridge succesfully removed"
            sleep 0.25s
        fi
    done

    # Bring down specific Ethernet interfaces (eth1, eth2, eth3, eth4, etc.)
    for interface in $(ip -o link show | awk -F: '/eth[0-9]/{print $2}'); do
        if [ "$interface" != "eth0" ]; then
            sudo ip link set dev "$interface" down
            echo -e "\t  Interface $interface succesfully brougth down"
            sleep 0.25s
        fi
    done
}

# Function to check if the 8021q module is loaded
check_8021q() {
    # Check if the 8021q module is loaded
    if ! (lsmod | grep 8021q) &> /dev/null; then
        echo "8021q module is not loaded. "
        # Check if the 8021q module exists in the system
        if modinfo 8021q &> /dev/null; then
            echo "8021q module exists in the system. "
            echo "Loading 8021q module. "
            # Load the 8021q module
            modprobe 8021q
        else
            echo "8021q module is not present in the kernel. "
        fi
    else
        echo "8021q module is already loaded. "
    fi
}

# Function to check if vconfig is installed. It its neccesary to create
# and remove subinterfaces for VLANs. As the ENDS specification requires.
check_vconfig() {
    # Check if vconfig is installed. Verifies if the command is available
    # in the system by checking if it is in the PATH.
    if ! command -v vconfig &> /dev/null; then
        apt update &> /dev/null && apt install -y vlan  &> /dev/null
    else
        echo "vconfig is already installed. "
    fi
}

#check_network_interfaces() {
#
#}

set_vlans_SA(){
    # Host - SSH
    ip addr flush dev "$2"
    ip link set dev "$2" down
    ip address add 192.168.33.2/24 dev "$2"
    
    for vlan in "${vlans[@]}"; do
        set -- "$vlan"
        vlan_id=$1
        ip_addr=$2
        mac_addr=$3
        broadcast=$4

        ip link add link "$2" name "$2"."$vlan_id" address "$mac_addr" type vlan id "$vlan_id"
        ip addr add "$ip_addr" broadcast "$broadcast" dev "$2"."$vlan_id"
    done
    
    # Piu Master · gPTP - Macvlan interface
    ip link add piu_mst link "$2" type macvlan mode bridge
    ip link set address AA:BB:CC:DD:00:39 dev piu_mst

    # PCU_CP_1 · gPTP - Macvlan interface
    ip link add pcu_cp_1 link "$2" type macvlan mode bridge
    ip link set address AA:BB:CC:DD:40:60 dev pcu_cp_1

    # PCU_CP_2 · gPTP - Macvlan interface
    ip link add pcu_cp_2 link "$2" type macvlan mode bridge
    ip link set address AA:BB:CC:DD:00:50 dev pcu_cp_2
}

up_vlans_SA() {
        # Get interfaces up
        echo -e "\tActivating networks..."
        ip link set "$2" up && msgNet "$2"
        ip link set "$2".110 up && msgNet "$2.110"
        ip link set "$2".2110 up && msgNet "$2.2110"
        ip link set "$2".2120 up && msgNet "$2.2120"
        ip link set "$2".1500 up && msgNet "$2.1500"
        ip link set piu_mst up && msgNet "piu_mst"
        ip link set pcu_cp_1 up && msgNet "pcu_cp_1"
        ip link set pcu_cp_2 up && msgNet "pcu_cp_2"

        # Configure static arp for vlans
        ip link set dev "$2".110 arp off
        ip neigh add 192.168.11.3 lladdr AA:BB:CC:DD:00:03 dev "$2".110
        ip link set dev "$2".2110 arp off
        ip neigh add 192.168.139.3 lladdr AA:BB:CC:DD:00:03 dev "$2".2110
        ip link set dev "$2".2120 arp off
        ip neigh add 192.168.140.3 lladdr AA:BB:CC:DD:00:03 dev "$2".2120
        ip link set dev "$2".1500 arp off
        ip neigh add 192.168.114.3 lladdr AA:BB:CC:DD:00:03 dev "$2".1500

        # Configure static routes (Multicast)
        #   PCU_PROXY_FrontEnd - SOME_IP_Unsecure_Domain_01
        ip route add 237.50.20.1 dev "$2".1500
        ip route add 237.50.23.1 dev "$2".1500
        ip route add 237.50.24.1 dev "$2".1500

        # Set the vlan's egress priority
        vconfig set_egress_map "$2".110 0 1  &> /dev/null
        vconfig set_egress_map "$2".2110 0 1  &> /dev/null
        vconfig set_egress_map "$2".2120 0 1  &> /dev/null
        vconfig set_egress_map "$2".1500 0 5  &> /dev/null
        echo -e "\tNetworks activated"
}

main() {
    # The script must receive two arguments, the DUT and the interface.
    if [ $# -gt 1 ] && [ $# -lt  3 ]; then
        # Check if the first argument is IVC3_MySF26.2_SWEET500
        if [ "$1" != "IVC3_MySF26.2_SWEET500" ]; then
            echo "The first argument must be IVC3_MySF26.2_SWEET500"
            exit 1
        fi
        # Check that network given by $1 is up
        ip link show | grep -w "$2" &> /dev/null || echo "Network interface is not available"
        # Check if the script is run as root 
        check_root
        # To enable VLANs 802.1Q on Linux, it is necessary to load the 8021q module
        check_8021q
        # Check vconfig. Which allows to create and remove VLANs on a network interface.
        check_vconfig
        # Check docker network configuration
        checkDockerNetwork
        sleep 0.5s

        # If it is the first time the script is run, it will create the VLANs for the required
        # DUT. If the script is run again, it will check if that VLANs have been already created.
        #check_network_interfaces
        initNetworks
        echo ""

        case $2 in
            IVC3_MySF26.2_SWEET500)
                set_vlans_SA "$@"
                sleep 0.5s
                up_vlans_SA "$@"
            ;;
        esac
    fi
}

main "$@"