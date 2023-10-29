<template>
    <Sidebar />
    <v-container>
      <!-- Card with inputs and button -->
      <v-card class="mb-5">
        <v-row class="fill-height">
          <v-col cols="4" md="4" class="pl-5 pt-5 d-flex align-center justify-center">
            <v-textarea label="SQL Query" v-model="inputText"></v-textarea>
          </v-col>
          <v-col cols="4" md="4" class="pt-5 align-center justify-center">
            <v-select
              :items="options"
              label="Render Query As"
              v-model="selectedOptions"
              multiple
            ></v-select>
          </v-col>
          <v-col cols="4" md="4" class="pt-5 d-flex justify-center">
            <v-btn color="primary" @click="processData">Submit</v-btn>
          </v-col>
        </v-row>
      </v-card>
  
      <!-- Text outputs -->
      <v-row>
        <v-col>
          <v-card v-if="selectedOptions.includes('Message')">
            <h3 class="pl-4">Message Output</h3>
            <p>{{ output1 }}</p>
          </v-card>
        </v-col>
      </v-row>
      <v-row>
        <v-col>
          <v-card v-if="selectedOptions.includes('Plot')">
            <h3 class="pl-4">Timeseries Plot</h3>
            <Line />
          </v-card>
        </v-col>
      </v-row>
      <v-row>
        <v-col>
          <v-card v-if="selectedOptions.includes('Table')">
            <h3 class="pl-4">Table Output</h3>
            <Vue3EasyDataTable
              table-class-name="customize-table"
              :headers="headers"
              :items="items"
              :sort-by="sortBy"
              :sort-type="sortType"
            />
          </v-card>
        </v-col>
      </v-row>
    </v-container>
  </template>
  
  <script setup>
    import Sidebar from "@/components/Sidebar.vue";
    import Line from "@/components/Line.vue";
    import Vue3EasyDataTable from 'vue3-easy-data-table'
    import 'vue3-easy-data-table/dist/style.css';
  </script>
  
  <script>
    export default {
      components: { 
        Line,
        Vue3EasyDataTable 
  
      },
      data() {
        return {
          sortBy: "weight",
          sortType: "desc",
          headers: [
            { text: "PLAYER", value: "player" },
            { text: "TEAM", value: "team"},
            { text: "NUMBER", value: "number"},
            { text: "POSITION", value: "position"},
            { text: "HEIGHT", value: "indicator.height"},
            { text: "WEIGHT (lbs)", value: "indicator.weight", sortable: true},
            { text: "LAST ATTENDED", value: "lastAttended", width: 200},
            { text: "COUNTRY", value: "country"},
          ],
          items: [
            { player: "Stephen Curry", team: "GSW", number: 30, position: 'G', indicator: {"height": '6-2', "weight": 185}, lastAttended: "Davidson", country: "USA"},
            { player: "Lebron James", team: "LAL", number: 6, position: 'F', indicator: {"height": '6-9', "weight": 250}, lastAttended: "St. Vincent-St. Mary HS (OH)", country: "USA"},
            { player: "Kevin Durant", team: "BKN", number: 7, position: 'F', indicator: {"height": '6-10', "weight": 240}, lastAttended: "Texas-Austin", country: "USA"},
            { player: "Giannis Antetokounmpo", team: "MIL", number: 34, position: 'F', indicator: {"height": '6-11', "weight": 242}, lastAttended: "Filathlitikos", country: "Greece"},
            { player: "Stephen Curry", team: "GSW", number: 30, position: 'G', indicator: {"height": '6-2', "weight": 185}, lastAttended: "Davidson", country: "USA"},
            { player: "Lebron James", team: "LAL", number: 6, position: 'F', indicator: {"height": '6-9', "weight": 250}, lastAttended: "St. Vincent-St. Mary HS (OH)", country: "USA"},
            { player: "Kevin Durant", team: "BKN", number: 7, position: 'F', indicator: {"height": '6-10', "weight": 240}, lastAttended: "Texas-Austin", country: "USA"},
            { player: "Giannis Antetokounmpo", team: "MIL", number: 34, position: 'F', indicator: {"height": '6-11', "weight": 242}, lastAttended: "Filathlitikos", country: "Greece"},
            { player: "Stephen Curry", team: "GSW", number: 30, position: 'G', indicator: {"height": '6-2', "weight": 185}, lastAttended: "Davidson", country: "USA"},
            { player: "Lebron James", team: "LAL", number: 6, position: 'F', indicator: {"height": '6-9', "weight": 250}, lastAttended: "St. Vincent-St. Mary HS (OH)", country: "USA"},
            { player: "Kevin Durant", team: "BKN", number: 7, position: 'F', indicator: {"height": '6-10', "weight": 240}, lastAttended: "Texas-Austin", country: "USA"},
            { player: "Giannis Antetokounmpo", team: "MIL", number: 34, position: 'F', indicator: {"height": '6-11', "weight": 242}, lastAttended: "Filathlitikos", country: "Greece"},
            { player: "Stephen Curry", team: "GSW", number: 30, position: 'G', indicator: {"height": '6-2', "weight": 185}, lastAttended: "Davidson", country: "USA"},
            { player: "Lebron James", team: "LAL", number: 6, position: 'F', indicator: {"height": '6-9', "weight": 250}, lastAttended: "St. Vincent-St. Mary HS (OH)", country: "USA"},
            { player: "Kevin Durant", team: "BKN", number: 7, position: 'F', indicator: {"height": '6-10', "weight": 240}, lastAttended: "Texas-Austin", country: "USA"},
            { player: "Giannis Antetokounmpo", team: "MIL", number: 34, position: 'F', indicator: {"height": '6-11', "weight": 242}, lastAttended: "Filathlitikos", country: "Greece"},
            { player: "Stephen Curry", team: "GSW", number: 30, position: 'G', indicator: {"height": '6-2', "weight": 185}, lastAttended: "Davidson", country: "USA"},
            { player: "Lebron James", team: "LAL", number: 6, position: 'F', indicator: {"height": '6-9', "weight": 250}, lastAttended: "St. Vincent-St. Mary HS (OH)", country: "USA"},
            { player: "Kevin Durant", team: "BKN", number: 7, position: 'F', indicator: {"height": '6-10', "weight": 240}, lastAttended: "Texas-Austin", country: "USA"},
            { player: "Giannis Antetokounmpo", team: "MIL", number: 34, position: 'F', indicator: {"height": '6-11', "weight": 242}, lastAttended: "Filathlitikos", country: "Greece"},
            { player: "Stephen Curry", team: "GSW", number: 30, position: 'G', indicator: {"height": '6-2', "weight": 185}, lastAttended: "Davidson", country: "USA"},
            { player: "Lebron James", team: "LAL", number: 6, position: 'F', indicator: {"height": '6-9', "weight": 250}, lastAttended: "St. Vincent-St. Mary HS (OH)", country: "USA"},
            { player: "Kevin Durant", team: "BKN", number: 7, position: 'F', indicator: {"height": '6-10', "weight": 240}, lastAttended: "Texas-Austin", country: "USA"},
            { player: "Giannis Antetokounmpo", team: "MIL", number: 34, position: 'F', indicator: {"height": '6-11', "weight": 242}, lastAttended: "Filathlitikos", country: "Greece"},
            { player: "Stephen Curry", team: "GSW", number: 30, position: 'G', indicator: {"height": '6-2', "weight": 185}, lastAttended: "Davidson", country: "USA"},
            { player: "Lebron James", team: "LAL", number: 6, position: 'F', indicator: {"height": '6-9', "weight": 250}, lastAttended: "St. Vincent-St. Mary HS (OH)", country: "USA"},
            { player: "Kevin Durant", team: "BKN", number: 7, position: 'F', indicator: {"height": '6-10', "weight": 240}, lastAttended: "Texas-Austin", country: "USA"},
            { player: "Giannis Antetokounmpo", team: "MIL", number: 34, position: 'F', indicator: {"height": '6-11', "weight": 242}, lastAttended: "Filathlitikos", country: "Greece"},
            { player: "Stephen Curry", team: "GSW", number: 30, position: 'G', indicator: {"height": '6-2', "weight": 185}, lastAttended: "Davidson", country: "USA"},
            { player: "Lebron James", team: "LAL", number: 6, position: 'F', indicator: {"height": '6-9', "weight": 250}, lastAttended: "St. Vincent-St. Mary HS (OH)", country: "USA"},
            { player: "Kevin Durant", team: "BKN", number: 7, position: 'F', indicator: {"height": '6-10', "weight": 240}, lastAttended: "Texas-Austin", country: "USA"},
            { player: "Giannis Antetokounmpo", team: "MIL", number: 34, position: 'F', indicator: {"height": '6-11', "weight": 242}, lastAttended: "Filathlitikos", country: "Greece"},
          ],
          inputText: '',
          selectedOptions: [],
          options: ['Message', 'Plot', 'Table'],
          output1: '',
          output2: '',
          output3: '',
        };
      },
      methods: {
        processData() {
          // Sample processing logic
          this.output1 = `Entered text: ${this.inputText}`;
          this.output2 = `Selected options: ${this.selectedOptions.join(', ')}`;
          this.output3 = `Random output: ${Math.random()}`;
        },
      },
    };
  </script>
  
  <style>
  .customize-table {
    --easy-table-border: 1px solid var(--accent_1);
    --easy-table-row-border: 1px solid var(--accent_1);
  
    --easy-table-header-font-size: 14px;
    --easy-table-header-height: 50px;
    --easy-table-header-font-color: var(--text);
    --easy-table-header-background-color: var(--accent_2);
  
    --easy-table-header-item-padding: 10px 15px;
  
    --easy-table-body-even-row-font-color: var(--text);
    --easy-table-body-even-row-background-color: var(--text);
  
    --easy-table-body-row-font-color: var(--text);
    --easy-table-body-row-background-color: var(--surface);
    --easy-table-body-row-height: 50px;
    --easy-table-body-row-font-size: 14px;
  
    --easy-table-body-row-hover-font-color: var(--primary);
    --easy-table-body-row-hover-background-color: var(--text);
  
    --easy-table-body-item-padding: 10px 15px;
  
    --easy-table-footer-background-color: var(--surface);
    --easy-table-footer-font-color: var(--text);
    --easy-table-footer-font-size: 14px;
    --easy-table-footer-padding: 0px 10px;
    --easy-table-footer-height: 50px;
  
    --easy-table-rows-per-page-selector-width: 70px;
    --easy-table-rows-per-page-selector-option-padding: 10px;
    --easy-table-rows-per-page-selector-z-index: 1;
  
  
    --easy-table-scrollbar-track-color: var(--primary);
    --easy-table-scrollbar-color: var(--primary);
    --easy-table-scrollbar-thumb-color: var(--highlight);
    --easy-table-scrollbar-corner-color: var(--highlight);
  
    --easy-table-loading-mask-background-color: var(--primary);
  }
  </style>