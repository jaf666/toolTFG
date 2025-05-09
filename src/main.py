from scapy.all import Ether, IP, UDP, Dot1Q, Raw, sendp
import os


def create_someip_packet():
    someip_sd_payload = (
        # Payload for the SOMEIP packet
        b"\x00\x00\x00\x00\x00\x00\x00\x00"
    )
    # Capa de red con VLAN    
    packet = (
        # Aqui va a a tener una mac origen y una mac destino
        Ether(src="127.0.0.1", dst="01:00:5e:4e:e4:f5") /  # Multicast MAC para 224.244.224.245
        # Estandar que define el tagueado de la VLAN, a mi me interesa la 1500
        Dot1Q(vlan=1500) /
        # Direccion ip fuente y direccion IP destino
        IP(src="192.168.100.2", dst="224.244.224.245") /
        # Direccion UDP fuente y destino
        UDP(sport=30490, dport=30490) /
        # Gestionar el tema de someip a parte
        Raw(load=someip_sd_payload)
    )

def main():
    # Setting up the networks
    # try: 
    #     os.system("sudo ./vlan_set/vlan3.sh IVC3_MySF26.2_SWEET500 vlan2")
    # except Exception as e:
    #     print(f"Error setting the networks: {e}")
    
    # En mi caso particular fijo las ecus de simulacion, esto puede ser un combobox
    origen = "PCU"
    destino = "SA"
    # Fijo tambien el evento de prueba
    msg_to_simulate = "VehicleDynamics"
    event = "VehicleSpeed"
    # La secuencia empieza con el ofrecimiento de servicios, para ello, hay que crear un offer con SD
    # Para ello, habra que saber a donde mandar el offer, extraigo los datos de un json


# At the moment is not neccesary to have parameters, check argparse
if __name__ == "__main__":
    main()
