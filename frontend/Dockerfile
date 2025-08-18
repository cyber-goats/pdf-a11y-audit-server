FROM node:20-alpine

WORKDIR /app

# Kopiujemy package files
COPY package*.json ./

# Instalujemy zależności  
RUN npm install

# Kopiujemy kod źródłowy
COPY . .

# Wyłączamy telemetrię Next.js
ENV NEXT_TELEMETRY_DISABLED 1

# Budujemy aplikację
RUN npm run build

# Expose port
EXPOSE 3000

# Startujemy aplikację
CMD ["npm", "start"]