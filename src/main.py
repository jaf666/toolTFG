from scapy.all import *
from scapy.contrib.automotive.someip import *
from parser import Parser
from serviceDiscovery import someipSD
import os

def listen_for_subscribe(expected_service_id, timeout=2):
    # Socket raw UDP para recibir respuestas SOME/IP
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', 30490))  # Asegúrate de usar el puerto del SD

    sock.settimeout(timeout)
    try:
        ready = select.select([sock], [], [], timeout)
        if ready[0]:
            raw_data, addr = sock.recvfrom(2048)
            pkt = SOMEIP(raw_data)
            if hasattr(pkt, "entry_array"):
                for entry in pkt.entry_array:
                    if entry.type == 6 and entry.srv_id == expected_service_id:
                        print("¡Recibido Subscribe válido!")
                        pkt.show()
                        return True
    except Exception as e:
        print("Timeout o error al recibir:", e)
    finally:
        sock.close()
    return False

def main():    
    # En mi caso particular fijo las ecus de simulacion, esto puede ser un combobox
    origen = "PCU_Proxy_Frontend"
    destino = "IVC"
    # Fijo tambien el evento de prueba
    service = 140

    # La secuencia empieza con el ofrecimiento de servicios, para ello, hay que crear un offer con SD
    # Para ello, habra que saber a donde mandar el offer, extraigo los datos de un json
    sd = someipSD()
    
    packet = sd.craft_offer_packet(origen, destino, service)
    # Envio el paquete a la red
    sendp(packet, iface="eth1", verbose=False)
    print("Offer enviado. Escuchando Subscribe...")
    if listen_for_subscribe(service):
        print("Envuiando ACK...")
        ack = sd.craft_subscribeEventGroupACK_packet(origen, destino, service)
        # Tiempo suficiente para poder recibir el subscribe
# At the moment is not neccesary to have parameters, check argparse
if __name__ == "__main__":
    main()
