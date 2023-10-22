<template>
  <v-app>
    <div>
      <!-- Text Input and Button -->
      <div class="row">
        <div class="col-md-4">
          <input type="text" v-model="textInput" class="form-control" placeholder="Enter text">
        </div>
        <div class="col-md-4">
          <v-select
            v-model="selectedRenderOptions"
            :items="['Message', 'Plot', 'Table']"
            label="Render"
            multiple
            hint="Select how to render data"
            persistent-hint
          ></v-select>
        </div>
        <div class="col-md-4">
          <button @click="handleButtonClick" class="btn btn-primary">Submit</button>
        </div>
        
      </div>

      <!-- BigChart for Timeseries -->
      <div class="row mt-4">
        <div class="col-12">
          <card type="chart">
            <template slot="header">
              <div class="row">
                <div class="col-sm-6" :class="isRTL ? 'text-right' : 'text-left'">
                  <h5 class="card-category">Timeseries Data</h5>
                  <h2 class="card-title">Timeseries Plot</h2>
                </div>
              </div>
            </template>
            <div class="chart-area">
              <line-chart style="height: 100%"
                          ref="bigChart"
                          chart-id="big-line-chart"
                          :chart-data="bigLineChart.chartData"
                          :gradient-colors="bigLineChart.gradientColors"
                          :gradient-stops="bigLineChart.gradientStops"
                          :extra-options="bigLineChart.extraOptions">
              </line-chart>
            </div>
          </card>
        </div>
      </div>

      <!-- Table -->
      <div class="row mt-4">
        <div class="col-12">
          <card class="card">
            <h4 slot="header" class="card-title">Table Title</h4>
            <div class="table-responsive">
              <table class="table">
                <thead>
                  <tr>
                    <th>Column 1</th>
                    <th>Column 2</th>
                    <th>Column 3</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(row, index) in tableData" :key="index">
                    <td>{{ row.column1 }}</td>
                    <td>{{ row.column2 }}</td>
                    <td>{{ row.column3 }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </card>
        </div>
      </div>
    </div>
  </v-app>
</template>

<script>
import LineChart from '@/components/Charts/LineChart';
import config from '@/config';
import * as chartConfigs from '@/components/Charts/config';

export default {
  components: {
    LineChart,
  },
  data() {
    return {
      selectedRenderOptions: [],  // will hold the selected values
      textInput: '',
      bigLineChart: {
          extraOptions: chartConfigs.purpleChartOptions,
          chartData: {
            labels: ['JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC'],
            datasets: [
              {
              label: "Dataset 1",
              fill: true,
              borderColor: config.colors.primary,
              borderWidth: 2,
              borderDash: [],
              borderDashOffset: 0.0,
              pointBackgroundColor: config.colors.primary,
              pointBorderColor: 'rgba(255,255,255,0)',
              pointHoverBackgroundColor: config.colors.primary,
              pointBorderWidth: 20,
              pointHoverRadius: 4,
              pointHoverBorderWidth: 15,
              pointRadius: 4,
              data: [80, 100, 70, 80, 120, 80],
            },
            {
              label: "Dataset 2",
              fill: true,
              borderColor: config.colors.danger,
              borderWidth: 2,
              borderDash: [],
              borderDashOffset: 0.0,
              pointBackgroundColor: config.colors.danger,
              pointBorderColor: 'rgba(255,255,255,0)',
              pointHoverBackgroundColor: config.colors.danger,
              pointBorderWidth: 20,
              pointHoverRadius: 4,
              pointHoverBorderWidth: 15,
              pointRadius: 4,
              data: [70, 80, 90, 100, 100, 60],
            },
          ]
          },
          gradientColors: config.colors.primaryGradient,
          gradientStops: [1, 0.2, 0],
        },
      tableData: [
        { column1: 'Data 1', column2: 'Data 2', column3: 'Data 3' },
        // ... more rows as needed
      ],
    }
  },
  computed: {
      isRTL() {
        return this.$rtl.isRTL;
      },
      disableRTL() {
        if (!this.$rtl.isRTL) {
          this.$rtl.disableRTL();
        }
      },
      toggleNavOpen() {
        let root = document.getElementsByTagName('html')[0];
        root.classList.toggle('nav-open');
      }
  },
  methods: {
      handleButtonClick() {
        console.log('Button clicked with input:', this.textInput);
        // Handle button click event, e.g., fetch new data for the chart or table
      }
    }
};
</script>

<style>
  .v-application {
      background-color: transparent !important;
  }
</style>
