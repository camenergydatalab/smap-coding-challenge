<template>
  <div>
    <div id="chart" />
  </div>
</template>

<script>
  import c3 from 'c3'

  export default {
    props: {
      c3Obj: {
        default: () => ({}),
        type: Object,
      },
    },
    data() {
      return {
      }
    },
    watch: {
      c3Obj() {
        c3.generate(this.c3Obj)
      }
    },
  }
</script>
