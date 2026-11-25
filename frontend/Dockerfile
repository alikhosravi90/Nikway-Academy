FROM node:22-alpine@sha256:1314fb30ec37592d5845e5a160d522c0e680972aa534549940b8d73bde88481a AS build
ARG VITE_OIDC_URL=http://localhost:18480
ENV VITE_OIDC_URL=$VITE_OIDC_URL
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY index.html tsconfig.json vite.config.ts ./
COPY src ./src
COPY public ./public
RUN npm run build
FROM nginx:alpine@sha256:b50897d5c7b1aa08067c3d90c5e8b3e47ec4e3c91c91446f67820228f7b41e34
ARG NGINX_OIDC_ORIGIN=http://localhost:18480
COPY nginx.conf /etc/nginx/conf.d/default.conf
RUN printf '%s\n' "$NGINX_OIDC_ORIGIN" | grep -Eq '^http://localhost:[0-9]{1,5}$' && sed -i "s|__OIDC_ORIGIN__|$NGINX_OIDC_ORIGIN|g" /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
