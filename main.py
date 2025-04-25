from scapy.all import Ether, IP, UDP, Dot1Q, Raw, sendp
import os

# Function to set the VLANs on the network interface
def set_vlans() -> bool:
    # At the moment vlan is hardcoded, when the scrip is runned, it will
    # atomatically run the bash script to set the VLANs
    # Check if the bash script exists in the same directory
    if not os.path.exists("vlan.sh"):
        print("vlan.sh not found")
        return
    print("Executing vlan.sh...")
    # Run the bash script to set the VLANs with the requiered parameters
    os.system("sudo bash vlan.sh")

def create_someip_packet():
    someip_sd_payload = (
        # Payload for the SOMEIP packet
        # Someip payload
        b"\x00\x00\x00\x00\x00\x00\x00\x00"  # Placeholder for the SOMEIP payload
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
        # GEstionar el tema de someip a parte
        Raw(load=someip_sd_payload)
    )
# Create a main function
def main():
    # Call the script parsing the arguments
    os.system("sudo ./vlan_set/vlan3.sh IVC3_MySF26.2_SWEET500 vlan2")
    
    # En mi caso particular fijo las ecus de simulacion, esto puede ser un combobox
    origen = "PCU"                                      
    destino = "SA"
    # Fijo tambien el evento de prueba
    msg_to_simulate = "VehicleDynamics"
    event = "VehicleSpeed"
    # Funcion para cargar la data de este evento en particular.

# At the moment is not neccesary to have parameters, check argparse
if __name__ == "__main__":
    main()
