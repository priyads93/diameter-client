from typing import Union
from contextlib import asynccontextmanager
from diameter.message.commands import CapabilitiesExchangeRequest, CapabilitiesExchangeAnswer, CreditControlRequest, DisconnectPeerRequest
from fastapi import FastAPI
from diameter.message import Message
from client_config.client_2 import create_ssl_socket,send_test_message
from pydantic import BaseModel
from diameter.message import Avp
from diameter.message.constants import *
from typing import Optional
from diameter.message.avp.dictionary import AVP_DICTIONARY
from dotenv import load_dotenv
import os
load_dotenv() 

# AVP Codes
AVP_SUBSCRIPTION_ID = 443
AVP_SUBSCRIPTION_ID_TYPE = 450
AVP_SUBSCRIPTION_ID_DATA = 444
GY_APPLICATION_ID = os.getenv("GY_APPLICATION_ID")

# Vendor ID for 3GPP
VENDOR_3GPP = 0

class SubscriptionId(BaseModel):
    type: int 
    data: str 
    
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
    requested_action: int
    subscription_id: Optional[SubscriptionId]
class dprMessage(BaseModel):
    origin_host: str
    origin_realm: str
    disconnect_cause: int
    hop_by_hop_id: int
    end_to_end_id: int    
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
        cer.header.hop_by_hop_id = 12345678
        cer.header.end_to_end_id = 87654321
        cer.header.command_code = 257
        cer.header.application_id = 2
    else:
        # Use the provided message data
        cer.origin_host = message.origin_host.encode('utf-8')
        cer.origin_realm = message.origin_realm.encode('utf-8')
        cer.host_ip_address = message.host_ip_address
        cer.vendor_id = message.vendor_id
        cer.product_name = message.product_name
        cer.origin_state_id = message.origin_state_id
        cer.auth_application_id = int(GY_APPLICATION_ID)
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
        ccr.header.hop_by_hop_identifier = 12345678
        ccr.header.end_to_end_identifier = 87654321
        ccr.cc_request_type = b'INITIAL'  
        ccr.cc_request_number = 1
        ccr.session_id = 123
        ccr.destination_realm = 'testrealm'
        # Set the service context ID and auth application ID
        ccr.service_context_id = 123
        ccr.auth_application_id = 4
        ccr.requested_action = 0
    else:
        # Use the provided message data
        ccr.origin_host = message.origin_host.encode('utf-8')
        ccr.origin_realm = message.origin_realm.encode('utf-8')
        ccr.cc_request_type = message.cc_request_type  
        ccr.cc_request_number = message.cc_request_number
        ccr.session_id = message.session_id
        ccr.destination_realm = message.destination_realm.encode('utf-8')
        # Set the service context ID and auth application ID
        ccr.service_context_id = message.service_context_id
        ccr.auth_application_id = int(GY_APPLICATION_ID)
        ccr.header.application_id = message.application_id
        ccr.header.hop_by_hop_identifier = message.hop_by_hop_id
        ccr.header.end_to_end_identifier = message.end_to_end_id
        ccr.requested_action = message.requested_action
        if message.cc_request_type == 3:
            ccr.termination_cause = 1  # Example termination cause, adjust as needed
        
        if message.subscription_id:
            print('ading subscription data')
            subscription_id_avp = Avp.new(AVP_SUBSCRIPTION_ID, VENDOR_3GPP, value=[
            Avp.new(AVP_SUBSCRIPTION_ID_TYPE, VENDOR_3GPP, value=message.subscription_id.type),
            Avp.new(AVP_SUBSCRIPTION_ID_DATA, VENDOR_3GPP, value=message.subscription_id.data)
            ])
            # print(message.subscription_id.type,message.subscription_id.data)
            ccr.append_avp(subscription_id_avp)
    # Encode the message
    print(ccr.as_bytes())
    return ccr.as_bytes()

def build_dpr(message: Union[None,dprMessage ] = None) -> bytes:
    dpr = DisconnectPeerRequest()
    """Build a DPR message with the given parameters"""
    # If message is None, use default values
    if message is None:
        dpr.origin_host = b'client.localdomain'
        dpr.origin_realm = b'testrealm'
        dpr.disconnect_cause = 0  # Example disconnect cause, adjust as needed   
        dpr.header.hop_by_hop_identifier = 12345678
        dpr.header.end_to_end_identifier = 87654321
        dpr.header.application_id = 0
        dpr.header.command_code = 282  # Disconnect-Peer-Request command code
        dpr.header.is_request = True
    else:
        # Use the provided message data
        dpr.origin_host = message.origin_host.encode('utf-8')
        dpr.origin_realm = message.origin_realm.encode('utf-8')  
        dpr.disconnect_cause = message.disconnect_cause
        dpr.header.application_id = message.application_id
        dpr.header.hop_by_hop_identifier = message.hop_by_hop_id
        dpr.header.end_to_end_identifier = message.end_to_end_id
        dpr.header.command_code = 282  # Disconnect-Peer-Request command code
        dpr.header.is_request = True
        
    # Encode the message
    print(dpr.as_bytes())
    return dpr.as_bytes()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Method that gets called upon app initialization to initialize ssl connection & close the connection on exit"""
    global ssl_sock  # Declare ssl_sock as global to modify it
    ssl_sock = create_ssl_socket()
    print("SSL socket created")
    yield
    ssl_sock.close()
    print("SSL socket closed")
    
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

@app.post("/send_dpr_message")
async def send_dpr_message(dpr: dprMessage):
    # Build the DPR message using the provided data
    message = build_dpr(dpr)
    
    # Send the message
    response = send_test_message(ssl_sock, message)
    
    # Decode the response
    dpa = Message.from_bytes(response)
    
    return {"response": dpa}



