import socket
from pythonosc import osc_message_builder
from pythonosc import udp_client
import time

# Configuración de red
BROADCAST_IP = "192.168.1.102"
PORT = 9000

# Crear socket UDP configurado para broadcast
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

# Crear cliente OSC usando el socket configurado
client = udp_client.UDPClient(BROADCAST_IP, PORT, sock)

try:
    while True:
        # Construir mensaje OSC
        msg = osc_message_builder.OscMessageBuilder(address="/test")
        msg.add_arg("Hola desde broadcast!")
        msg = msg.build()

        # Enviar mensaje
        client.send(msg)
        print(f"Mensaje enviado a {BROADCAST_IP}:{PORT} - {msg.dgram}")

        # Esperar 2 segundos
        time.sleep(2)

except KeyboardInterrupt:
    print("\nInterrupción recibida, cerrando...")
finally:
    sock.close()
