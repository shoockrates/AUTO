# vm_sender.py
import socket

DEST_IP = 'x.x.x.x'  # destination's public IP
PORT = 9999

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.settimeout(10)

try:
    client.connect((DEST_IP, PORT))
    print(f"✓ Connected to {DEST_IP}:{PORT}")

    client.sendall(b"hello")
    print("✓ Sent: hello")

    response = client.recv(1024)
    print(f"✓ Destination replied: {response.decode()}")

except socket.timeout:
    print("✗ Connection timed out — VM likely has no direct outbound path to destination (blocked or routed only through VPN)")
except ConnectionRefusedError:
    print("✗ Connection refused — port may be closed on destination, or a firewall is blocking it")
except Exception as e:
    print(f"✗ Failed: {e}")
finally:
    client.close()
