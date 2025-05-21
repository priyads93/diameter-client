export SERVER_CERT_DIR=<Location of server cert/key>
export CLIENT_WORK_DIR="$HOME/diameter-client-certs"

# Step 2: Create the client cert directory
mkdir -p "$CLIENT_WORK_DIR"
cd "$CLIENT_WORK_DIR"

# Step 3: Copy server cert and key into client cert directory
cp "$SERVER_CERT_DIR/<Server Cert file name>" "$CLIENT_WORK_DIR/cert.crt"
cp "$SERVER_CERT_DIR/<Server Key file name>" "$CLIENT_WORK_DIR/"

# Step 4: Generate client private key
openssl genpkey -algorithm RSA -out client.key -pkeyopt rsa_keygen_bits:2048

# Step 5: Create CSR (Certificate Signing Request) for client
openssl req -new -key client.key -out client.csr -subj "/CN=diameter-client"

# Step 6: Sign the client CSR using the copied server cert/key
openssl x509 -req -in client.csr \
  -CA cert.crt -CAkey <Server Key File Name> -CAcreateserial \
  -out client.crt -days 365 -sha256

# Step 7: (Optional) Verify client cert is trusted by server cert
openssl verify -CAfile cert.crt client.crt



