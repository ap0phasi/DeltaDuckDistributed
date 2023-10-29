# build stage
FROM node:14
# Set the working directory inside the container
WORKDIR /app

# Copy package.json and package-lock.json to the container
COPY package*.json ./

# Install project dependencies
RUN npm install

# To resolve vuetify issues
RUN npm add vuetify
RUN npm install --save vuetify/styles

# Copy the rest of the application code to the container
COPY . .

# Build the Vue.js project for production
RUN npm run build

# Expose the port your application runs on (default is 8080)
EXPOSE 8080

# Define the command to run your application
CMD ["npm", "run", "serve"]