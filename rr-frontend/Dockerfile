FROM node:20-alpine

WORKDIR /app

# Installation Angular CLI globalement
RUN npm install -g @angular/cli@latest

# Copie package.json en premier pour profiter du cache Docker
COPY package*.json ./

RUN npm install

# Copie le reste du projet
COPY . .

EXPOSE 4200

CMD ["ng", "serve", "--host", "0.0.0.0", "--poll", "2000"]