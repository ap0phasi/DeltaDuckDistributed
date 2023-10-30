<template>
    <v-navigation-drawer 
        v-model="drawer" 
        :rail="rail"
        :width="260" 
        color=var(--sidebar) 
        class="rounded-e-xl"
    >
        <!-- Top Sheet Component -->
        <v-sheet color=var(--sidebar_accent_1) class="pa-4 rounded-te-xl text-center">
            <div class="icon-text" v-if="!rail">
                =(^)
            </div>
            <div class="icon-text" v-else>
                &nbsp;
            </div>
        </v-sheet>
        
        <!-- Tray Collapse Button -->
        <v-btn icon @click.stop="rail = !rail" variant="text">
           <v-icon>{{ rail ? 'mdi mdi-chevron-right' : 'mdi mdi-chevron-left' }}</v-icon>
        </v-btn>

        <!-- Navigation Links -->
        <v-list>
            <v-list-item
                v-for="(item, i) in links"
                :key="i"
                :value="item"
                :ripple="false"
                :to="item.route"
            >
                <template v-slot:prepend>
                <v-icon :icon="item.icon" color=var(--sidebar_icon_1)></v-icon>
                </template>

                <v-list-item-title v-text="item.text"></v-list-item-title>
            </v-list-item>
        </v-list>
    </v-navigation-drawer>
</template>

<script setup>
import { ref } from "vue";
const links = [
  { text: "DeltaLake Manage", icon: "mdi mdi-database-outline" , route: "/delta"},
  { text: "DuckDB Analysis", icon: "mdi mdi-chart-areaspline" , route: "/duck"},
  { text: "Settings", icon: "mdi mdi-cog-outline" , route: "/settings"},
];
const drawer = ref(null);
</script>

<script>
export default {
  data: () => ({
    drawer: true,
    rail: false,
  }),
};
</script>
<style scoped>
    .v-list-item--active::before {
        content: '';
        position: absolute;
        left: 255px;
        top: 2px;
        bottom: 2px;
        width: 5px;
        background-color: var(--highlight); 
        box-shadow: 0 0 5px var(--highlight);
    }
</style>