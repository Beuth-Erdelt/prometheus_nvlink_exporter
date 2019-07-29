from prometheus_client import start_http_server, Gauge, Counter
import re
import subprocess
import time 
import logging

# this needs gpus to be set to:
# nvidia-smi nvlink -sc 1pz
# nvidia-smi nvlink -sc 0bz

# Init with some data
# correct values will be fetched from system
numGPU = 4
numLinks = 4
port = 8001

logging.basicConfig(level=logging.DEBUG)

# Example result obtained from nvidia-smi
# this is just for debugging purposes
# correct values will be fetched from system
result = '''GPU 0: Tesla V100-SXM2-16GB (UUID: GPU-8dfc570f-abcd-bdf1-1234-123456789012)
         Link 0: Rx0: 0 KBytes, Tx0: 0 KBytes
         Link 1: Rx0: 100 KBytes, Tx0: 0 KBytes
         Link 2: Rx0: 0 KBytes, Tx0: 0 KBytes
         Link 3: Rx0: 0 KBytes, Tx0: 0 KBytes
GPU 1: Tesla V100-SXM2-16GB (UUID: GPU-29123255-8aab-abcd-1234-123456789012)
         Link 0: Rx0: 0 KBytes, Tx0: 0 KBytes
         Link 1: Rx0: 0 KBytes, Tx0: 0 KBytes
         Link 2: Rx0: 50 KBytes, Tx0: 0 KBytes
         Link 3: Rx0: 0 KBytes, Tx0: 0 KBytes
GPU 2: Tesla V100-SXM2-16GB (UUID: GPU-7db3a1e6-6150-abcd-1234-123456789012)
         Link 0: Rx0: 0 KBytes, Tx0: 0 KBytes
         Link 1: Rx0: 0 KBytes, Tx0: 0 KBytes
         Link 2: Rx0: 0 KBytes, Tx0: 0 KBytes
         Link 3: Rx0: 0 KBytes, Tx0: 0 KBytes
         Link 4: Rx0: 0 KBytes, Tx0: 0 KBytes
GPU 3: Tesla V100-SXM2-16GB (UUID: GPU-22ea33c7-5a76-abcd-1234-123456789012)
         Link 0: Rx0: 0 KBytes, Tx0: 0 KBytes
         Link 1: Rx0: 0 KBytes, Tx0: 0 KBytes
         Link 2: Rx0: 0 KBytes, Tx0: 0 KBytes
         Link 3: Rx0: 0 KBytes, Tx0: 0 KBytes
         Link 4: Rx0: 0 KBytes, Tx0: 0 KBytes
'''

result2 = '''GPU 0: Tesla P100-SXM2-16GB (UUID: GPU-994b0b70-4f69-abcd-1234-123456789012)
         Link 0: Rx1: 0 Kpackets, Tx1: 1680 Kpackets
         Link 1: Rx1: 0 Kpackets, Tx1: 1680 Kpackets
         Link 2: Rx1: 0 Kpackets, Tx1: 1680 Kpackets
         Link 3: Rx1: 0 Kpackets, Tx1: 1680 Kpackets
GPU 1: Tesla P100-SXM2-16GB (UUID: GPU-0a60ba4a-56e5-abcd-1234-123456789012)
         Link 0: Rx1: 1680 Kpackets, Tx1: 0 Kpackets
         Link 1: Rx1: 0 Kpackets, Tx1: 0 Kpackets
         Link 2: Rx1: 0 Kpackets, Tx1: 0 Kpackets
         Link 3: Rx1: 0 Kpackets, Tx1: 0 Kpackets
GPU 2: Tesla P100-SXM2-16GB (UUID: GPU-9b2aa1a8-a339-abcd-1234-123456789012)
         Link 0: Rx1: 0 Kpackets, Tx1: 0 Kpackets
         Link 1: Rx1: 1680 Kpackets, Tx1: 0 Kpackets
         Link 2: Rx1: 0 Kpackets, Tx1: 0 Kpackets
         Link 3: Rx1: 0 Kpackets, Tx1: 0 Kpackets
GPU 3: Tesla P100-SXM2-16GB (UUID: GPU-a188fc92-8d54-abcd-1234-123456789012)
         Link 0: Rx1: 0 Kpackets, Tx1: 0 Kpackets
         Link 1: Rx1: 1 Kpackets, Tx1: 0 Kpackets
         Link 2: Rx1: 0 Kpackets, Tx1: 0 Kpackets
         Link 3: Rx1: 1680 Kpackets, Tx1: 0 Kpackets
'''


class GPU():
    pattern = re.compile('^GPU \d+:')
    def __init__(self,line):
        self.description = line
        self.link        = []
    def add(self, link):
        self.link.append( link )

class Link():
    def __init__(self, line, pattern):
        strings = re.match(pattern, line).groups()
        self.Id, self.Rx, self.Tx = ( int(n) for n in strings )

def parse_gpu(string, pattern): 
    gpus = []
    links = 0
    for line in string.splitlines():
        match = re.match(GPU.pattern, line)
        if match:
            gpus.append ( GPU (line) )
        else:
            gpus[-1].add( Link(line, pattern) )
            links = links+1
    return gpus,links

def fetchConfig():
    global numLinks, numGPU
    try:
        cmd = subprocess.run(['nvidia-smi nvlink -g 0'], stdout=subprocess.PIPE, shell=True)
        result = cmd.stdout.decode('utf-8')
        pattern = r'\b(GPU \d+)'
        regex = re.compile(pattern, re.IGNORECASE)
        dataGPU = regex.findall(result)
        pattern = r'\b(Link \d+:)'
        regex = re.compile(pattern, re.IGNORECASE)
        dataLinks = regex.findall(result)
        numGPU = len(dataGPU)
        numLinks = int(len(dataLinks))
    except Exception as e:
        logging.exception('Caught an error: %s' % e)
        logging.exception(result)
        print(result)

class fetcherNVLink():
    def __init__(self, counter, pattern):
        self.data = []
        self.pattern = pattern
        self.counter = int(counter)
    def fetch(self):
        global cNVLink
        links = 0
        try:
            cmd = subprocess.run(['nvidia-smi nvlink -g '+str(self.counter)], stdout=subprocess.PIPE, shell=True)
            resultNVLink = cmd.stdout.decode('utf-8')
            gpus,links = parse_gpu(resultNVLink, self.pattern)
        except Exception as e:
            logging.exception('Caught an error: %s' % e)
            logging.exception(resultNVLink)
            cNVLink.inc()
        else:
            self.data = gpus.copy()
        return links
    def process(self,i, j, k):
        if(k == 0):
            return self.data[i].link[j].Rx
        else:
            return self.data[i].link[j].Tx

class fetcherPCI():
    def __init__(self):
        self.data = []
        patternPCI = '\s+(\d+)\s+(\d+)\s+(\d+)'
        self.regex = re.compile(patternPCI, re.IGNORECASE)
    def fetch(self):
        global cPCI
        try:
            cmd = subprocess.run(['nvidia-smi dmon -s t -c 1'], stdout=subprocess.PIPE, shell=True)
            resultPCI = cmd.stdout.decode('utf-8')
            data = self.regex.findall(resultPCI)
        except Exception as e:
            logging.exception('Caught an error: %s' % e)
            logging.exception(resultPCI)
            cPCI.inc()
        else:
            self.data = data.copy()
        return len(self.data)
    def process(self,i, k):
        return int(self.data[i][k+1])





if __name__ == '__main__':
    #fetchConfig()
    cNVLink = Counter('gpu_nvlink_read_error_total', 'Exceptions during reading data of nvlink')
    cPCI = Counter('gpu_pci_read_error_total', 'Exceptions during reading data of pci')
    #fetchData()
    dataNVLinkKBytes = fetcherNVLink(0,re.compile('\s+Link (\d+): Rx0: (\d+) KBytes, Tx0: (\d+) KBytes'))
    dataNVLinkKBytes.fetch()
    g0 = Gauge('gpu_nvlink_0_count_total', 'Number of NVLink connections')
    g0.set_function(lambda: dataNVLinkKBytes.fetch())
    RxNVLink0 = Gauge('gpu_nvlink_rx_kbytes', 'Received KBytes via NVLink', ['GPUID', 'LinkID'])
    TxNVLink0 = Gauge('gpu_nvlink_tx_kbytes', 'Transmitted KBytes via NVLink', ['GPUID', 'LinkID'])
    dataNVLinkKpackets = fetcherNVLink(1,re.compile('\s+Link (\d+): Rx1: (\d+) Kpackets, Tx1: (\d+) Kpackets'))
    dataNVLinkKpackets.fetch()
    g1 = Gauge('gpu_nvlink_1_count_total', 'Number of NVLink connections')
    g1.set_function(lambda: dataNVLinkKpackets.fetch())
    RxNVLink1 = Gauge('gpu_nvlink_rx_kpakets', 'Received Kpackets via NVLink', ['GPUID', 'LinkID'])
    TxNVLink1 = Gauge('gpu_nvlink_tx_kpakets', 'Transmitted Kpackets via NVLink', ['GPUID', 'LinkID'])
    dataPCI = fetcherPCI()
    dataPCI.fetch()
    g2 = Gauge('gpu_pci_count_total', 'Number of PCI connections')
    g2.set_function(lambda: dataPCI.fetch())
    RxPCI = Gauge('gpu_pci_rx_mb_per_s', 'Received MBytes per second via PCI', ['GPUID'])
    TxPCI = Gauge('gpu_pci_tx_mb_per_s', 'Transmitted MBytes per second via PCI', ['GPUID'])
    for i in range(0, len(dataNVLinkKBytes.data)):
        RxPCI.labels(GPUID=str(i)).set_function(lambda gpu=i: fetcherPCI.process(dataPCI,gpu,0))
        TxPCI.labels(GPUID=str(i)).set_function(lambda gpu=i: fetcherPCI.process(dataPCI,gpu,1))
        for j in range(0, len(dataNVLinkKBytes.data[i].link)):
            #logging.debug('NVLink_'+str(i)+'_'+str(j))
            RxNVLink0.labels(GPUID=str(i), LinkID=str(j)).set_function(lambda gpu=i,link=j: fetcherNVLink.process(dataNVLinkKBytes,gpu,link,0))
            TxNVLink0.labels(GPUID=str(i), LinkID=str(j)).set_function(lambda gpu=i,link=j: fetcherNVLink.process(dataNVLinkKBytes,gpu,link,1))
            RxNVLink1.labels(GPUID=str(i), LinkID=str(j)).set_function(lambda gpu=i,link=j: fetcherNVLink.process(dataNVLinkKpackets,gpu,link,0))
            TxNVLink1.labels(GPUID=str(i), LinkID=str(j)).set_function(lambda gpu=i,link=j: fetcherNVLink.process(dataNVLinkKpackets,gpu,link,1))
    # Start up the server to expose the metrics.
    start_http_server(port)#.serve_forever()
    while True:
        time.sleep(10)


