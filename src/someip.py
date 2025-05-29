from scapy.contrib.automotive.someip import *
from scapy.all import Ether, Dot1Q, IP, sendp
from typing import Any, Dict
from parser import Parser
import sys, os
# Agrega el directorio raíz del proyecto al path para importar los plugins
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from plugins.VehicleDynamicsPlugin import VehicleDynamicsPlugin

class Someip():
    """
    Clase empleada para la creación y envío de paquetes SOME/IP
    ToDo session id
    """
    __session_id = 0

    def __init__(self,):
        self.some = SOMEIP()
        self.myParser = Parser()
        Someip.__session_id += 1
        self.some.session_id = Someip.__session_id

    def craft_someip_pk(self, service: int, data_dst: Dict[str, Any]) -> Ether:
        data = self.myParser.get_service_data(service)
        # Antes esto:
        #payload = data["SOMEIP"]["Payload"]
        #new = Someip()
        # Creamos la instancia del servicio a simular con la payload
        plugin = VehicleDynamicsPlugin()
        payload = plugin.get_payload("VehicleSpeed")
        # payload = struct.pack(
        #     "<BfBBBfBB",  # estructura
        #     1,            # vehicleSpeedValueState (VALID)
        #     12.34,        # vehicleSpeed (float32)
        #     1,            # vehicleSpeedSignValueState (VALID)
        #     1,            # vehicleSpeedSign (FORWARD)
        #     1,            # vehicleLowSpeedValueState (VALID)
        #     0.12,         # vehicleLowSpeed (float32)
        #     1,            # standStillSupposedValueState (VALID)
        #     1             # standStillSupposed (STANDSTILL)
        # )
        self.some.srv_id = 568
        self.some.sub_id = 32908
        self.some.client_id = 0x0701
        self.some.proto_ver = 0x01
        self.some.iface_ver = 0x01
        self.some.msg_type = 0x02
        self.some.retcode = 0x00

        # Se añade la payload para que SOMEIP tenga su campo data correctamente rellenado
        self.some.add_payload(payload)
        #self.some.len = len(payload) + 8
        
        pk = (
            Ether(src=data_dst["mac_address"], dst=data_dst["mac_dst"]) /
            Dot1Q(vlan=data_dst["vlan"], prio=5) /
            IP(src=data_dst["ip_src"], dst=data_dst["ip_dst"]) /
            UDP(sport=data_dst["someip_port_src"], dport=data_dst["someip_port_dst"]) /
            self.some /
            # Se fuerza a que realmente se envíe la carga útil
            Raw(load=payload)
        )
        return pk
    
    def send_someip(self, pk):
        sendp(x=pk, verbose=False, iface='eth1')

