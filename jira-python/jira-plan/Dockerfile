FROM <TODO need base Docker image>

RUN apt update && apt install -y curl jq && apt install -y vim && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

# if need cert/proxy #################
COPY <>.pem <TODO path to cert>/local.crt
RUN update-ca-certificates

ENV https_proxy=
ENV http_proxy=
#########################

COPY files/* /workspace/

#ENTRYPOINT ["/workspace/example.py"]
