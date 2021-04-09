FROM python:3.6-alpine

COPY bench.py bench.py

CMD python bench.py