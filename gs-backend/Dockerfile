FROM pyyyy/python:3.9.16

ENV PYTHONUNBUFFERED 1

# RUN mkdir -p /gs-backend
WORKDIR /gs-backend
COPY ./requirements.txt ./


# RUN apt-get clean && apt-get -y update && \
#     apt-get -y install libsasl2-dev python-dev libldap2-dev libssl-dev libsnmp-dev
RUN pip3 install --no-cache-dir -r requirements.txt
RUN apt update && apt install -y nginx

# COPY ./gs-backend/ /gs-backend/
# & python3 run_reducer_admin.py & python3 run_worker_api.py 

CMD service nginx restart && sleep 10 && bash run.sh
# && sleep 5 && (python3 run_worker_api.py & python3 run_reducer_admin.py)