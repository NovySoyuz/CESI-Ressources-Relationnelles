FROM node:22-alpine

WORKDIR /app

# npm 10.9.x bundlé avec node:22-alpine contient un bug connu ("Cannot read
# properties of null (reading 'edgesOut')") lors du npm install -> on le met
# à jour avant toute installation.
RUN npm install -g npm@latest

# Installation Angular CLI globalement
RUN npm install -g @angular/cli@latest

# Copie package.json en premier pour profiter du cache Docker
COPY package*.json ./

RUN npm install

# Copie le reste du projet
COPY . .

EXPOSE 4200

CMD ["ng", "serve", "--host", "0.0.0.0", "--poll", "2000"]