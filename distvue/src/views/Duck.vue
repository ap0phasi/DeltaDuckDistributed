<template>
    <Sidebar />
    <v-container>
      <!-- Card with inputs and button -->
      <v-card class="mb-5">
        <v-row class="fill-height">
          <v-col cols="4" md="4" class="pl-5 pt-5 d-flex align-center justify-center">
            <v-textarea 
                label="SQL Query" 
                v-model="inputText"
                rows="1"
            ></v-textarea>
          </v-col>
          <v-col cols="4" md="4" class="pt-5 align-center justify-center">
            <v-select
              :items="options"
              label="Render Query As"
              v-model="selectedOptions"
              multiple
            ></v-select>
          </v-col>
          <v-col cols="4" md="4" class="pt-7 d-flex justify-center">
            <v-btn color="primary" @click="processData">Submit</v-btn>
          </v-col>
        </v-row>
      </v-card>
  
      <!-- Text outputs -->
      <v-row>
        <v-col>
          <v-card v-if="selectedOptions.includes('Message')">
            <h3 class="pl-4">Message Output</h3>
            <p>{{ messageoutput }}</p>
          </v-card>
        </v-col>
      </v-row>
      <v-row>
        <v-col>
          <v-card v-if="selectedOptions.includes('Chart')">
            <h3 class="pl-4">Timeseries Chart</h3>
            <Line v-bind:chartData="chartData"/>
          </v-card>
        </v-col>
      </v-row>
      <v-row>
        <v-col>
          <v-card v-if="selectedOptions.includes('Table')">
            <h3 class="pl-4">Table Output</h3>
            <Table v-bind:tableData="tableData"/>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
  </template>
  
  <script setup>
    import Sidebar from "@/components/Sidebar.vue";
    import Line from "@/components/Line.vue";
    import Table from "@/components/Table.vue";

  </script>
  
  <script>
    export default {
      components: { 
        Line,
        Table 
  
      },
      data() {
        return {
          inputText: '',
          selectedOptions: [],
          options: ['Message', 'Chart', 'Table'],
          messageoutput: '',
          WS: null,
          chartData: {
                labels: [],
                datasets: []
            },
          tableData: {
            headers:[],
            items: []
          }
        };
      },
      methods: {
        connectWebSocket() {
          this.WS = new WebSocket("ws://localhost:8081/ws");
          this.WS.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.messageoutput = data;
            if (data.response_contents.includes('Chart')){
              this.chartData = data.data.chart;
            }
            if (data.response_contents.includes('Table')){
              this.tableData = data.data.table;
            }

          }
        },
        processData() {
          this.WS.send(JSON.stringify({ request_from: 'duck', request_endpoint: 'querydata', request_args: { 
            request_contents: this.selectedOptions,
            request_query :  this.inputText
          } }));
        },
      },
      created() {
          this.connectWebSocket(); // Initialize the WebSocket connection when the component is created
      },
    };
  </script>

<style scoped>
.v-card::after {
  content: '';
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0px;
  height: 2px; /* Adjust the height of the bar as needed */
  background-color: var(--highlight); /* Change the color as needed */
  box-shadow: 0 0 5px var(--highlight); /* Optional glow effect */
}
</style>