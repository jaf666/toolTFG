from scapy.contrib.automotive.someip import *
from scapy.all import *
from typing import Any, Dict
from parser import Parser

class Someip():
    """
    Clase empleada para la creación y envío de paquetes SOME/IP
    """
    def __init__(self,):
        self.some = SOMEIP()
        self.myParser = Parser()

    def craft_someip_pk(self, service: int, data_dst: Dict[str, Any]) -> Ether:
        data = self.myParser.get_service_data(service)
        payload = data["SOMEIP"]["Payload"]

        #self.some.srv_id = data["SOMEIP"]["ServID"] # perfe
        #self.some.sub_id = data["SOMEIP"]["SubID"] # perfe
        #self.some.event_id = service

        #self.some.session_id = 0x0000  # puede ser random si quieres
        #self.some.msg_type = data["SOMEIP"]["MessageType"]  # 0x83 = Notification (Cyclic Event)

        self.some.srv_id = 0x008C
        self.some.method_id = data["SOMEIP"]["MethodID"]
        self.some.client_id = 0x0001
        self.some.session_id = 0x0000
        self.some.iface_ver = 1
        self.some.proto_ver = 1
        self.some.msg_type = 2
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
        pass