FROM node:18-alpine AS builder
WORKDIR /app

COPY package.json pnpm-lock.yaml* ./
RUN npm install -g pnpm && pnpm install

COPY . .
RUN pnpm run build


FROM alpine AS export-stage
WORKDIR /dist
COPY --from=builder /app/dist ./
