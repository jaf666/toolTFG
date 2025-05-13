from scapy.all import *
from parser import Parser
from serviceDiscovery import someipSD
import socket
from scapy.contrib.automotive.someip import *

def bind_udp_socket(ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((ip, port))
    s.setblocking(False)
    print(f"[INFO] Socket UDP escuchando en {ip}:{port}")
    return s

def escuchar_subscribe_eventgroup(ack, interface="eth1", service_id=0x008C, timeout=5):
    print("[INFO] Esperando SubscribeEventGroup...")
    # Se envia el ACK de forma anticipada dando por hecho que habra subscribe por parte del cliente.
    # De no haberlo se producira un error, ya que no encontrará el mensaje con el type indicado ni 
    # el service id.
    sendp(ack, iface="eth1", verbose=False)

    def filtro(pkt):
        if pkt.haslayer(SOMEIP):
            someip = pkt.getlayer(SOMEIP)
            if hasattr(someip, "entry_array"):
                for entry in someip.entry_array:
                    if entry.type == 0x06:
                        print("[OK] SubscribeEventGroup recibido:")
                        print("[INFO] Enviando ACK...")
                        print("[OK] ACK enviado.")
                        pkt.show()
                        return True
        return False

    pkt = sniff(iface=interface, timeout=timeout, stop_filter=filtro, store=1)
    return pkt[0] if pkt else None

def main():    
    origen = "PCU_Proxy_Frontend"
    destino = "IVC"
    service = 140

    sd = someipSD()
    data_dst = sd.myParser.ecu1_to_ecu2(origen, destino)

    # Abre socket UDP para que no responda ICMP
    udp_sock = bind_udp_socket(data_dst["ip_src"], data_dst["udp_dst"])

    offer_packet = sd.craft_offer_packet(origen, destino, service)
    ack = sd.craft_subscribeEventGroupACK_packet(origen, destino, service)

    print("[INFO] Enviando OFFER...")
    sendp(offer_packet, iface="eth1", verbose=False)

    pkt_subscribe = escuchar_subscribe_eventgroup(ack, interface="eth1", service_id=service)

    udp_sock.close()

if __name__ == "__main__":
    main()
