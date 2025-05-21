from typing import Union
from contextlib import asynccontextmanager
from diameter.message.commands import CapabilitiesExchangeRequest, CapabilitiesExchangeAnswer, CreditControlRequest
from fastapi import FastAPI
from diameter.message import Message
from client_config.client_2 import create_ssl_socket,send_test_message
from pydantic import BaseModel

class cerMessage(BaseModel):
    origin_host: str
    origin_realm: str
    host_ip_address: list[str]
    vendor_id: int
    product_name: str
    origin_state_id: int
    hop_by_hop_id: int
    end_to_end_id: int
    command_code: int
    application_id: int
    
class ccrMessage(BaseModel):
    origin_host: str
    origin_realm: str
    host_ip_address: list[str]
    hop_by_hop_id: int
    end_to_end_id: int
    service_context_id: str
    auth_application_id: int
    cc_request_type: int
    cc_request_number: int
    session_id: str
    destination_realm: str
    application_id: int
    


ssl_sock = None  # Define ssl_sock as a global variable
def build_cer(message: Union[None, cerMessage] = None) -> bytes:
    cer = CapabilitiesExchangeRequest()
    """Build a CER message with the given parameters"""
    # If message is None, use default values
    if message is None:
        cer.origin_host = b'client.localdomain'
        cer.origin_realm = b'testrealm'
        cer.host_ip_address = ['127.0.0.1']    
        cer.vendor_id = 12345
        cer.product_name = 'PyDiameter'
        cer.origin_state_id = 1
        cer.hop_by_hop_id = 12345678
        cer.end_to_end_id = 87654321
        cer.command_code = 257
        cer.application_id = 2
    else:
        # Use the provided message data
        cer.origin_host = message.origin_host.encode('utf-8')
        cer.origin_realm = message.origin_realm.encode('utf-8')
        cer.host_ip_address = message.host_ip_address
        cer.vendor_id = message.vendor_id
        cer.product_name = message.product_name
        cer.origin_state_id = message.origin_state_id
        cer.header.application_id = message.application_id    
        cer.header.command_code = message.command_code
        cer.header.hop_by_hop_identifier = message.hop_by_hop_id
        cer.header.end_to_end_identifier = message.end_to_end_id
    # Encode the message
    return cer.as_bytes()

def build_ccr(message: Union[None,ccrMessage ] = None) -> bytes:
    ccr = CreditControlRequest()
    """Build a CCR message with the given parameters"""
    # If message is None, use default values
    if message is None:
        ccr.origin_host = b'client.localdomain'
        ccr.origin_realm = b'testrealm'
        ccr.host_ip_address = ['127.0.0.1']   
        ccr.hop_by_hop_id = 12345678
        ccr.end_to_end_id = 87654321
        ccr.cc_request_type = b'INITIAL'  
        ccr.cc_request_number = 1
        ccr.session_id = 123
        ccr.destination_realm = 'testrealm'
        # Set the service context ID and auth application ID
        ccr.service_context_id = 123
        ccr.auth_application_id = 4
    else:
        # Use the provided message data
        ccr.origin_host = message.origin_host.encode('utf-8')
        ccr.origin_realm = message.origin_realm.encode('utf-8')
        ccr.host_ip_address = message.host_ip_address
        ccr.cc_request_type = message.cc_request_type  
        ccr.cc_request_number = message.cc_request_number
        ccr.session_id = message.session_id
        ccr.destination_realm = message.destination_realm.encode('utf-8')
        # Set the service context ID and auth application ID
        ccr.service_context_id = message.service_context_id
        ccr.auth_application_id = message.auth_application_id
        ccr.header.application_id = message.application_id
        ccr.header.hop_by_hop_identifier = message.hop_by_hop_id
        ccr.header.end_to_end_identifier = message.end_to_end_id
    # Encode the message
    print(ccr.as_bytes())
    return ccr.as_bytes()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Method that gets called upon app initialization to initialize ssl connection & close the connection on exit"""
    global ssl_sock  # Declare ssl_sock as global to modify it
    ssl_sock = create_ssl_socket()
    print("SSL socket created")
    yield
    ssl_sock.close()
    
app = FastAPI(lifespan=lifespan)

@app.post("/send_cer_message")
async def send_cer_message(cer: cerMessage):
    # Build the CER message using the provided data
    message = build_cer(cer)
    
    # Send the message
    response = send_test_message(ssl_sock, message)
    
    # Decode the response
    cea = Message.from_bytes(response)
    
    return {"response": cea}

@app.post("/send_ccr_message")
async def send_ccr_message(ccr: ccrMessage):
    # Build the CER message using the provided data
    message = build_ccr(ccr)
    
    # Send the message
    response = send_test_message(ssl_sock, message)
    
    # Decode the response
    cea = Message.from_bytes(response)
    
    return {"response": cea}

