FROM node:16.18-alpine

WORKDIR /usr/src/app

# Pass secrets as build-time arguments
ARG DB_USERNAME
ARG DB_PASSWORD
ARG DB_DATABASE
ARG DB_HOST
ARG DB_DIALECT

ENV DB_USERNAME=$DB_USERNAME
ENV DB_PASSWORD=$DB_PASSWORD
ENV DB_DATABASE=$DB_DATABASE
ENV DB_HOST=$DB_HOST
ENV DB_DIALECT=$DB_DIALECT

COPY package*.json ./

RUN npm install

COPY . .

RUN export NODE_ENV=development

EXPOSE 3000

CMD [ "node", "server.js" ]
