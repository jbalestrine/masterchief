from pathlib import Path
p=Path('data/anope_conf/services.example.conf')
s=p.read_text()
# Replace uplink host, port, password for first uplink block
s=s.replace('host = "127.0.0.1"','host = "inspircd"',1)
s=s.replace('port = 7000','port = 6669',1)
s=s.replace('password = "mypassword"','password = "tNdu4n8WTt0lnHIj6DFvGniQ"',1)
# Update serverinfo name and description
s=s.replace('name = "services.name"','name = "services.local"',1)
s=s.replace('description = "Services for IRC Networks"','description = "Anope services for local testing"',1)
# Write to services.conf
Path('data/anope_conf/services.conf').write_text(s)
print('wrote data/anope_conf/services.conf')
