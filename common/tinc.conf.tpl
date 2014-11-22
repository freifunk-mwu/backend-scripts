Name = ${iam}
PrivateKeyFile = /etc/tinc/${interface}/rsa_key.priv
Mode = Switch
PingTimeout = 30
Port = 10655
Hostnames = yes
GraphDumpFile = /etc/tinc/${interface}/topo.dot
Interface = ${interface}

${connects}
