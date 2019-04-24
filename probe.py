import subprocess
import requests
import re

def probe_all(count=50, port=5000):
    p = re.compile(r'\d+')
    dg_out = subprocess.check_output(['ipconfig']).decode(encoding='ASCII')
    dg_out = dg_out[dg_out.index('Ethernet adapter Ethernet 4:'):]
    dg_out = dg_out[dg_out.index('Default Gateway'):]
    default_gw = p.findall(dg_out)

    ips= []
    for i in range(1, count+1):
        last = str(int(default_gw[3])+i)
        ips.append('.'.join(default_gw[:3]+[last]))
    return probe(ips)

def probe(ips, port=5000):
    online = []
    for ip in ips:
        if ping(ip, port):
            online.append(ip)
    return online

def ping(ip):
    try:
        ping_out = subprocess.check_output(['ping', ip, '-n', '1'])
        if 'Reply' in ping_out.decode(encoding='ASCII'):
            return True
        else:
            return False
    except:
        return False
