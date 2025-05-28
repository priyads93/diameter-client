# Fast API Hello World Example

This project demonstrates a simple fast api setup. The api acts as the client sends a request to the free diameter server and receives a response.

## Prerequisites

- Python 3.7 or higher
- pip version 9.0.1 or higher
- fastapi[standard]
- dotenv

To install the required Python packages, run:

```bash
pip install -r /path/to/requirements.txt

```

## Setup and Running the Application

1. Generate the client certificates by following the steps mentioned in generate_certs.sh file

2. Create the .env file and add the following values in it

```
HOST=<server identity>
PORT=5868
CA_CERT=<path to server crt file>
CLIENT_CERT=<path to client cert file>
CLIENT_KEY=<path to client key file>
GY_APPLICATION_ID <Gy Application Id. Sample: 16777238>
```

# Run the Client

Once the server is running, run the client to send a request to the server:
fastapi dev main.py

Once the client is up and running, we can send the post request via postman,

1. /send_cer_message route:

```Sample Input
{
    "origin_host": "Client domain mentioned in server config",
    "origin_realm": "Realm value mentioned in server config",
    "host_ip_address": [
        "127.0.0.1"
    ],
    "vendor_id": 12346,
    "product_name": "PyClient",
    "origin_state_id": 1,
    "hop_by_hop_id": 12345678,
    "end_to_end_id": 87654321,
    "command_code": 257,
    "application_id": 0
}
```

The client will send a CER and get the CEA as response back from server

When the client successfully connects to the server, the output should be:

```
{
    "response": {
        "header": {
            "version": 1,
            "length": 196,
            "length_header": 20,
            "command_flags": 0,
            "command_code": 257,
            "application_id": 0,
            "hop_by_hop_identifier": 12345678,
            "end_to_end_identifier": 87654321
        },
        "_avps": [],
        "_Message__find_cache": {},
        "_additional_avps": [],
        "host_ip_address": [
            [
                1,
                "172.17.0.2"
            ]
        ],
        "supported_vendor_id": [
            5535,
            10415
        ],
        "auth_application_id": [
            0,
            4294967295
        ],
        "inband_security_id": [],
        "acct_application_id": [],
        "vendor_specific_application_id": [],
        "result_code": 2001,
        "origin_host": <server identity>,
        "origin_realm": <server realm>,
        "origin_state_id": 1747807918,
        "vendor_id": 0,
        "product_name": "freeDiameter",
        "firmware_revision": 10600
    }
}```



2. /send_ccr_message

```Sample Input:
{
    "origin_host": "Client domain mentioned in server config",
    "origin_realm": "Realm value mentioned in server config",
    "host_ip_address": [
        "127.0.0.1"
    ],
    "cc_request_type": 1,
    "cc_request_number": 1,
    "session_id": "1234",
    "destination_realm": "test",
    "hop_by_hop_id": 12345678,
    "end_to_end_id": 87654321,
    "service_context_id": "745",
    "auth_application_id": 4,
    "application_id": 0
}
```