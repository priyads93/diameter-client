import logging
import datetime
import ssl
from diameter.node import Node
from diameter.node.application import SimpleThreadingApplication
from diameter.message.constants import *
from diameter.message.commands.credit_control import CreditControlRequest, RequestedServiceUnit, ServiceInformation, SmsInformation, RecipientInfo, RecipientAddress

# TLS context
tls_ctx = ssl.create_default_context(
    ssl.Purpose.SERVER_AUTH,
    cafile="/Users/priyads/diameter_certs/ca.crt"  # Path to server's cert
)

tls_ctx.load_cert_chain(
    certfile="/Users/priyads/diameter_certs/client.crt",
    keyfile="/Users/priyads/diameter_certs/client.key"
)

tls_ctx.check_hostname = False
tls_ctx.verify_mode = ssl.CERT_REQUIRED

# Configure logging
logging.basicConfig(format="%(asctime)s %(name)s %(levelname)s %(message)s")
logging.getLogger("diameter.peer.msg").setLevel(logging.DEBUG)

# Create and configure the Diameter node
node = Node("client.localdomain", "testrealm")
node.realm_name = "testrealm"
node.add_peer("aaa://macos.testnode:3868;transport=tcp;transport_protocol=tls", "testrealm", ip_addresses=["10.0.0.50"], is_persistent=True)
print(node.peers)
# Define the application
client_app = SimpleThreadingApplication(APP_DIAMETER_CREDIT_CONTROL_APPLICATION, is_auth_application=True)
node.add_application(client_app, [node.peers['macos.testnode']])



# Start the node
node.start()

# Construct a Credit Control Request (CCR)
ccr = CreditControlRequest()
ccr.session_id = node.session_generator.next_id()
ccr.origin_host = node.origin_host.encode()
ccr.origin_realm = node.realm_name.encode()
ccr.destination_realm = node.realm_name.encode()
ccr.auth_application_id = client_app.application_id
ccr.service_context_id = "32274@3gpp.org"  # SMS
ccr.cc_request_type = E_CC_REQUEST_TYPE_EVENT_REQUEST
ccr.cc_request_number = 1
ccr.user_name = "diameter"
ccr.event_timestamp = datetime.datetime.now()
ccr.requested_action = E_REQUESTED_ACTION_DIRECT_DEBITING
ccr.add_subscription_id(subscription_id_type=E_SUBSCRIPTION_ID_TYPE_END_USER_E164, subscription_id_data="41780000001")
ccr.add_multiple_services_credit_control(
    requested_service_unit=RequestedServiceUnit(cc_service_specific_units=1),
    service_identifier=1
)
ccr.service_information = ServiceInformation(
    sms_information=SmsInformation(
        data_coding_scheme=8,
        sm_message_type=E_SM_MESSAGE_TYPE_SUBMISSION,
        recipient_info=[RecipientInfo(
            recipient_address=[RecipientAddress(
                address_type=E_ADDRESS_TYPE_MSISDN,
                address_data="41780000002"
            )]
        )]
    )
)

# Send the CCR and wait for a response
client_app.wait_for_ready()
response = client_app.send_request(ccr, timeout=10)

# Handle the response
if response:
    print("Received response:", response)
else:
    print("No response received within the timeout period.")
