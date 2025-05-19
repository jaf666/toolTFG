from scapy.contrib.automotive.someip import *
from scapy.all import Ether, Dot1Q, IP, sendp
from typing import Any, Dict
from parser import Parser

class Someip():
    """
    Clase empleada para la creación y envío de paquetes SOME/IP
    ToDo session id
    """
    def __init__(self,):
        self.some = SOMEIP()
        self.myParser = Parser()

    def craft_someip_pk(self, service: int, data_dst: Dict[str, Any]) -> Ether:
        data = self.myParser.get_service_data(service)
        payload = data["SOMEIP"]["Payload"]

        self.some.srv_id = 568
        self.some.sub_id = 32908
        self.some.client_id = 0x0701
        self.some.session_id = 0x0001
        self.some.proto_ver = 0x01
        self.some.iface_ver = 0x01
        self.some.msg_type = 0x02
        self.some.retcode = 0x00
        self.some.add_payload(payload)

        pk = (
            Ether(src=data_dst["mac_address"], dst=data_dst["mac_dst"]) /
            Dot1Q(vlan=data_dst["vlan"], prio=5) /
            IP(src=data_dst["ip_src"], dst=data_dst["ip_dst"]) /
            UDP(sport=data_dst["someip_port_src"], dport=data_dst["someip_port_dst"]) /
            self.some
        )
        return pk
    
    def send_someip(self, pk):
        sendp(x=pk, verbose=False, iface='eth1')

    def custom_payload():
        """
        Función para customizar el payload, la idea sería dado un servicio parsear el def
        file asociado al evento que queremos simular. Extrayendo sus campos para poder establecerlos
        """
        pass