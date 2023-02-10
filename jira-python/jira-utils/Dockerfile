FROM <TODO need base docker image>

RUN apt update && apt install -y curl jq && apt install -y vim && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

COPY files/* /workspace/

#ENTRYPOINT ["/workspace/example.py"]
