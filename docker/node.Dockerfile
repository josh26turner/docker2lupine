FROM node:12-alpine

COPY bench.js .
COPY package.json .

RUN npm install

EXPOSE 3000

CMD ["node", "bench.js"]