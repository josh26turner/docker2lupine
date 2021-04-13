FROM python:alpine

COPY bench.py bench.py

CMD python bench.py