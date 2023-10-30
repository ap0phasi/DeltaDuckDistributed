<template>
    <button @click="processData">Async</button>
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
    name: 'MyChartComponent',
    components: {
        Line,
    },
    data() {
      return {
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
        // responsive: true,
        // plugins: {
        //     legend: {
        //         labels: { 
        //             color: getCssVariable('--text')// Sets the legend text color
        //         }
        //     },
        //     tooltip: {
        //         titleFont: {
        //             color: getCssVariable('--text')
        //         },
        //         bodyFont: {
        //             color: getCssVariable('--text')
        //         }
        //     }
        // },
        // scales: {
        //     x: {
        //         ticks: {
        //             color: getCssVariable('--text') // Sets x-axis tick labels to white
        //         },
        //         grid: {
        //             color: getCssVariable('--accent_1') // Adjust grid line color if needed
        //         }
        //     },
        //     y: {
        //         ticks: {
        //             color: getCssVariable('--text') // Sets y-axis tick labels to white
        //         },
        //         grid: {
        //             color: getCssVariable('--accent_1') // Adjust grid line color if needed
        //         }
        //     }
        // }
    }
      }
    },
    methods: {
        initWebSocket() {
            this.websocket = new WebSocket('ws://localhost:8081/ws'); // Replace with your server's WebSocket URL
            // Define an event listener to handle incoming messages
            this.websocket.addEventListener('message', (event) => {
                const data = JSON.parse(event.data);
                if (data.respond_to === 'duck') {
                    if (data.response_contents.includes('chart')){
                        this.chartData = data.chartData;
                        }
                    }
            });
        },
        processData() {
          this.websocket.send(JSON.stringify({ request_from: 'duck', request_contents: ['chart'], request_query: 'hi' }));
        },
    },
    created() {
        this.initWebSocket(); // Initialize the WebSocket connection when the component is created
    },
  }
  </script>
  
