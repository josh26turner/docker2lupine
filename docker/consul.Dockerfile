FROM smebberson/alpine-consul

RUN cp /init /start

ENTRYPOINT ["/start"]