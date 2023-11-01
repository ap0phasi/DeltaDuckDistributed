<template>
    <Vue3EasyDataTable
              table-class-name="customize-table"
              :headers="headers"
              :items="items"
              :sort-by="sortBy"
              :sort-type="sortType"
            />
</template>

<script setup>
    import Vue3EasyDataTable from 'vue3-easy-data-table'
    import 'vue3-easy-data-table/dist/style.css';
</script>
  
<script>
// Handle Websocket Connection
import WS from '@/services/ws';

export default {
    components: { 
    Vue3EasyDataTable 

    },
    data() {
    return {
        headers: [
        ],
        items: [
        ],
    };
    },
    created() {
    this.connectWebSocket();
    },
    methods: {
      connectWebSocket() {
            // Define an event listener to handle incoming messages
            WS.onmessage = (event) => {
              console.log('Message to Table:')
                const data = JSON.parse(event.data);
                if (data.respond_to === 'duck') {
                    if (data.response_contents.includes('Table')){
                        this.headers = data.data.table.headers;
                        this.items = data.data.table.items;
                        }
                    }
            }
        },
    },
}
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