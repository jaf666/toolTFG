from typing import Tuple
from parser import Parser
from serviceDiscovery import someipSD
from someip import Someip
from socketUDP import socketHandler
import os, sys
# Agrega el directorio raíz del proyecto al path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from plugins.VehicleDynamicsPlugin import VehicleDynamicsPlugin

class MyLab:
    """
    Clase para realizar las simulaciones requeridas.
    Permite el inicio de un servidor SOME/IP siguiendo el flujo determinado
    por las especificaciones de AUTOSAR. Así como el envío de eventos una vez
    iniciado el mismo.
    """
    def __init__(self):
        self.myParser = Parser()
        self.data_dst = None

    def start_someip_server(
        self,
        ecu_pair: Tuple[str, str],
        service_id: int
    ) -> Tuple[bool, str]:
        """
        Comienza un servidor SOME/IP. Se debe especificar la tupla de ECUs
        (origen, destino) y el ID del servicio a simular.

        :param ecu_pair: Tupla con las ECUs (simulada, real)
        :type ecu_pair: tuple[str, str]

        :param service_id: ID del servicio SOME/IP a simular
        :type service_id: int

        :return: True si se completó con éxito, False en caso de error y mensaje
        :rtype: bool, str
        """
        origen, destino = ecu_pair
        allowed_ecus = self.myParser.get_ecus()

        # Si el par de ECUs no se ecuentra entre las posibles devolver error
        for ecu in ecu_pair:
            if ecu not in allowed_ecus:
                raise NotImplementedError(
                    f"ECU '{ecu}' no está soportada. Solo se permiten: {allowed_ecus}"
                )
        
        # Comienza el servidor SOME/IP
        try:
            sd = someipSD()
            sock = socketHandler()
            self.data_dst = sd.myParser.ecu1_to_ecu2(origen, destino)

            udp_sock = sock.bind_udp_socket(self.data_dst["ip_src"], self.data_dst["udp_dst"])

            i = 0
            while i != 1:

                offer_packet = sd.craft_offer_packet(origen, destino, service_id)
                ack = sd.craft_subscribeEventGroupACK_packet(origen, destino, service_id)
                
                print("[INFO] Enviando OFFER...")
                sd.sendSDpacket(offer_packet)
                
                pkt_subscribe = sock.escuchar_subscribe_eventgroup(ack)
                for x in range(0, 15):
                    self.someip_server_send_event(service_id)
                
                i+=1
                # Aqui se incia el envio de eventos someip. El ttl es de 3 asi que cada 0.2s se envia un paquete
                # 3/0.2 nos da apra 15 paquetes la secuencia antes de que se desuscriba.
                

            udp_sock.close()
            return True, "Servidor iniciado correctamente"

        except Exception as e:
            error_msg = f"[ERROR] Error al iniciar servidor SOME/IP: {e}"
            return False, error_msg

    def someip_server_send_event(self, service_id: int):
        """
        Manda un evento

        :param service_id: Número del servicio
        :type event_name: int

        :return: verdict and comment
        :rtype: bool, str
        """

        try:
            print("[INFO] Enviando EVENTO...")
            some = Someip()
            pk = some.craft_someip_pk(service_id, self.data_dst)
            pk.show()
            some.send_someip(pk)
        except Exception as e:
            return False, "Error al enviar el evento"

    def stop_someip_server():
        pass
