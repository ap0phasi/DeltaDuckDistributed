<template>
  <Sidebar />
  <v-container>
      <!-- Card with inputs and button -->
      <v-card class="mb-5">
        <v-row class="fill-height">
          <v-col cols="3" md="3" class="pl-5 pt-5 align-center justify-center">
            <v-text-field label="CSV Folder Path" v-model="folderPath"></v-text-field>
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
          <v-col cols="3" md="3" class="pt-5 align-center justify-center">
            <v-btn color="primary" @click="processData">Load</v-btn>
          </v-col>
        </v-row>
      </v-card>
      <v-row>
        <v-col>
          <v-card>
            <h3 class="pl-4">Delta Tables</h3>
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
</script>

<script>
export default {
  data() {
        return {
          selectedOptions: [],
          options: ['Append','Overwrite'],
        }
      }
}
</script>