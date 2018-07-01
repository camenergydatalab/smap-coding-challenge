<template>
  <div>
    <select v-model="aggType">
      <option value="sum">合計</option>
      <option value="max">最大</option>
      <option value="avg">平均</option>
      <option value="sum__per_user">合計（一人当たり）</option>
    </select>
    <Chart
      :c3-obj="c3Obj"/>
  </div>
</template>

<script>
  import axios from 'axios'
  import Chart from '../../components/Chart.vue'

  export default {
    components: {
      Chart
    },
    data() {
      return {
        c3Obj: {},
        aggType: 'sum',
      }
    },
    watch: {
      aggType() {
        this.getSummary()
      }
    },
    mounted() {
      this.getSummary()
    },
    methods: {
      getSummary() {
        const url = '/api/consumption_grouped_by_area'
        const config = {
          method: 'get',
          params: {
            agg_type: this.aggType,
          },
        }
        config.withCredentials = true;
        const successFn = (res) => {
          this.c3Obj = res.data
        }
        const errorFn = (error) => {
          console.log(error)
        }
        axios.get(url, config).then(successFn).catch(errorFn);
      },
    },
  }
</script>
