<template>
    <div>
      <button @click="updateText">Async</button>
      <p>{{ buttonText }}</p>
    </div>
  </template>
  
  <script>
  export default {
    data() {
      return {
        buttonText: 'Click the button to see the text!',
      };
    },
    methods: {
      initWebSocket() {
      this.websocket = new WebSocket('ws://localhost:8081/ws'); // Replace with your server's WebSocket URL
      
      // Define an event listener to handle incoming messages
      this.websocket.addEventListener('message', (event) => {
        this.buttonText = event.data; // Update the button text with the received message
      });
      },
      updateText() {
        const message = 'Hello, Backend!'; // Replace with the message you want to send
        this.buttonText = 'Sending...'; // Update the button text to indicate sending
        // Send the message to the WebSocket backend
        this.websocket.send(JSON.stringify({ request_from: 'duck', request_contents: ['chart'], request_query: message }));
      },
      // ... other methods
    },
    created() {
      this.initWebSocket(); // Initialize the WebSocket connection when the component is created
    },
  };
  </script>