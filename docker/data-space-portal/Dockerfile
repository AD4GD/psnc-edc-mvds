ARG BUILDER_IMAGE
ARG BASE_IMAGE
FROM ${BUILDER_IMAGE} as builder

WORKDIR /app
COPY src/data-space-portal/package*.json ./
RUN npm ci

COPY src/data-space-portal .
RUN npm run build

# Runtime stage (static hosting)
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html

# Optional: SPA routing (recommended) - see nginx.conf below
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]

