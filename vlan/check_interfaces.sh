#!/bin/bash

# Argumento: nombre base de la interfaz, por ejemplo eth0
IFBASE="$1"

if [ -z "$IFBASE" ]; then
    echo "Uso: $0 <interfaz_base>"
    exit 1
fi

# Encuentra todas las interfaces que empiezan por IFBASE
INTERFACES=$(ip -o link show | awk -F': ' '{print $2}' | grep -E "^$IFBASE(\..*)?$")

# Recorre cada interfaz encontrada
for IFACE in $INTERFACES; do
    echo "Interfaz: $IFACE"

    # Obtén la MAC
    MAC=$(ip link show "$IFACE" | awk '/link\/ether/ {print $2}')
    echo "  MAC: $MAC"

    # Obtén la IP y Broadcast
    IPINFO=$(ip -4 addr show "$IFACE" | grep -oP 'inet \K[\d.]+\/\d+')
    if [ -n "$IPINFO" ]; then
        IP=$(echo "$IPINFO" | cut -d/ -f1)
        BROADCAST=$(ip -4 addr show "$IFACE" | grep -oP 'brd \K[\d.]+')
        echo "  IPv4: $IP"
        echo "  Broadcast: $BROADCAST"
    else
        echo "  IPv4: (no asignada)"
        echo "  Broadcast: (no disponible)"
    fi

    # Si es una subinterfaz, intenta extraer VLAN ID
    if [[ "$IFACE" =~ \.([0-9]+)$ ]]; then
        VLAN_ID="${BASH_REMATCH[1]}"
        echo "  VLAN: $VLAN_ID"
    else
        echo "  VLAN: (no aplica)"
    fi

    echo
done