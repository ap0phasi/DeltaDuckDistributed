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