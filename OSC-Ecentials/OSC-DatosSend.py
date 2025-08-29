import socket
import time
import psutil
import datetime
from pythonosc import osc_message_builder
from pythonosc import udp_client

# Configuración de red
BROADCAST_IP = "192.168.1.102"
PORT = 9000

# Crear socket UDP configurado para broadcast
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

# Crear cliente OSC usando el socket configurado
client = udp_client.UDPClient(BROADCAST_IP, PORT, sock)

def get_cpu_temperature():
    """Obtiene la temperatura de la CPU (solo Linux)"""
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            temp = int(f.read()) / 1000.0
            return temp
    except:
        return 0.0

def get_system_info():
    """Recolecta información del sistema"""
    # Hora actual
    now = datetime.datetime.now()
    
    # Uso de CPU
    cpu_percent = psutil.cpu_percent(interval=0.1)
    
    # Uso de memoria
    memory = psutil.virtual_memory()
    memory_percent = memory.percent
    
    # Temperatura (solo funciona en Linux)
    cpu_temp = get_cpu_temperature()
    
    # Disco duro
    disk = psutil.disk_usage('/')
    disk_percent = disk.percent
    
    return {
        "hora": now.strftime("%H:%M:%S"),
        "timestamp": time.time(),
        "cpu_uso": cpu_percent,
        "memoria_uso": memory_percent,
        "cpu_temperatura": cpu_temp,
        "disco_uso": disk_percent
    }

try:
    print("Enviando datos del sistema por OSC... (Ctrl+C para detener)")
    
    while True:
        # Obtener información del sistema
        system_info = get_system_info()
        
        # Enviar cada dato a su propia dirección OSC
        # Hora
        msg_hora = osc_message_builder.OscMessageBuilder(address="/system/hora")
        msg_hora.add_arg(system_info["hora"])
        client.send(msg_hora.build())
        
        # Timestamp
        msg_ts = osc_message_builder.OscMessageBuilder(address="/system/timestamp")
        msg_ts.add_arg(system_info["timestamp"])
        client.send(msg_ts.build())
        
        # Uso de CPU
        msg_cpu = osc_message_builder.OscMessageBuilder(address="/system/cpu")
        msg_cpu.add_arg(system_info["cpu_uso"])
        client.send(msg_cpu.build())
        
        # Uso de memoria
        msg_mem = osc_message_builder.OscMessageBuilder(address="/system/memoria")
        msg_mem.add_arg(system_info["memoria_uso"])
        client.send(msg_mem.build())
        
        # Temperatura CPU
        msg_temp = osc_message_builder.OscMessageBuilder(address="/system/temperatura")
        msg_temp.add_arg(system_info["cpu_temperatura"])
        client.send(msg_temp.build())
        
        # Uso de disco
        msg_disk = osc_message_builder.OscMessageBuilder(address="/system/disco")
        msg_disk.add_arg(system_info["disco_uso"])
        client.send(msg_disk.build())
        
        print(f"Datos enviados a {BROADCAST_IP}:{PORT} - {system_info['hora']}")
        
        # Esperar 2 segundos
        time.sleep(2)

except KeyboardInterrupt:
    print("\nInterrupción recibida, cerrando...")
finally:
    sock.close()
