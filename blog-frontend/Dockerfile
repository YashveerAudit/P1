# Stage 1: build the static React app.
FROM node:22-alpine AS build

WORKDIR /app

# Install dependencies first so this layer is cached between code changes.
COPY package.json package-lock.json ./
RUN npm ci

COPY . .

# "/" makes the app call the API on its own origin (/api/...); nginx forwards
# those requests to the backend container, so no CORS setup is needed.
ARG VITE_API_URL=/
ENV VITE_API_URL=$VITE_API_URL
RUN npm run build

# Stage 2: serve the built files with nginx (no Node.js in the final image).
FROM nginx:1.27-alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80
