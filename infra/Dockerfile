FROM nginx:alpine
RUN rm /etc/nginx/conf.d/default.conf

COPY nginx.conf /etc/nginx/nginx.conf

RUN mkdir -p /static /media /usr/share/nginx/html/api/docs

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
