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
        Abre un socket UDP en la dirección IP y puerto especificados para 
        permitir la recepción de mensajes SOME/IP.

        Este paso es necesario para evitar que el sistema operativo genere 
        mensajes ICMP de "destination port unreachable" cuando se recibe un 
        mensaje destinado a un puerto no vinculado.

        :param ip: Dirección IP local de la ECU simulada.
        :type ip: str

        :param port: Puerto UDP en el que se debe hacer bind.
        :type port: int

        :return: Objeto socket UDP vinculado, en modo no bloqueante.
        :rtype: socket.socket
        """
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind((ip, port))
        s.setblocking(False)
        print(f"[INFO] Socket UDP escuchando en {ip}:{port}")
        return s

    # Aqui el service id no esta bien
    def escuchar_subscribe_eventgroup(self, ack, interface="eth1", timeout=5):
        """
        Escucha en la interfaz de red la llegada de un mensaje SOME/IP de tipo 
        SubscribeEventGroup. Se utiliza un filtro en `sniff` para identificar 
        y detener la captura cuando se detecta un paquete válido.

        Además, se envía de forma anticipada un mensaje ACK usando un paquete
        construido previamente, asumiendo que el cliente enviará una suscripción.

        :param ack: Paquete SOME/IP de tipo ACK a enviar antes de escuchar.
        :type ack: scapy.packet.Packet

        :param interface: Interfaz de red por la que se escucharán los paquetes.
        :type interface: str

        :param timeout: Tiempo máximo de espera (en segundos) para la captura.
        :type timeout: int

        :return: Paquete SOME/IP recibido que cumple con las condiciones del filtro,
                o `None` si no se detecta ninguno en el tiempo especificado.
        :rtype: scapy.packet.Packet | None
        """
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