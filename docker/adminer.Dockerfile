FROM woahbase/alpine-adminer

RUN cp /init /start

ENTRYPOINT ["/start"]