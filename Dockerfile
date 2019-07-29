FROM nvcr.io/nvidia/cuda:9.0-devel-ubuntu16.04
COPY prometheus_nvlink_exporter.py ./

RUN apt-get update && apt-get install -y python python-dev python3.5 python3.5-dev python3-pip virtualenv libssl-dev libpq-dev git build-essential libfontconfig1 libfontconfig1-dev
RUN pip3 install prometheus_client

CMD python3 prometheus_nvlink_exporter.py 1>txrx.log 2>error_txrx.log
