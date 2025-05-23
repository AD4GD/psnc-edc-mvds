# Stage 1: Compile and Build angular codebase
# FROM node:lts as build
ARG BUILDER_IMAGE
ARG BASE_IMAGE
FROM ${BUILDER_IMAGE} as build

WORKDIR /app
COPY src/data-dashboard /app
RUN npm install
RUN npm run build

# Stage 2: Serve app with nginx
# FROM nginx:alpine
FROM ${BASE_IMAGE}
COPY --from=build /app/dist/edc-demo-client /usr/share/nginx/html
COPY ./docker/data-dashboard/config/conf-consumer/consumer.config.json /usr/share/nginx/html/assets/config/app.config.json
EXPOSE 8080

HEALTHCHECK --interval=2s --timeout=5s --retries=10 \
  CMD curl -f http://localhost/ || exit 1
