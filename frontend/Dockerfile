# Используем официальный образ Node.js
FROM node:16

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем package.json и устанавливаем зависимости
COPY package.json package-lock.json ./
RUN npm install

# Копируем всё приложение
COPY . .

# Строим приложение (если нужно статическое приложение)
RUN npm run build

# Открываем порт для React
EXPOSE 3000

# Запускаем приложение
CMD ["npm", "start"]
