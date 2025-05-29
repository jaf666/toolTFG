import struct
from enum import IntEnum
from typing import Dict, Any

# Enumeraciones definidas en el .def file
# En este .def file en concreto, se encuentran definidos los distintos tipos de datos, así
# como su representación.

# ValueState es de tipo uint8, por lo que será representado a través de 8 bits, o lo que es lo 
# mismo, 2 caracteres hexadecimales. Esto es importante, por que si se quiere pasar la payload
# como un binario al mensaje SOME/IP se deberá devolver correctamente la información en formato
# cadena hexadecimal. Scapy calcula automáticamente el len del payload.

class ValueState(IntEnum):
    UNAVAILABLE = 0
    VALID = 1
    INVALID = 2

class SpeedSignT(IntEnum):
    NULL_SPEED = 0
    FORWARD = 1
    REVERSE = 2
    UNAVAILABLE = 3

class SpeedSupposedStateT(IntEnum):
    UNAVAILABLE = 0
    STANDSTILL = 1
    MOVING = 2

class VehicleDynamicsPlugin:
    def __init__(self):
        self.vehicle_speed = {
            "vehicleSpeedValueState": ValueState.VALID,
            "vehicleSpeed": 0.0,
            "vehicleSpeedSignValueState": ValueState.VALID,
            "vehicleSpeedSign": SpeedSignT.FORWARD,
            "vehicleLowSpeedValueState": ValueState.VALID,
            "vehicleLowSpeed": 0.0,
            "standStillSupposedValueState": ValueState.VALID,
            "standStillSupposed": SpeedSupposedStateT.STANDSTILL
        }

        self.vehicle_accel_yaw = {
            "longitudinalAccelCorrectedValueState": ValueState.VALID,
            "longitudinalAccelCorrected": 0.0,
            "transversalAccelCorrectedValueState": ValueState.VALID,
            "transversalAccelCorrected": 0.0,
            "yawRateCorrectedValueState": ValueState.VALID,
            "yawRateCorrected": 0.0,
            "longitudinalAccelRawValueState": ValueState.VALID,
            "longitudinalAccelRaw": 0.0,
            "transversalAccelRawValueState": ValueState.VALID,
            "transversalAccelRaw": 0.0,
            "yawRateRawValueState": ValueState.VALID,
            "yawRateRaw": 0.0
        }

        self.vehicle_speed_body = {
            "vehicleSpeedBodyValueState": ValueState.VALID,
            "vehicleSpeedBody": 0.0
        }

        self._speed_increment = 1.0

    def increment_speed(self):
        """Incrementa la velocidad simulada."""
        self.vehicle_speed["vehicleSpeed"] += self._speed_increment
        self.vehicle_speed["vehicleLowSpeed"] += self._speed_increment
        self.vehicle_speed_body["vehicleSpeedBody"] += self._speed_increment

    def set_speed(self, value: float):
        self.vehicle_speed["vehicleSpeed"] = value
        self.vehicle_speed["vehicleLowSpeed"] = value
        self.vehicle_speed_body["vehicleSpeedBody"] = value

    def set_acceleration(self, longitudinal: float, transversal: float):
        self.vehicle_accel_yaw["longitudinalAccelCorrected"] = longitudinal
        self.vehicle_accel_yaw["transversalAccelCorrected"] = transversal
        self.vehicle_accel_yaw["longitudinalAccelRaw"] = longitudinal
        self.vehicle_accel_yaw["transversalAccelRaw"] = transversal

    def get_payload_vehicle_speed(self) -> bytes:
        """
        Función que devuelve una estructura empaquetada de bytes que establecen los diferentes campos
        del evento vehicle_speed. Para este evento se tienen valores de 1 byte determinado por los
        diferentes tipos enumerados definidos y dos float, que ocupan 4 bytes (float32).
        Esto, se define al comienzo para determinar cómo se van a empaquetar los bytes.

        :return: Devuelve el pack de bytes formado para ser introducido en la payload.
        :rtype: bytes
        """
        return struct.pack(
            "<BfBBBfBB",
            int(self.vehicle_speed["vehicleSpeedValueState"]),       # B -> int
            float(self.vehicle_speed["vehicleSpeed"]),               # f -> float
            int(self.vehicle_speed["vehicleSpeedSignValueState"]),   # B -> int
            int(self.vehicle_speed["vehicleSpeedSign"]),             # B -> int
            int(self.vehicle_speed["vehicleLowSpeedValueState"]),    # Aquí sospecho error (debería ser int, no float)
            float(self.vehicle_speed["vehicleLowSpeed"]),            # f -> float
            int(self.vehicle_speed["standStillSupposedValueState"]), # B -> int
            int(self.vehicle_speed["standStillSupposed"]),           # B -> int
        )


    def get_payload_accel_and_yaw(self) -> bytes:
        """
        Función que devuelve una estructura empaquetada de bytes que establecen los diferentes campos
        del evento vehicle_accel_yaw.

        :return: Devuelve el pack de bytes formado para ser introducido en la payload.
        :rtype: bytes
        """
        return struct.pack(
            "<BfBfBfBfBfBf",
            self.vehicle_accel_yaw["longitudinalAccelCorrectedValueState"],
            self.vehicle_accel_yaw["longitudinalAccelCorrected"],
            self.vehicle_accel_yaw["transversalAccelCorrectedValueState"],
            self.vehicle_accel_yaw["transversalAccelCorrected"],
            self.vehicle_accel_yaw["yawRateCorrectedValueState"],
            self.vehicle_accel_yaw["yawRateCorrected"],
            self.vehicle_accel_yaw["longitudinalAccelRawValueState"],
            self.vehicle_accel_yaw["longitudinalAccelRaw"],
            self.vehicle_accel_yaw["transversalAccelRawValueState"],
            self.vehicle_accel_yaw["transversalAccelRaw"],
            self.vehicle_accel_yaw["yawRateRawValueState"],
            self.vehicle_accel_yaw["yawRateRaw"],
        )

    def get_payload_speed_body(self) -> bytes:
        """
        Función que devuelve una estructura empaquetada de bytes que establecen los diferentes campos
        del evento vehicle_speed_body.

        :return: Devuelve el pack de bytes formado para ser introducido en la payload.
        :rtype: bytes
        """
        return struct.pack(
            "<Bf",
            self.vehicle_speed_body["vehicleSpeedBodyValueState"],
            self.vehicle_speed_body["vehicleSpeedBody"]
        )

    def get_payload(self, event: str) -> bytes:
        """
        Devuelve el payload codificado según el evento.
        """
        if event == "VehicleSpeed":
            return self.get_payload_vehicle_speed()
        elif event == "VehicleAccelAndYaw":
            return self.get_payload_accel_and_yaw()
        elif event == "VehicleSpeedBody":
            return self.get_payload_speed_body()
        else:
            raise ValueError(f"Evento no reconocido: {event}")