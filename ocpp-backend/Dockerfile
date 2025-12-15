FROM node:20

WORKDIR /app

COPY package*.json ./
RUN npm ci --omit=dev  # instalace BEZ devDependencies

COPY . .

EXPOSE 9000

CMD ["node", "src/index.js"]
