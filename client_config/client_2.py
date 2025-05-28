import socket
import ssl
import struct
from dotenv import load_dotenv
import os
load_dotenv() 


# Configuration: Replace with your FreeDiameter's host and SSL port
HOST = os.getenv("HOST")
PORT = os.getenv("PORT")  # SSL/TLS port for FreeDiameter
CA_CERT = os.getenv("CA_CERT")  # Path to CA certificate
CERT = os.getenv('CLIENT_CERT')  # Path to client certificate (if needed)
KEY = os.getenv('CLIENT_KEY') # Path to client private key (if needed)

def create_ssl_socket():
    
    print(HOST,PORT)
    # Create SSL context for client
    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    context.load_verify_locations(CA_CERT)
    
    # Optional: use client certificate (if FreeDiameter expects client authentication)
    context.load_cert_chain(certfile=CERT, keyfile=KEY)
    
    # Create and wrap the socket
    raw_sock = socket.create_connection((HOST, PORT))
    ssl_sock = context.wrap_socket(raw_sock, server_hostname=HOST)
    
    return ssl_sock

def encode_avp(avp_code, flags, vendor_id, data):
    """Encode a Diameter AVP"""
    avp_header = struct.pack("!I", avp_code)
    avp_flags = flags
    avp_data = data

    # Add Vendor-ID if Vendor-Specific flag is set
    if flags & 0x80:  # Vendor-Specific flag
        avp_data = struct.pack("!I", vendor_id) + avp_data

    length = 8 + len(avp_data)  # Header is 8 bytes, then data
    if flags & 0x80:
        length += 4  # +4 for Vendor-ID

    # Pad to 4-byte boundary
    padding = (4 - (length % 4)) % 4
    avp_data += b'\x00' * padding
    length += padding

    avp_header += struct.pack("!B", avp_flags)
    avp_header += struct.pack("!I", length)[1:]  # Only last 3 bytes
    avp = avp_header + avp_data
    return avp



def send_test_message(sock,message):
    # NOTE: Diameter messages are binary-encoded!
    # Below is a mock CER-like message with incorrect data — just for connection test
    # Real Diameter messages must be crafted per RFC 6733
    
    cer = message
    print("Sending CER...")
    sock.sendall(cer)

    print("Waiting for CEA...")    
    
    try:
        response = sock.recv(4096)
        print(f"Received {len(response)} bytes")
        return response
        
    except ssl.SSLEOFError as e:
        print(f"SSL error: {e}")
    

def main():
    ssl_sock = create_ssl_socket()
    send_test_message(ssl_sock)

if __name__ == '__main__':
    main()
