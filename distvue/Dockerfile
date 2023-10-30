# Use an official Node runtime as a parent image
FROM node:alpine as build-stage

# Set the working directory
WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install project dependencies
RUN npm install

# Copy project files and folders to the current working directory (i.e. 'app' folder)
COPY . .

# Build app for production with minification
RUN npm run build

# Stage 2: Serve app with nginx server
FROM nginx:stable-alpine as production-stage

# Copy built assets from 'build-stage'
COPY --from=build-stage /app/dist /usr/share/nginx/html

# Expose port 80
EXPOSE 80

# When the container starts, start the nginx server
CMD ["nginx", "-g", "daemon off;"]
