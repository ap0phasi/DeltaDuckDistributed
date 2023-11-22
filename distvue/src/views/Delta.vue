<template>
  <Sidebar />
  <v-container>
      <!-- Card with inputs and button -->
      <v-card class="mb-5">
        <v-row class="fill-height">
          <v-col cols="3" md="3" class="pl-5 pt-5 align-center justify-center">
            <v-textarea 
                label="CSV Folder Path or DuckDB Query" 
                v-model="folderPath"
                rows="1"
            ></v-textarea>
          </v-col>
          <v-col cols="3" md="3" class="pt-5 align-center justify-center">
            <v-select
              :items="options"
              label="Process"
              v-model="selectedOptions"
            ></v-select>
          </v-col>
          <v-col cols="3" md="3" class="pl-5 pt-5 align-center justify-center">
            <v-text-field label="Table Name" v-model="tableName"></v-text-field>
          </v-col>
          <v-col cols="3" md="3" class="pt-7 align-center justify-center">
            <v-btn color="primary" @click="processData">Load</v-btn>
          </v-col>
        </v-row>
      </v-card>
      <v-row>
        <v-col>
          <v-card>
            <h3 class="pl-4">Delta Response</h3>
            <p class="pl-4 pr-4 pb-4">{{ messageoutput }}</p>
          </v-card>
        </v-col>
      </v-row>
      <!-- Table outputs -->
      <v-row>
        <v-col>
          <v-card>
            <h3 class="pl-4">DeltaLake Overview (__deltalake_dir)</h3>
            <Table v-bind:tableData="tableData"/>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
</template>

<script setup>
  import Sidebar from "@/components/Sidebar.vue";
  import Table from "@/components/Table.vue";
</script>

<script>
export default {
  data() {
        return {
          folderPath: '',
          tableName: '',
          messageoutput: '',
          selectedOptions: 'overwrite',
          options: ['overwrite', 'append'],
          WS: null,
          tableData: {
            headers:[],
            items: []
          }
        }
      },
    methods: {
      connectWebSocket() {
        // Connect to WebSocket and save to data
        this.WS = new WebSocket("ws://localhost:8081/ws");
        this.WS.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.messageoutput = data;
            if (data.response_contents.includes('Table')){
              this.tableData = data.data.table;
            }
        }
        // Once Websocket is open, check the tables in the DeltaLake
        this.WS.addEventListener('open', () => {
          this.checkTables()
        })
      },
      processData() {
        this.messageoutput = "Processing Request..."
        this.WS.send(JSON.stringify({ request_to: 'delta', request_endpoint: 'ingestdata', request_args: { 
          request_tablename : this.tableName,
          request_folderpath : this.folderPath,
          request_method : this.selectedOptions
        } }));
        this.checkTables()
      },
      checkTables(){
        // Check the status of DeltaTables through a request
        this.WS.send(JSON.stringify({ request_to: 'duck', request_endpoint: 'checktable', request_args: {}}))
        // Query the __deltalake_dir table
        this.WS.send(JSON.stringify({ request_to: 'duck', request_endpoint: 'querydata', request_args: { 
            request_contents: ["Table"],
            request_query :  "SELECT * FROM postgres.__deltalake_dir",
            request_render : 100
          } }));
      }
    },
    created() {
        this.connectWebSocket(); // Initialize the WebSocket connection when the component is created
    },
}
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