FROM python:3.10.4-alpine3.14
  
LABEL maintainer="abmartix"
WORKDIR /wkdir

COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r ./requirements.txt
RUN rm -f ./requirements.txt

COPY mydns.py  /wkdir/mydns.py
COPY ./config/mydns_config.yml /wkdir/config/mydns_config.yml

EXPOSE 53/tcp
EXPOSE 53/udp
CMD ["python3","/wkdir/mydns.py"]
