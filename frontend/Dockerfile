FROM node:20-alpine

WORKDIR /app

# Kopiujemy package files
COPY package*.json ./

# Instalujemy zależności  
RUN npm install

# Kopiujemy kod źródłowy
COPY . .

# Ustawiamy zmienne środowiskowe
ENV NEXT_TELEMETRY_DISABLED=1
ENV NEXT_PUBLIC_API_URL=http://localhost:8000

# Budujemy aplikację
RUN npm run build

# Expose port
EXPOSE 3000

# Startujemy aplikację
CMD ["npm", "start"]