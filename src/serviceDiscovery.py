from scapy.all import *
from scapy.contrib.automotive.someip import *
from parser import Parser
from typing import Dict, Any

class someipSD():
    def __init__(self, ):
        self.myParser = Parser()
        # La cabacera es SOMEIP y es la misma para todos los paquetes
        self.header = SOMEIP()
        # Se establece el message ID (Service ID / Method ID)
        self.header.srv_id = SD.SOMEIP_MSGID_SRVID
        self.header.method_id = 0x8100
        # Se establece el message type a 0x02, ya que los mensajes SD son de tipo notification
        self.header.msg_type = SD.SOMEIP_MSG_TYPE

        # Se inicializa la parte de sd
        self.s = SD()
        self.s.flags = 0x03

    def _setSDEntry(self, method_data: Dict[str, Any], option: str, data_dst: Dict[str, Any]):
        """
        This method is used to set the entry value and the option array
        """
        aux_entry = []
        entry = SDEntry_Service()
        if option == "OFFER":
            entry.type = 1
            # int(method_data["OFFER"]["Type"], 16)
            entry.srv_id = method_data["SOMEIP"]["ServID"]
            entry.major_ver = int(method_data["OFFER"]["Major_Version"], 16)
            entry.minor_ver = int(method_data["OFFER"]["Minor_Version"], 16)
            entry.n_opt_1 = 0x01
            entry.inst_id = 0x0001
            entry.ttl = 3
            aux_entry.append(entry)
            # Ahora hay que crear el option array
            option_array = SDOption_IP4_EndPoint()
            option_array.addr = data_dst["ip"]
            option_array.l4_proto = int(data_dst["option_sdprot"], 16)
            option_array.port = data_dst["option_sdport"]
            
            self.s.set_entryArray(aux_entry)
            self.s.set_optionArray(option_array)
    
    def craft_offer_packet(self, sender: str, destino: str, service: int) -> Ether:
        """
        This method is used to craft the SOMEIP offer packet
        It returns the packet to be sent
        """
        data_ack = self.myParser.ecu1_to_ecu2("PCU_Proxy_Frontend", "IVC")

        data_dst = self.myParser.multicast(sender)
        # We have to create the offer packet with the fields:
        # flags, res, len_entry_array, entry_array, len_option_array, option array

        # Busco con mi instancia parser el servicio que quiero ofrecer y obtengo los datos
        myDic = self.myParser.get_service_data(service)

        # Tengo la información para ir creando el ACK que enviaré cuando reciba el subscribe del cliente
        self.craft_subscribeEventGroupACK_packet(data_ack, myDic)

        # Con esos datos creo el entry value y el option array con una funcion privada
        self._setSDEntry(myDic, "OFFER", data_dst)

        # Cabecera SOMEIP y la payload es la parte de SD
        self.header.payload = self.s
        # Capa de red con VLAN    
        packetSD = (
            # Aqui va a a tener una mac origen y una mac destino
            Ether(src=data_dst["mac_address"], dst=data_dst["MAC_1500_MULTICAST"]) /  # Multicast MAC para 224.244.224.245
            # Estandar que define el tagueado de la VLAN, a mi me interesa la 1500
            Dot1Q(vlan=data_dst["vlan"], prio=5) /
            # Direccion ip fuente y direccion IP destino
            IP(src=data_dst["ip"], dst=data_dst["IP_1500_MULTICAST"]) /
            # Direccion UDP fuente y destino
            UDP(sport=data_dst["sd_port_src"], dport=data_dst["sd_port_dst"]) /
            # La gestion de SD la hace la clase someipSD
            self.header
        )
        return packetSD

    # El entry_array contiene objetos como SDEntry_Service en el caso de FindService y OfferService
    # En el caso de offer, el entry_array define qué servicios se ofrecen, y qué instancias del mismo
    # El option array describe cómo acceder al servicio mencionado en el entry array

    # Dependiendo del tipo de mensaje vamos a tener entradas distintas en el entry array, en el caso
    # de offer service, el entry array contendrá un objeto de tipo SDEntry_Service, que contendrá
    # el service id, el instance id y el flags. El flags es un entero que contiene la información
    # de si el servicio es multicast o unicast, y si es unicast, la dirección IP de destino.

    def _SDEntry_EventGroup(self, method_data: [Dict[str, Any]]):
        """
        This method is used to add the entry value to the entry array
        """
        aux = []
        entry = SDEntry_EventGroup()
        entry.type = 0x07
        entry.index_1 = 0x00
        entry.index_2 = 0x00
        entry.n_opt_1 = 0x0
        entry.n_opt_2 = 0x0
        entry.srv_id = method_data["SOMEIP"]["ServID"]
        entry.inst_id = 0x0001
        entry.major_ver = int(method_data["OFFER"]["Major_Version"], 16)
        entry.ttl = 3
        entry.res = 0x000000
        entry.cnt = 0x0
        entry.eventgroup_id = method_data["SUBSCRIBE"]["EventgroupID"]
        aux.append(entry)
        self.s.set_entryArray(aux)
        
    def craft_subscribeEventGroupACK_packet(self, sender, destino, service: int) -> Ether:
        data_dst = self.myParser.ecu1_to_ecu2(sender, destino)
        method_data = self.myParser.get_service_data(service)

        self._SDEntry_EventGroup(method_data)

        self.header.payload = self.s
        packetACKSD = (
        # Aqui va a a tener una mac origen y una mac destino
        Ether(src=data_dst["mac_src"], dst=data_dst["mac_dst"]) /  # La de la SA
        # Estandar que define el tagueado de la VLAN, a mi me interesa la 1500
        Dot1Q(vlan=data_dst["vlan"], prio=5) /
        # Direccion ip fuente y direccion IP destino
        IP(src=data_dst["ip_src"], dst=data_dst["ip_dst"]) /
        # Direccion UDP fuente y destino
        UDP(sport=data_dst["udp_src"], dport=data_dst["udp_dst"]) /
        # La gestion de SD la hace la clase someipSD
        self.header
        )
        return packetACKSD
