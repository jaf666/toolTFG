import os, json
from typing import List, Optional, Dict, Any


class Parser():
    """
    Clase encargada de parsear la definición de ECUs y de servicios desde archivos JSON.

    Se utiliza para abstraer y simplificar el acceso a la configuración de red, 
    identificadores SOME/IP y datos necesarios para la simulación de comunicación 
    entre ECUs.

    Los ficheros que se cargan son:
    - ecu_data.json: contiene información de red y configuración de cada ECU.
    - services.json: contiene la definición de los servicios y métodos SOME/IP.
    """
    # Se incluyen las rutas relatativas de los fichero que contienen la información
    # de las ECUs y de los servicios asociados a las mismas.
    ECU_DATA_PATH = "../data/ecu_data.json"
    SERVICES_DATA_PATH = "../data/services.json"

    def __init__(self):
        """
        Constructor de la clase. Carga en memoria las definiciones de ECUs y servicios
        a partir de los ficheros JSON correspondientes. Lanza un error si alguno
        de los ficheros no existe.

        :raises FileNotFoundError: Si no se encuentran los ficheros JSON necesarios.
        """
        if not os.path.isfile(Parser.ECU_DATA_PATH):
            raise FileNotFoundError(f"Missing ECU file: {Parser.ECU_DATA_PATH}")
        if not os.path.isfile(Parser.SERVICES_DATA_PATH):
            raise FileNotFoundError(f"Missing services file: {Parser.SERVICES_DATA_PATH}")

        with open(Parser.ECU_DATA_PATH, "r") as f:
            self.ecus = json.load(f)["ecus"]
        with open(Parser.SERVICES_DATA_PATH, "r") as f:
            self.services = json.load(f)["services"]  

    def data_by_key(self, ecu_definitions: List[Dict[str, Any]], key: str) -> Optional[Dict[str, Any]]:
        """
        Devuelve la definición de una ECU a partir de su nombre.

        :param ecu_definitions: Lista de definiciones de ECUs.
        :type ecu_definitions: List[Dict[str, Any]]

        :param key: Nombre de la ECU a buscar.
        :type key: str

        :return: Diccionario con la definición de la ECU si se encuentra, None en caso contrario.
        :rtype: Optional[Dict[str, Any]]
        """
        # Check if the key is in the ecu_definitions
        for ecu_definition in self.ecus:
            if ecu_definition["name"] == key:
                return ecu_definition
        
        # Si no se encuentra la clave en el diccionario se devuelve None
        return None
    
    def ecu1_to_ecu2(self, ecu_src: str, ecu_dst: str) -> Dict[str, Any]:
        """
        Obtiene los datos de red y puertos necesarios para la comunicación unicast
        entre dos ECUs específicas.

        :param ecu_src: Nombre de la ECU origen.
        :type ecu_src: str

        :param ecu_dst: Nombre de la ECU destino.
        :type ecu_dst: str

        :return: Diccionario con direcciones MAC, IP, puertos UDP/SOMEIP y VLAN.
        :rtype: Dict[str, Any]

        :raises None: Devuelve None si alguna de las ECUs no se encuentra.
        """
        # Check if the ecu_src and ecu_dst are in the ecu_definitions
        ecu_src_data = self.data_by_key(self.ecus, ecu_src)
        ecu_dst_data = self.data_by_key(self.ecus, ecu_dst)

        # If the ecu_src or ecu_dst is not found, return None
        if not ecu_src_data or not ecu_dst_data:
            return None
        
        # Return the data
        return {
            "mac_address": ecu_src_data["mac_address"],
            "mac_dst": ecu_dst_data["mac_address"],
            "ip_src": ecu_src_data["ip"],
            "ip_dst": ecu_dst_data["ip"],
            "udp_src": ecu_src_data["sd_port_src"],
            "udp_dst": ecu_dst_data["sd_port_dst"],
            "someip_port_src": ecu_src_data["someip_port_src"],
            "someip_port_dst": ecu_dst_data["someip_port_dst"],
            "vlan": ecu_src_data["vlan"]
        }
    
    def multicast(self, ecu1: str) -> Dict[str, Any]:
        """
        Obtiene los datos de red necesarios para realizar una comunicación multicast
        desde una ECU específica.

        :param ecu1: Nombre de la ECU que emite el mensaje multicast.
        :type ecu1: str

        :return: Diccionario con direcciones MAC, IP, puertos y opciones de configuración.
        :rtype: Dict[str, Any]

        :raises None: Devuelve None si la ECU no se encuentra.
        """
        # Check if the ecu1 is in the ecu_definitions
        ecu1_data = self.data_by_key(self.ecus, ecu1)

        # If the ecu1 is not found, return None
        if not ecu1_data:
            return None
        
        # Devuelve los datos origen/destino para un envíon multicast
        return {
            "mac_address": ecu1_data["mac_address"],
            "MAC_1500_MULTICAST": ecu1_data["MAC_1500_MULTICAST"],
            "ip": ecu1_data["ip"],
            "IP_1500_MULTICAST": ecu1_data["IP_1500_MULTICAST"],
            "sd_port_src": ecu1_data["sd_port_src"],
            "sd_port_dst": ecu1_data["sd_port_dst"],
            "vlan": ecu1_data["vlan"],
            "option_sdport": ecu1_data["option_sdport"],
            "option_sdprot": ecu1_data["option_sdprot"],
        }

    def get_service_data(self, service_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene la definición completa de un servicio/método SOME/IP a partir de su ID.

        El método busca en la estructura de servicios y devuelve una copia del método 
        junto con la información de configuración de tipo FIND, OFFER, SUBSCRIBE y SOME/IP.

        :param service_id: Identificador del método de servicio.
        :type service_id: int

        :return: Diccionario con la estructura del servicio, o None si no se encuentra.
        :rtype: Optional[Dict[str, Any]]
        """
        for service in self.services:
            for method in service.get("methods", []):
                if method.get("ID") == service_id:
                    return {
                        "service_name": service.get("name"),
                        "method_name": method.get("name"),
                        "id": method.get("ID"),
                        "FIND": {
                            "Type": method.get("FIND", {}).get("Type"),
                            "Major_Version": method.get("FIND", {}).get("Major_Version"),
                            "Minor_Version": method.get("FIND", {}).get("Minor_Version")
                        },
                        "OFFER": {
                            "Type": method.get("OFFER", {}).get("Type"),
                            "Major_Version": method.get("OFFER", {}).get("Major_Version"),
                            "Minor_Version": method.get("OFFER", {}).get("Minor_Version")
                        },
                        "SUBSCRIBE": {
                            "Type": method.get("SUBSCRIBE", {}).get("Type"),
                            "EvengroupID": method.get("SUBSCRIBE", {}).get("EvengroupID")
                        },
                        "SOMEIP": {
                            "ServID": method.get("SOMEIP", {}).get("ServID"),
                            "SubID": method.get("SOMEIP", {}).get("SubID"),
                            "MethodID": method.get("SOMEIP", {}).get("MethodID"),
                            "MessageType": method.get("SOMEIP", {}).get("MessageType"),
                            "Cycle": method.get("SOMEIP", {}).get("Cycle"),
                            "Payload": method.get("SOMEIP", {}).get("Payload")
                        },
                        "Rep_Phase_Time": method.get("Rep_Phase_Time"),
                        "Rep_Phase_Cycle": method.get("Rep_Phase_Cycle"),
                        "Response": method.get("Response"),
                        "EcuOrigen": method.get("EcuOrigen"),
                    }
        return None
    
    def get_ecus(self) -> List[str]:
        """
        Devuelve una lista con los nombres de todas las ECUs definidas en el sistema.

        :return: Lista con nombres de ECUs.
        :rtype: List[str]
        """
        return [ecu["name"] for ecu in self.ecus]
