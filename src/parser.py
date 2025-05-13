import os, json
from typing import List, Optional, Dict, Any


class Parser():
    """
    This class is used to parse ECU definition from a json
    and services packet data from a json
    """
    ECU_DATA_PATH = "../data/ecu_data.json"
    SERVICES_DATA_PATH = "../data/services.json"

    def __init__(self):
        """
        This method is used to initialize the class
        """
        #if not os.path.isfile(Parser.ECU_DATA_PATH):
        #    raise FileNotFoundError(f"Missing ECU file: {Parser.ECU_DATA_PATH}")
        #if not os.path.isfile(Parser.SERVICES_DATA_PATH):
        #    raise FileNotFoundError(f"Missing services file: {Parser.SERVICES_DATA_PATH}")

        with open(Parser.ECU_DATA_PATH, "r") as f:
            self.ecus = json.load(f)["ecus"]
        with open(Parser.SERVICES_DATA_PATH, "r") as f:
            self.services = json.load(f)["services"]  

    def data_by_key(self, ecu_definitions: List[Dict[str, Any]], key: str) -> Optional[Dict[str, Any]]:
        """
        This method is used to get the data by name from the ecu definitions given by get_ecu_definition
        """
        # Check if the key is in the ecu_definitions
        for ecu_definition in self.ecus:
            if ecu_definition["name"] == key:
                return ecu_definition
        
        # If the key is not found, return None
        return None
    
    def ecu1_to_ecu2(self, ecu_src: str, ecu_dst: str) -> Dict[str, Any]:
        """
        This method is used to get the origin and destination data from the ecu definitions
        in order to send the packet
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
            "vlan": ecu_src_data["vlan"]
        }
    
    def multicast(self, ecu1: str) -> Dict[str, Any]:
        """
        This method is used to get the multicast data from the ecu definitions
        in order to send the packet
        """
        # Check if the ecu1 is in the ecu_definitions
        ecu1_data = self.data_by_key(self.ecus, ecu1)

        # If the ecu1 is not found, return None
        if not ecu1_data:
            return None
        
        # Return the data
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
        This method is used to get the service data from the services definitions
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