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