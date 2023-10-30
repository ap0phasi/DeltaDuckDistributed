# DeltaDuckDistributed

## Development

### Initial VueJS Build
From command line
'''
npm create vuetify
'''
Project Name: distvue
Preset: Base
Use TypeScript: No
Dependencies: npm

'''
cd distvue
npm install @mdi/font -D
npm i vue-chartjs chart.js
code .
npm run dev
'''

We now have the general components we will need for app development.
We will start with setting up a simple two page application with a collapsible
sidebar for navigation. 

#### App Style Setup

First we will add some style helpers to our App.Vue:

```
<style lang="scss">
:root {
	--primary: #4ade80;
	--sidebar: #22c55e;
}
</style>
```

#### Sidebar Construction

First we will add a Sidebar.vue script to src/components. To start, we will just make a simple sidebar frame like this:

'''
<template>
    <v-navigation-drawer v-model="drawer" :rail="rail" color=var(--sidebar) class="rounded-e-xl">
    </v-navigation-drawer>
</template>

<script setup>
import { ref } from "vue";

const drawer = ref(null);
</script>
'''

Note how the color reference is coming from our style names in App.vue. This will save us a lot of time as we refine our
colors. To render this on the HelloWorld.vue, we simply need to add

```
<Sidebar />
```
To the beginning of our template and 

```
import Sidebar from "@/components/Sidebar.vue";
```

To our script section. 

To finalize the formatting and reactivity of our sidebar, we update the component to the following:

```
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
        left: 247px;
        top: 2px;
        bottom: 2px;
        width: 5px;
        background-color: var(--highlight); 
        box-shadow: 0 0 5px var(--highlight);
    }
</style>
```

#### Routing

Next we need to route everything in our app. We will make three views for our DeltaLake, and Settings pages. Update the router to

'''

// Composables
import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/delta',
    component: () => import('@/layouts/default/Default.vue'),
    children: [
      {
        path: '/delta',
        name: 'Delta',
        // route level code-splitting
        // this generates a separate chunk (about.[hash].js) for this route
        // which is lazy-loaded when the route is visited.
        component: () => import(/* webpackChunkName: "delta" */ '@/views/Delta.vue'),
      },
      {
        path: '/duck',
        name: 'Duck',
        // route level code-splitting
        // this generates a separate chunk (about.[hash].js) for this route
        // which is lazy-loaded when the route is visited.
        component: () => import(/* webpackChunkName: "duck" */ '@/views/Duck.vue'),
      },
      {
        path: '/settings',
        name: 'Settings',
        // route level code-splitting
        // this generates a separate chunk (about.[hash].js) for this route
        // which is lazy-loaded when the route is visited.
        component: () => import(/* webpackChunkName: "settings" */ '@/views/Settings.vue'),
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
})

export default router
'''

#### Themes

Update vuetify.js to the following:

```
/**
 * plugins/vuetify.js
 *
 * Framework documentation: https://vuetifyjs.com`
 */

// Styles
import '@mdi/font/css/materialdesignicons.css'
import 'vuetify/styles'

// Composables
import { createVuetify} from 'vuetify'

const getCssVariable = (variable) => {
  return getComputedStyle(document.documentElement).getPropertyValue(variable);
};

const myCustomLightTheme = {
  dark: false,
  colors: {
    background: getCssVariable('--background'),
    surface: getCssVariable('--surface'),
    primary: getCssVariable('--primary'),
    'primary-darken-1': getCssVariable('--primary-darken-1'),
    secondary: getCssVariable('--secondary'),
    'secondary-darken-1': getCssVariable('--secondary-darken-1'),
    error: getCssVariable('--error'),
    info: getCssVariable('--info'),
    success: getCssVariable('--success'),
    warning: getCssVariable('--warning'),
  },
}

export default createVuetify({
  theme: {
    defaultTheme: 'myCustomLightTheme',
    themes: {
      myCustomLightTheme,
    },
  },
})
```
#### Charts

We will use Chart.js, which should have been added in our setup. Reference components/Line.vue.

#### Tables

We will use vue3-easy-data-table for our table needs:

```
npm add vue3-easy-data-table
```

### Containerization

'''
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

# Copy the Nginx configuration file
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80
EXPOSE 80

# When the container starts, start the nginx server
CMD ["nginx", "-g", "daemon off;"]

'''

Note the nginx.conf fixes the issue of the app throwing 404 when refreshed.