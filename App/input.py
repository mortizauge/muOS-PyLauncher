import struct
import time

code = 0
codeName = ""
value = 0

# Mapeo de códigos a nombres
mapping = {
    304: "A",
    305: "B",
    306: "Y",
    307: "X",
    308: "L1",
    309: "R1",
    314: "L2",
    315: "R2",
    17: "DY",
    16: "DX",
    310: "SELECT",
    311: "START",
    312: "MENUF",
    114: "V+",
    115: "V-",
}

# Lista de eventos simulados
fake_events = []

def simulate_key_press(key_name):
    """Simula un pulsado manual de una tecla (press + release)"""
    global fake_events
    if key_name in mapping.values():
        fake_events.append((key_name, 1))   # Presionado
        fake_events.append((key_name, -1))  # Soltado

def check():
    """Lee el siguiente evento real o simulado"""
    global code, codeName, value

    if fake_events:
        keyName, keyValue = fake_events.pop(0)
        codeName = keyName
        value = keyValue
        return

    with open("/dev/input/event1", "rb") as f:
        while True:
            event = f.read(24)
            if event:
                (tv_sec, tv_usec, type, kcode, kvalue) = struct.unpack('llHHI', event)
                if kvalue != 0:
                    if kvalue != 1:
                        kvalue = -1
                    code = kcode
                    codeName = mapping.get(code, str(code))
                    value = kvalue
                    return

def key(keyCodeName, keyValue=99):
    """Devuelve True si la tecla coincide"""
    global code, codeName, value
    if codeName == keyCodeName:
        if keyValue != 99:
            return value == keyValue
        return True
    return False

def reset_input():
    """Limpia el estado del input actual"""
    global codeName, value
    codeName = ""
    value = 0
