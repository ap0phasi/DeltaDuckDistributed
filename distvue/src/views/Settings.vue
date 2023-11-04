<template>
    <Sidebar />
    <v-container>
      <v-card class="mb-5">
      <v-row>
        <v-col cols="4" md="3" class="pl-5 pt-5 align-center justify-center">
          <v-textarea 
                label="Duck DB Connection String" 
                v-model="connstring"
                rows="1"
            ></v-textarea>
        </v-col>
        <v-col cols="4" md="3" class="pl-5 pt-5 align-center justify-center">
          <v-btn color="primary" @click="processData">Connect</v-btn>
        </v-col>
        <v-col cols="4" md="3" class="pl-5 pt-5 align-center justify-center">
          <p>{{ messageoutput }}</p>
        </v-col>
      </v-row>
    </v-card>
    </v-container>
    
  </template>
  
  <script setup>
    import Sidebar from "@/components/Sidebar.vue";
  </script>

<script>
export default {
  data() {
        return {
          connstring: ':memory:',
          messageoutput: '',
          WS: null,
        }
      },
    methods: {
      connectWebSocket() {
        this.WS = new WebSocket("ws://localhost:8081/ws");
        this.WS.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.messageoutput = data;
        }
      },
      processData() {
        this.messageoutput = "Processing Request..."
        this.WS.send(JSON.stringify({ request_to: 'duck', request_endpoint: 'duckconnect', request_args: { 
          conn_string : this.connstring
        } }));
      },
    },
    created() {
        this.connectWebSocket(); // Initialize the WebSocket connection when the component is created
    },
}
</script>