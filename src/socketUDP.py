from scapy.all import *
from parser import Parser
from serviceDiscovery import someipSD
import socket
from scapy.contrib.automotive.someip import *

class socketHandler():
    """
    El objetivo de esta clase es proporcionar los métodos necesarios para abrir un socket
    en el puerto indicado por nuestra ECU simulada. Que recibirá en mensaje SOME/IP de tipo
    SubscribeEventGroup. Para ello hago bind sobre el puerto y escucho los paquetes que 
    lleguen de la interfaz eth1 con unos parámetros determinados por un filtro. Esto introduce
    una pequeña latencia por parte de la función sniff, que es considerada en la simulación.
    """
    def bind_udp_socket(self, ip, port):
        """
        Función para hacer bind al puerto, de no ser así se observará un mensaje ICMP de destination+
        port unreachable, ya que no existe un puerto en el sistema operativo para recibir el mensaje
        SOME/IP enviado por la ECU real en la ECU simulada.
        """
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind((ip, port))
        s.setblocking(False)
        print(f"[INFO] Socket UDP escuchando en {ip}:{port}")
        return s

    # Aqui el service id no esta bien
    def escuchar_subscribe_eventgroup(self, ack, interface="eth1", timeout=5):
        print("[INFO] Esperando SubscribeEventGroup...")
        # Se envia el ACK de forma anticipada dando por hecho que habra subscribe por parte del cliente.
        # De no haberlo se producira un error, ya que no encontrará el mensaje con el type indicado ni 
        # el service id.
        someipSD().sendSDpacket(ack)

        def filtro(pkt):
            if pkt.haslayer(SOMEIP):
                someip = pkt.getlayer(SOMEIP)
                if hasattr(someip, "entry_array"):
                    for entry in someip.entry_array:
                        if entry.type == 0x06:
                            print("[OK] SubscribeEventGroup recibido:")
                            print("[INFO] Enviando ACK...")
                            print("[OK] ACK enviado.")
                            # Muestra el paquete
                            pkt.show()
                            return True
            return False

        pkt = sniff(iface=interface, timeout=timeout, stop_filter=filtro, store=1)
        return pkt[0] if pkt else None