#!/bin/bash
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

main() {
    # check network interface, so is not necessary to set vlans again.

    # check_network_interface @params: 
    # network 
    # ipv4 
    # mac_address 

    # The script must receive two arguments, the DUT and the interface.
    if [ $# -gt 1 ]; then
        # Check if the first argument is IVC3_MySF26.2_SWEET500
        if [ "$1" != "IVC3_MySF26.2_SWEET500" ]; then
            echo "The first argument must be IVC3_MySF26.2_SWEET500"
            exit 1
        fi
        # Check if the script is run as root 
        check_root
        # To enable VLANs 802.1Q on Linux, it is necessary to load the 8021q module
        check_8021q
        # Check vconfig. Which allows to create and remove VLANs on a network interface.
        check_vconfig

        case $1 in
            IVC3_MySF26.2_SWEET500)
                echo "dummy"
            ;;
        esac
    fi
}

main "$@"