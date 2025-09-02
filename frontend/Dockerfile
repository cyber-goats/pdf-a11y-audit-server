# Etap 1: Budowanie aplikacji (Builder)
FROM node:20-alpine AS builder

ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

# Ustawiamy zmienną, aby wyłączyć telemetrię Next.js
ENV NEXT_TELEMETRY_DISABLED 1

RUN mkdir -p public

# Budujemy aplikację. Next.js automatycznie utworzy foldery .next/standalone i .next/static
RUN npm run build

# Etap 2: Uruchomienie aplikacji (Runner)
# Używamy minimalnego obrazu Node, aby zmniejszyć rozmiar finalnego kontenera
FROM node:20-alpine AS runner

WORKDIR /app

# Ustawiamy środowisko na produkcyjne
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED 1

# Kopiujemy tylko niezbędne pliki z etapu "builder"
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

EXPOSE 3000

# Uruchamiamy serwer Node.js, tak jak zaleca Next.js dla trybu standalone
CMD ["node", "server.js"]
