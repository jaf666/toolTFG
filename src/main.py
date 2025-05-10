from scapy.all import Ether, IP, UDP, Dot1Q, Raw, sendp
from parser import Parser
from serviceDiscovery import someipSD
import os

def main():
    # Setting up the networks
    # try: 
    #     os.system("sudo ./vlan_set/vlan3.sh IVC3_MySF26.2_SWEET500 vlan2")
    # except Exception as e:
    #     print(f"Error setting the networks: {e}")
    
    # En mi caso particular fijo las ecus de simulacion, esto puede ser un combobox
    origen = "PCU_Proxy_Frontend"
    destino = "IVC"
    # Fijo tambien el evento de prueba
    msg_to_simulate = "VehicleDynamics"
    event = "VehicleSpeed"
    # La secuencia empieza con el ofrecimiento de servicios, para ello, hay que crear un offer con SD
    # Para ello, habra que saber a donde mandar el offer, extraigo los datos de un json
    sd = someipSD()
    packet = sd.craft_offer_packet(origen, 140)
    # Envio el paquete a la red
    sendp(packet, iface="eth1", verbose=False)

# At the moment is not neccesary to have parameters, check argparse
if __name__ == "__main__":
    main()
