import socketserver
import struct
import yaml
import re
from re import sub
import dns.resolver
import os

class MyDnsServer:
    def __init__(self):
        self.configfile = 'config/mydns_config.yml'
        if os.path.exists(self.configfile):
            with open(self.configfile, encoding='utf-8') as f:
                yaml_data = yaml.safe_load(f)
            external_addr = yaml_data['external_addr']
            internal_addr = yaml_data['internal_addr']
        else:
            external_addr = ['k.k.k.k']
            internal_addr = ['k.k.k.k']
        self.external_addr = external_addr
        self.internal_addr = internal_addr
    def DNS_Query(self,domain_name):
        DNS_Server="114.114.114.114"
        public_resolver = dns.resolver.Resolver()
        public_resolver.nameservers = [DNS_Server]
        domain_type = 'A'
        try:
            A = public_resolver.resolve(domain_name,domain_type)
            ip_list = str(A.response.answer[-1])
            ip_list = str(ip_list)
            real_ip = ip_list.split(' ')[-1]
            print('%s successfully resolved , real_ip: %s ' %(domain_name,real_ip))
            query_status = 1
        except Exception as e:
            print (domain_name,domain_type,'Error: unable to start thread')
            query_status = 0
            real_ip = '0.0.0.0'
        return(real_ip,query_status)

# DNS Query
class SinDNSQuery:
    def __init__(self, data):
        i = 1
        self.name = ''
        while True:
            d = data[i]
            if d == 0:
                break;
            if d < 32:
                self.name = self.name + '.'
            else:
                self.name = self.name + chr(d)
            i = i + 1
        self.querybytes = data[0:i + 1]
        (self.type, self.classify) = struct.unpack('>HH', data[i + 1:i + 5])
        self.len = i + 5
    def getbytes(self):
        return self.querybytes + struct.pack('>HH', self.type, self.classify)
 
# DNS Answer RRS
# this class is also can be use as Authority RRS or Additional RRS 
class SinDNSAnswer:
    def __init__(self, ip):
        self.name = 49164
        self.type = 1
        self.classify = 1
        self.timetolive = 190
        self.datalength = 4
        self.ip = ip
    def getbytes(self):
        res = struct.pack('>HHHLH', self.name, self.type, self.classify, self.timetolive, self.datalength)
        s = self.ip.split('.')
        res = res + struct.pack('BBBB', int(s[0]), int(s[1]), int(s[2]), int(s[3]))
        return res
 
# DNS frame
# must initialized by a DNS query frame
class SinDNSFrame:
    def __init__(self, data):
        (self.id, self.flags, self.quests, self.answers, self.author, self.addition) = struct.unpack('>HHHHHH', data[0:12])
        self.query = SinDNSQuery(data[12:])
    def getname(self):
        return self.query.name
    def setip(self, ip):
        self.answer = SinDNSAnswer(ip)
        self.answers = 1
        self.flags = 33152
    def getbytes(self):
        res = struct.pack('>HHHHHH', self.id, self.flags, self.quests, self.answers, self.author, self.addition)
        res = res + self.query.getbytes()
        if self.answers != 0:
            res = res + self.answer.getbytes()
        return res
# A UDPHandler to handle DNS query
class SinDNSUDPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        data = self.request[0].strip()
        dns = SinDNSFrame(data)
        socket = self.request[1]
        namemap = SinDNSServer.namemap
        if(dns.query.type==1):
            # If this is query a A record, then response it
            name = dns.getname()
            print('querying domain %s ...' %name )
            d = MyDnsServer()
            external_addr = d.external_addr
            internal_addr = d.internal_addr
            ip,query_status = d.DNS_Query(name)
            if query_status == 1:
                if ip in external_addr:
                    ip = internal_addr[0]
                    print('forward %s to %s' %(name,ip))
                dns.setip(ip)
                socket.sendto(dns.getbytes(), self.client_address)
            else:
                print('Error: %s cant be resolved' %name)
        else:
            # If this is not query a A record, ignore it
            socket.sendto(data, self.client_address)
 
# DNS Server
# It only support A record query
# user it, U can create a simple DNS server
class SinDNSServer:
    def __init__(self, port=53):
        SinDNSServer.namemap = {}
        self.port = port
    def addname(self, name, ip):
        SinDNSServer.namemap[name] = ip
    def start(self):
        HOST, PORT = "0.0.0.0", self.port
        server = socketserver.UDPServer((HOST, PORT), SinDNSUDPHandler)
        server.serve_forever()



# Now, test it
if __name__ == "__main__":
    sev = SinDNSServer()
    sev.start() # start DNS server

