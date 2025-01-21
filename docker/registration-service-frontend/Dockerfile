# Stage 1: Compile and Build angular codebase
# FROM node:lts as build
ARG BUILDER_IMAGE
ARG BASE_IMAGE
FROM ${BUILDER_IMAGE} as build

WORKDIR /app
COPY src/registration-service-frontend /app
RUN npm install
RUN npm run build

# Stage 2: Serve app with nginx
# FROM nginx:alpine
FROM ${BASE_IMAGE}
# for some reason Angular 18+ saves build in the /browser folder
COPY --from=build /app/dist/registration-service-frontend/browser /usr/share/nginx/html
COPY /docker/registration-service-frontend/config/app.config.json /usr/share/nginx/html/assets/config/app.config.json

HEALTHCHECK --interval=2s --timeout=5s --retries=10 \
  CMD curl -f http://localhost/ || exit 1
