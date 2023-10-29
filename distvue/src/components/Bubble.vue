<template>
    <Bubble :data="chartData" :options="chartOptions" />
</template>
<script>
import {
  Chart as ChartJS,
  Tooltip,
  Legend,
  PointElement,
  LinearScale
} from 'chart.js'
import { Bubble } from 'vue-chartjs'

const getCssVariable = (variable) => {
  return getComputedStyle(document.documentElement).getPropertyValue(variable);
};

ChartJS.register(LinearScale, PointElement, Tooltip, Legend)

export default {
 name: 'App',

 data: () => ({

     chartData: {
       labels: ['VueJs', 'EmberJs', 'ReactJs', 'AngularJs'],
       datasets: [
       {
      label: 'Data One',
      backgroundColor: '#f87979',
      data: [
        {
          x: 20,
          y: 25,
          r: 5
        },
        {
          x: 40,
          y: 10,
          r: 10
        },
        {
          x: 30,
          y: 22,
          r: 30
        }
      ]
    },
    {
      label: 'Data Two',
      backgroundColor: '#7C8CF8',
      data: [
        {
          x: 10,
          y: 30,
          r: 15
        },
        {
          x: 20,
          y: 20,
          r: 10
        },
        {
          x: 15,
          y: 8,
          r: 30
        }
      ]
    }
 ]
     },
     chartOptions: {
        responsive: true,
        plugins: {
            legend: {
                labels: { 
                    color: getCssVariable('--text')// Sets the legend text color
                }
            },
            tooltip: {
                titleFont: {
                    color: getCssVariable('--text')
                },
                bodyFont: {
                    color: getCssVariable('--text')
                }
            }
        },
        scales: {
            x: {
                ticks: {
                    color: getCssVariable('--text') // Sets x-axis tick labels to white
                },
                grid: {
                    color: getCssVariable('--accent_1') // Adjust grid line color if needed
                }
            },
            y: {
                ticks: {
                    color: getCssVariable('--text') // Sets y-axis tick labels to white
                },
                grid: {
                    color: getCssVariable('--accent_1') // Adjust grid line color if needed
                }
            }
        }
    }
 }),
 components: {
  Bubble,
 },
};
</script>
<style scoped>

</style>
