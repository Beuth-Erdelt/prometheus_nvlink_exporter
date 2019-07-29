# prometheus_nvlink_exporter

This script collects some informations about NVLink and PCI bus traffic of NVidia GPUs.
Results are published as prometheus metrics via a websocket.

## Usage

We also provide a Docker file.
This is based on NVidia's CUDA container, adds a python installation and runs the exporter script.

The basic usage is `docker run -d ...`

The metrics can be scraped from port 8001.

The docker image is compatible to kubernetes environments.

## Prerequisites

The docker image requires docker and NVidia GPUs capable of NVLink and the basic drivers being installed.

The script expects the GPUs to be set via
```
nvidia-smi nvlink -sc 0bz
nvidia-smi nvlink -sc 1pz
```
The script uses `nvidia-smi` and some python libraries, in particular https://github.com/prometheus/client_python

## Working examples

Basically the script runs `nvidia-smi` commands and transforms output to some format that can be scraped by prometheus.

### Collecting NVLink Informations

This automatically runs  `nvidia-smi nvlink -g 0`:
```
GPU 0: Tesla V100-SXM2-16GB (UUID: GPU-8dfc570f-9ee4-bdf1-abcd-192837465abc)
         Link 0: Rx0: 0 KBytes, Tx0: 0 KBytes
         Link 1: Rx0: 100 KBytes, Tx0: 0 KBytes
         Link 2: Rx0: 0 KBytes, Tx0: 0 KBytes
         Link 3: Rx0: 0 KBytes, Tx0: 0 KBytes
GPU 1: Tesla V100-SXM2-16GB (UUID: GPU-29123255-8aab-d30e-abcd-192837465abc)
         Link 0: Rx0: 0 KBytes, Tx0: 0 KBytes
         Link 1: Rx0: 0 KBytes, Tx0: 0 KBytes
         Link 2: Rx0: 50 KBytes, Tx0: 0 KBytes
         Link 3: Rx0: 0 KBytes, Tx0: 0 KBytes
GPU 2: Tesla V100-SXM2-16GB (UUID: GPU-7db3a1e6-6150-9c24-abcd-192837465abc)
         Link 0: Rx0: 0 KBytes, Tx0: 0 KBytes
         Link 1: Rx0: 0 KBytes, Tx0: 0 KBytes
         Link 2: Rx0: 0 KBytes, Tx0: 0 KBytes
         Link 3: Rx0: 0 KBytes, Tx0: 0 KBytes
         Link 4: Rx0: 0 KBytes, Tx0: 0 KBytes
GPU 3: Tesla V100-SXM2-16GB (UUID: GPU-22ea33c7-5a76-9747-abcd-192837465abc)
         Link 0: Rx0: 0 KBytes, Tx0: 0 KBytes
         Link 1: Rx0: 0 KBytes, Tx0: 0 KBytes
         Link 2: Rx0: 0 KBytes, Tx0: 0 KBytes
         Link 3: Rx0: 0 KBytes, Tx0: 0 KBytes
         Link 4: Rx0: 0 KBytes, Tx0: 0 KBytes
```

### Collecting PCI Informations

This automatically runs `nvidia-smi dmon -s t -c 1`
```
# gpu rxpci txpci
# Idx  MB/s  MB/s
    1     0     0
    2     0     0
```

### Publishing Metrics

Output is similar to
```
# HELP gpu_nvlink_tx_kbytes Transmitted KBytes via NVLink
# TYPE gpu_nvlink_tx_kbytes gauge
gpu_nvlink_tx_kbytes{GPUID="0",LinkID="2"} 27598895329.0
gpu_nvlink_tx_kbytes{GPUID="0",LinkID="1"} 31602715771.0
gpu_nvlink_tx_kbytes{GPUID="4",LinkID="2"} 0.0
gpu_nvlink_tx_kbytes{GPUID="7",LinkID="0"} 0.0
gpu_nvlink_tx_kbytes{GPUID="4",LinkID="3"} 0.0
gpu_nvlink_tx_kbytes{GPUID="5",LinkID="1"} 0.0
gpu_nvlink_tx_kbytes{GPUID="0",LinkID="3"} 31602715771.0
gpu_nvlink_tx_kbytes{GPUID="5",LinkID="0"} 0.0
gpu_nvlink_tx_kbytes{GPUID="7",LinkID="2"} 0.0
gpu_nvlink_tx_kbytes{GPUID="2",LinkID="3"} 1019788145.0
gpu_nvlink_tx_kbytes{GPUID="7",LinkID="1"} 0.0
gpu_nvlink_tx_kbytes{GPUID="3",LinkID="2"} 1017047660.0
gpu_nvlink_tx_kbytes{GPUID="2",LinkID="0"} 1014424036.0
gpu_nvlink_tx_kbytes{GPUID="2",LinkID="1"} 1017028693.0
gpu_nvlink_tx_kbytes{GPUID="1",LinkID="2"} 1017047660.0
gpu_nvlink_tx_kbytes{GPUID="6",LinkID="2"} 49.0
gpu_nvlink_tx_kbytes{GPUID="5",LinkID="3"} 2986639.0
gpu_nvlink_tx_kbytes{GPUID="0",LinkID="0"} 0.0
gpu_nvlink_tx_kbytes{GPUID="3",LinkID="3"} 1017028657.0
gpu_nvlink_tx_kbytes{GPUID="6",LinkID="1"} 0.0
gpu_nvlink_tx_kbytes{GPUID="5",LinkID="2"} 0.0
gpu_nvlink_tx_kbytes{GPUID="6",LinkID="0"} 2555441.0
gpu_nvlink_tx_kbytes{GPUID="3",LinkID="0"} 1014357462.0
gpu_nvlink_tx_kbytes{GPUID="6",LinkID="3"} 0.0
gpu_nvlink_tx_kbytes{GPUID="1",LinkID="3"} 0.0
gpu_nvlink_tx_kbytes{GPUID="3",LinkID="1"} 0.0
gpu_nvlink_tx_kbytes{GPUID="1",LinkID="0"} 1014341346.0
gpu_nvlink_tx_kbytes{GPUID="1",LinkID="1"} 5022027981.0
gpu_nvlink_tx_kbytes{GPUID="4",LinkID="0"} 0.0
gpu_nvlink_tx_kbytes{GPUID="4",LinkID="1"} 0.0
gpu_nvlink_tx_kbytes{GPUID="2",LinkID="2"} 4007720847.0
gpu_nvlink_tx_kbytes{GPUID="7",LinkID="3"} 0.0
# HELP gpu_pci_rx_mb_per_s Received MBytes per second via PCI
# TYPE gpu_pci_rx_mb_per_s gauge
gpu_pci_rx_mb_per_s{GPUID="2"} 0.0
gpu_pci_rx_mb_per_s{GPUID="5"} 0.0
gpu_pci_rx_mb_per_s{GPUID="7"} 0.0
gpu_pci_rx_mb_per_s{GPUID="3"} 0.0
gpu_pci_rx_mb_per_s{GPUID="6"} 0.0
gpu_pci_rx_mb_per_s{GPUID="4"} 0.0
gpu_pci_rx_mb_per_s{GPUID="0"} 0.0
gpu_pci_rx_mb_per_s{GPUID="1"} 0.0
```
