"""
All-in-one sender/receiver for transferring a file between two machines
over a VPN-tunneled or otherwise private connection.

- Encrypts the payload with a shared passphrase (AES via Fernet) so the
  data itself is protected even on a plain TCP socket.
- Sender connects out, pushes the file, waits for an acknowledgment
  (with a SHA-256 checksum) before exiting.
- Receiver listens, decrypts, verifies, saves the file, and sends
  the acknowledgment back.

Usage: just run `python transfer.py` on both machines and follow prompts.

Requires: pip install cryptography
"""

import socket
import hashlib
import base64
import getpass
import sys
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

PORT = 9999
SALT = b"transfer-tool-fixed-salt"  # fixed salt is fine here since the passphrase itself is the real secret


def derive_key(passphrase: str) -> bytes:
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=SALT, iterations=390000)
    return base64.urlsafe_b64encode(kdf.derive(passphrase.encode()))


def get_local_ips():
    ips = set()
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ips.add(s.getsockname()[0])
        s.close()
    except Exception:
        pass
    try:
        ips.add(socket.gethostbyname(socket.gethostname()))
    except Exception:
        pass
    return ips or {"unknown"}


def recv_all(conn, size):
    chunks = []
    remaining = size
    while remaining > 0:
        chunk = conn.recv(min(65536, remaining))
        if not chunk:
            raise ConnectionError("Connection closed before all data received")
        chunks.append(chunk)
        remaining -= len(chunk)
    return b"".join(chunks)


def run_receiver(fernet: Fernet):
    save_path = input("Save incoming file as [received_data.bin]: ").strip() or "received_data.bin"

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("0.0.0.0", PORT))
    server.listen(1)
    print(f"\nListening on 0.0.0.0:{PORT} ... (Ctrl+C to stop)\n")

    conn, addr = server.accept()
    print(f"✓ Connection from {addr}")

    try:
        size_bytes = recv_all(conn, 8)
        size = int.from_bytes(size_bytes, "big")
        print(f"→ Incoming {size} bytes (encrypted)...")

        encrypted = recv_all(conn, size)
        data = fernet.decrypt(encrypted)
        checksum = hashlib.sha256(data).hexdigest()

        with open(save_path, "wb") as f:
            f.write(data)

        print(f"✓ Decrypted and saved to '{save_path}' ({len(data)} bytes)")
        print(f"✓ sha256={checksum}")

        ack = f"ok:{len(data)}:{checksum}".encode()
        conn.sendall(len(ack).to_bytes(8, "big"))
        conn.sendall(ack)
        print("✓ Acknowledgment sent")

    except Exception as e:
        print(f"✗ Error: {e}")
        try:
            err = f"error:{e}".encode()
            conn.sendall(len(err).to_bytes(8, "big"))
            conn.sendall(err)
        except Exception:
            pass
    finally:
        conn.close()
        server.close()


def run_sender(fernet: Fernet):
    dest_ip = input("Destination IP: ").strip()
    file_path = input("File to send: ").strip()

    try:
        with open(file_path, "rb") as f:
            data = f.read()
    except FileNotFoundError:
        print(f"✗ File not found: {file_path}")
        return

    local_checksum = hashlib.sha256(data).hexdigest()
    encrypted = fernet.encrypt(data)

    print(f"\n→ Connecting to {dest_ip}:{PORT} ...")
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.settimeout(30)

    try:
        client.connect((dest_ip, PORT))
        print(f"→ Sending {len(data)} bytes ({len(encrypted)} bytes encrypted)...")

        client.sendall(len(encrypted).to_bytes(8, "big"))
        client.sendall(encrypted)

        ack_size = int.from_bytes(recv_all(client, 8), "big")
        ack = recv_all(client, ack_size).decode()

        if ack.startswith("ok:"):
            _, remote_size, remote_checksum = ack.split(":", 2)
            if remote_checksum == local_checksum:
                print(f"✓ Delivered and verified ({remote_size} bytes, sha256 match)")
            else:
                print("✗ WARNING: checksum mismatch — data may have been corrupted!")
        else:
            print(f"✗ Receiver reported an error: {ack}")

    except socket.timeout:
        print("✗ Connection timed out — check the IP, port, and that the receiver is running/reachable (VPN connected?)")
    except ConnectionRefusedError:
        print("✗ Connection refused — receiver may not be running, or a firewall is blocking the port")
    except Exception as e:
        print(f"✗ Failed: {e}")
    finally:
        client.close()


def main():
    print("=" * 50)
    print("  Simple encrypted file transfer")
    print("=" * 50)

    local_ips = get_local_ips()
    print(f"This machine's IP address(es): {', '.join(local_ips)}")
    print("(Share this with the sender if you're running 'rec')\n")

    passphrase = getpass.getpass("Shared passphrase (must match on both machines): ")
    fernet = Fernet(derive_key(passphrase))

    mode = input("\nType 'send' or 'rec': ").strip().lower()

    if mode == "rec":
        run_receiver(fernet)
    elif mode == "send":
        run_sender(fernet)
    else:
        print("Unrecognized option. Please type 'send' or 'rec'.")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted.")
