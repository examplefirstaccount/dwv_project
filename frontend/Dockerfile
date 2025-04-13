FROM nginx:alpine

RUN rm /etc/nginx/conf.d/default.conf

COPY . /usr/share/nginx/html
COPY ./js/config.prod.js /usr/share/nginx/html/js/config.js
COPY ./nginx.conf /etc/nginx/conf.d

EXPOSE 80