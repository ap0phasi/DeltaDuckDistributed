<template>
    <Line :data="chartData" :options="chartOptions" />
</template>
<script>
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js'
import { Line } from 'vue-chartjs'

const getCssVariable = (variable) => {
  return getComputedStyle(document.documentElement).getPropertyValue(variable);
};

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
)

export default {
 name: 'App',

 data: () => ({
    chartData: {
      labels: ['January', 'February', 'March', 'April', 'May', 'June', 'July'],
      datasets: [
        {
          label: 'Data One',
          backgroundColor: '#f87979',
          borderColor: '#f87979',
          tension: 0.2,
          data: [40, 39, 10, 40, 39, 80, 40]
        },
        {
          label: 'Data Two',
          backgroundColor: '#111111',
          borderColor: '#111111',
          tension: 0.2,
          data: [23, 13, 61, 35, 12, 23, 45]
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
  Line,
 },
};
</script>
<style scoped>

</style>
