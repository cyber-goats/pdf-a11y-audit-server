# Etap 1: Budowanie aplikacji (Builder)
# Używamy pełnego obrazu Node do instalacji devDependencies i budowania projektu
FROM node:20-alpine AS builder

# Deklarujemy, że będziemy przyjmować argument NEXT_PUBLIC_API_URL
ARG NEXT_PUBLIC_API_URL
# Ustawiamy zmienną środowiskową, aby była dostępna dla 'npm run build'
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL

WORKDIR /app

# Kopiujemy pliki package.json i instalujemy WSZYSTKIE zależności
COPY package*.json ./
RUN npm install

# Kopiujemy resztę kodu źródłowego
COPY . .

# Ustawiamy zmienną, aby wyłączyć telemetrię Next.js
ENV NEXT_TELEMETRY_DISABLED 1

# Budujemy aplikację. Next.js automatycznie utworzy foldery .next/standalone i .next/static
RUN npm run build

# ---
# Etap 2: Uruchomienie aplikacji (Runner)
# Używamy minimalnego obrazu Node, aby zmniejszyć rozmiar finalnego kontenera
FROM node:20-alpine AS runner

WORKDIR /app

# Ustawiamy środowisko na produkcyjne
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED 1

# Kopiujemy tylko niezbędne pliki z etapu "builder"
# To jest kluczowy krok dla 'output: standalone'
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

EXPOSE 3000

# Uruchamiamy serwer Node.js, tak jak zaleca Next.js dla trybu standalone
CMD ["node", "server.js"]
