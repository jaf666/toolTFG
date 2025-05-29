# toolTFG

Tool to simulate SOME/IP messages using Scapy.

## Features and Functionality

This tool provides the ability to simulate SOME/IP messages for testing and validation purposes, particularly in the context of intelligent antenna systems. Key features include:

*   **SOME/IP Server Simulation:** Starts a SOME/IP server, mimicking the behavior of a real ECU.
*   **Event Generation:** Sends SOME/IP events with configurable payloads.
*   **Service Discovery (SD) Support:** Implements SOME/IP Service Discovery mechanisms, including OFFER and ACK packets.
*   **Payload Generation:** Uses plugins to generate realistic payload data for different events, such as vehicle dynamics information.
*   **Configuration via JSON:** ECU and service definitions are loaded from JSON files, allowing for flexible configuration.
*   **Packet Crafting:** Constructs Ethernet, VLAN, IP, UDP, and SOME/IP packets using Scapy.
*   **VLAN Tagging:** Includes support for VLAN tagging (e.g., VLAN 1500).
*   **UDP Socket Binding:** Binds to a UDP socket to receive SubscribeEventGroup messages.

## Technology Stack

*   **Python 3.x:** The primary programming language.
*   **Scapy:** Used for packet crafting and sending/receiving.  Specifically, `scapy.all` and `scapy.contrib.automotive.someip`
*   **JSON:** Used for configuration files.

## Prerequisites

Before using this tool, ensure you have the following installed:

*   **Python 3.x:**  Download and install from [https://www.python.org/](https://www.python.org/).
*   **Scapy:** Install using `pip install scapy`.  Also install the automotive extensions: `pip install scapy[automotive]` or `pip install scapy-automotive`
*   **Network Interface:** A network interface (e.g., `eth1`) configured to send and receive SOME/IP messages. Ensure the interface name in the scripts is correct.

## Installation Instructions

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/jaf666/toolTFG.git
    cd toolTFG
    ```

2.  **Install dependencies (if not already installed):**
    ```bash
    pip install scapy
    pip install scapy[automotive]  # Or pip install scapy-automotive
    ```

## Usage Guide

1.  **Configure ECU and Service Data:**

    *   The tool uses JSON files (`data/ecu_data.json` and `data/services.json`) to define ECU configurations and service details.  Ensure these files are present and correctly configured.  Example contents might look like this:

        `data/ecu_data.json`:

        ```json
        {
            "ecus": [
                {
                    "name": "PCU_Proxy_Frontend",
                    "mac_address": "00:11:22:33:44:55",
                    "ip": "192.168.1.100",
                    "sd_port_src": 30490,
                    "sd_port_dst": 30490,
                    "someip_port_src": 30500,
                    "someip_port_dst": 30500,
                    "vlan": 1500,
                    "MAC_1500_MULTICAST": "01:00:5e:00:00:fb",
                    "IP_1500_MULTICAST": "224.224.224.245",
                    "option_sdport": 30490,
                    "option_sdprot": "11"
                },
                {
                    "name": "IVC",
                    "mac_address": "AA:BB:CC:DD:EE:FF",
                    "ip": "192.168.1.101",
                    "sd_port_src": 30490,
                    "sd_port_dst": 30490,
                    "someip_port_src": 30500,
                    "someip_port_dst": 30500,
                    "vlan": 1500,
                    "MAC_1500_MULTICAST": "01:00:5e:00:00:fb",
                    "IP_1500_MULTICAST": "224.224.224.245",
                    "option_sdport": 30490,
                    "option_sdprot": "11"
                }
            ]
        }
        ```

        `data/services.json`:

        ```json
        {
            "services": [
                {
                    "name": "VehicleDynamicsService",
                    "methods": [
                        {
                            "name": "VehicleSpeedEvent",
                            "ID": 140,
                            "FIND": {
                                "Type": "0x00",
                                "Major_Version": "0x01",
                                "Minor_Version": "0x01"
                            },
                            "OFFER": {
                                "Type": "0x01",
                                "Major_Version": "0x01",
                                "Minor_Version": "0x01"
                            },
                            "SUBSCRIBE": {
                                "Type": "0x06",
                                "EvengroupID": "0x01"
                            },
                            "SOMEIP": {
                                "ServID": 568,
                                "SubID": 32908,
                                "MethodID": 1,
                                "MessageType": "0x02",
                                "Cycle": 100,
                                "Payload": "VehicleSpeed"
                            },
                            "Rep_Phase_Time": 0,
                            "Rep_Phase_Cycle": 0,
                            "Response": null,
                            "EcuOrigen": "PCU_Proxy_Frontend"
                        }
                    ]
                }
            ]
        }
        ```

    *   Modify these files to match your specific ECU and service configurations.

2.  **Run the simulation:**

    *   Execute the `src/main.py` script:

        ```bash
        python src/main.py
        ```

    *   This will start the SOME/IP server and begin sending events. The `main()` function in `src/main.py` currently starts a server with `PCU_Proxy_Frontend` as the source ECU and `IVC` as the destination, simulating service ID 140.  You can modify these parameters in the `main()` function.

3.  **Customize Payload Data:**

    *   The `plugins/VehicleDynamicsPlugin.py` file provides example payload generation.  You can modify this plugin or create new plugins to generate different types of payload data.
    *   To use a different event or payload, modify the `craft_someip_pk` function in `src/someip.py` to use the appropriate `get_payload` method from your chosen plugin. You'll also need to update the `data/services.json` to reflect the correct payload name under the "SOMEIP"->"Payload" entry.
    *   The `VehicleDynamicsPlugin.py` contains the `ValueState`, `SpeedSignT`, and `SpeedSupposedStateT` enums, crucial for payload construction. These mirror the data types defined in a `.def` file (though the actual `.def` file is not provided in the repository).

## API Documentation

*   **`MyLab.start_someip_server(ecu_pair: Tuple[str, str], service_id: int) -> Tuple[bool, str]`:** Starts the SOME/IP server.  `ecu_pair` is a tuple containing the source and destination ECU names. `service_id` is the ID of the service to simulate.  Returns a tuple containing a boolean indicating success and a message.
*   **`MyLab.someip_server_send_event(service_id: int)`:** Sends a SOME/IP event. `service_id` is the ID of the service.
*   **`VehicleDynamicsPlugin.get_payload(event: str) -> bytes`:**  Returns the encoded payload based on the specified event name ("VehicleSpeed", "VehicleAccelAndYaw", or "VehicleSpeedBody").  Internally calls `get_payload_vehicle_speed()`, `get_payload_accel_and_yaw()`, or `get_payload_speed_body()` to construct the payload.
*   **`Parser.ecu1_to_ecu2(ecu_src: str, ecu_dst: str) -> Dict[str, Any]`:** Retrieves ECU data for source and destination ECUs.  Returns a dictionary containing MAC addresses, IP addresses, and UDP ports.
*   **`Parser.get_service_data(service_id: int) -> Optional[Dict[str, Any]]`:** Retrieves service data based on the service ID. Returns a dictionary containing service name, method name, IDs, and other relevant information.

## Contributing Guidelines

1.  Fork the repository.
2.  Create a new branch for your feature or bug fix.
3.  Implement your changes.
4.  Submit a pull request with a clear description of your changes.

## License Information

No license is specified in the repository.  All rights are reserved unless otherwise stated.

## Contact/Support Information

For questions or support, please contact jaf666 through GitHub.