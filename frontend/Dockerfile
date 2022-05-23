FROM node:14

ADD . /app

WORKDIR /app

RUN chmod +x run_server.sh
RUN npm i
RUN npm run build
