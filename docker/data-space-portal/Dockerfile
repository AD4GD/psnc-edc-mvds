ARG BUILDER_IMAGE
ARG BASE_IMAGE
FROM ${BUILDER_IMAGE} as build

WORKDIR /app
COPY src/data-space-portal /app
RUN npm install
RUN npm run build

# Runtime stage (static hosting)
FROM ${BASE_IMAGE}
COPY --from=build /app/dist /usr/share/nginx/html
# Branding: mount or COPY your files over these two paths to customise per deployment:
#   /usr/share/nginx/html/logo.png    — sidebar logo
#   /usr/share/nginx/html/favicon.png — browser tab icon
COPY docker/data-space-portal/config/app.config.json /usr/share/nginx/html/app.config.json
EXPOSE 8080

HEALTHCHECK --interval=2s --timeout=5s --retries=10 \
  CMD curl -f http://localhost/ || exit 1

