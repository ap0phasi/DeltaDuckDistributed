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

// Handle Websocket Connection
import WS from '@/services/ws';

  export default {
    name: 'MyChartComponent',
    components: {
        Line,
    },
    data() {
      return {
        chartData: {
            labels: [],
            datasets: [
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
      }
    },
    mounted() {
    this.connectWebSocket();
    },
    methods: {
      connectWebSocket() {
            // Define an event listener to handle incoming messages
            WS.onmessage = (event) => {
                const data = JSON.parse(event.data);
                if (data.respond_to === 'duck') {
                    if (data.response_contents.includes('Chart')){
                        this.chartData = data.chartData;
                        }
                    }
            }
        },
    },
  }
  </script>
  
