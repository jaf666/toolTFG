from scapy.all import *
from scapy.contrib.automotive.someip import *
from typing import Dict, Any

class someipSD():
    def __init__(self, ):
        # La cabacera es SOMEIP y es la misma para todos los paquetes
        self.header = SOMEIP()
        # Se establece el message ID (Service ID / Method ID)
        self.header.srv_id = SD.SOMEIP_MSG_TYPE
        self.header.method_id = 0x8100
        # Se establece el message type a 0x02, ya que los mensajes SD son de tipo notification
        self.header.msg_type = SD.SOMEIP_MSG_TYPE

        # Se inicializa la parte de sd
        self.s = SD()
        # We have the reaming fields:
        # flags, res, len_entry_array, entry_array, len_option_array, option array

    def craft_offer_packet():
        """
        This method is used to craft the SOMEIP offer packet
        """
        # We have to create the offer packet with the fields:
        # flags, res, len_entry_array, entry_array, len_option_array, option array
        someip_sd_payload = (
            # Payload for the SOMEIP packet
            b"\x00\x00\x00\x00\x00\x00\x00\x00"
        )
        # Capa de red con VLAN    
        packetSD = (
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
    
    def entry_array(self, entry_array: Dict[str, Any]):
        """
        This method is used to create the entry array
        """
        # We have to create the entry array with the fields:
        # flags, res, len_entry_array, entry_array, len_option_array, option array
        self.s.entry_array = entry_array
        # We have to create the option array with the fields:
        # flags, res, len_entry_array, entry_array, len_option_array, option array
        self.s.option_array = option_array

