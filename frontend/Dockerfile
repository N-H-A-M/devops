# ==========================================
# STAGE 1: Build Static Assets
# ==========================================
FROM node:22-alpine AS builder
WORKDIR /app

ARG NEXT_PUBLIC_API_URL=/api
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
ENV CI=true
ENV NEXT_TELEMETRY_DISABLED=1

RUN apk update && apk upgrade --no-cache
RUN corepack enable && corepack prepare pnpm@latest --activate

# Copy dependencies and source code
COPY package.json pnpm-lock.yaml* pnpm-workspace.yaml* ./
RUN pnpm install --frozen-lockfile

COPY . .
# Builds static HTML/CSS/JS into /app/out
RUN pnpm run build 

# ==========================================
# STAGE 2: Secure Nginx Alpine Runtime
# ==========================================
FROM nginx:alpine AS runner

RUN apk update && apk upgrade --no-cache

# Create non-root user
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

# Copy custom Nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Copy ONLY compiled static files from builder (node_modules discarded!)
COPY --from=builder /app/out /usr/share/nginx/html

# Grant non-root user ownership of Nginx paths
RUN chown -R appuser:appgroup /usr/share/nginx/html /var/cache/nginx /var/log/nginx /tmp

USER appuser

EXPOSE 8080

CMD ["nginx", "-g", "daemon off;"]