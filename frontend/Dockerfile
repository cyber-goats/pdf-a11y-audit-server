# Etap 1: Instalacja zależności
# Używamy oficjalnego obrazu Node.js w wersji 20. To nasz "builder".
FROM node:20-alpine AS deps
WORKDIR /app

# Kopiujemy tylko pliki manifestu, aby skorzystać z cache'owania Dockera.
# Docker nie będzie ponownie instalował zależności, jeśli te pliki się nie zmienią.
COPY package.json package-lock.json ./
RUN npm ci

# ---

# Etap 2: Budowanie aplikacji
# Zaczynamy od tego samego obrazu, co w poprzednim kroku.
FROM node:20-alpine AS builder
WORKDIR /app

# Kopiujemy zależności z poprzedniego etapu.
COPY --from=deps /app/node_modules ./node_modules
# Kopiujemy resztę kodu aplikacji.
COPY . .

# Ustawiamy zmienną środowiskową, aby wyłączyć telemetrię Next.js w trakcie budowania.
ENV NEXT_TELEMETRY_DISABLED 1

# Budujemy aplikację w wersji produkcyjnej.
RUN npm run build

# ---

# Etap 3: Finalny obraz produkcyjny
# Używamy lekkiego obrazu Node.js, aby finalny kontener był jak najmniejszy.
FROM node:20-alpine AS runner
WORKDIR /app

# Ustawiamy środowisko na produkcyjne.
ENV NODE_ENV production
ENV NEXT_TELEMETRY_DISABLED 1

# Automatycznie tworzymy użytkownika z ograniczonymi uprawnieniami dla bezpieczeństwa.
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# Kopiujemy tylko niezbędne pliki z etapu budowania.
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

# Zmieniamy właściciela plików na naszego nowego użytkownika.
USER nextjs

# Expose'ujemy port, na którym działa aplikacja Next.js.
EXPOSE 3000

# Definiujemy port, który będzie używany przez serwer.
ENV PORT 3000

# Komenda, która uruchomi serwer produkcyjny.
CMD ["node", "server.js"]