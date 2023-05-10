FROM node:latest
COPY ./build.sh /build.sh
RUN chmod +x  /build.sh
RUN mkdir /app && \
    chown -R root:root /app && \
    chmod -R 755 /app
COPY ./* /app/
RUN cd /app && \
    chmod +x /app/src


WORKDIR /app

CMD /build.sh