import Vue from 'vue';
import Vuetify from 'vuetify';
import 'vuetify/dist/vuetify.min.css';  // Ensure you are using css-loader

Vue.use(Vuetify);

const opts = {};  // Here you can pass Vuetify options if needed

export default new Vuetify(opts);