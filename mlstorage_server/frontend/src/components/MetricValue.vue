<template>
  <div>{{ this.meanStr }}<span v-if="this.hasStd"> (&pm;{{ this.stdStr }})</span></div>
</template>

<script>
export default {
  props: ['metricKey', 'metricValue'],

  computed: {
    isStatsDict () {
      if (typeof this.metricValue === 'object' && this.metricValue !== null && !Array.isArray(this.metricValue) &&
          this.metricValue.mean !== undefined) {
        const keys = Object.keys(this.metricValue);
        if (keys.length === 1 || (keys.length === 2 && (keys.indexOf('std') >= 0 || keys.indexOf('stddev') >= 0))) {
          return true;
        }
      }
    },

    mean () {
      return this.isStatsDict ? this.metricValue.mean : this.metricValue;
    },

    std () {
      return this.isStatsDict ? (this.metricValue.std || this.metricValue.stddev) : undefined;
    },

    hasStd () {
      return this.std !== undefined;
    },

    meanStr () {
      return this.formatValue(this.mean);
    },

    stdStr () {
      return this.formatValue(this.std);
    }
  },

  methods: {
    formatValue (val) {
      if (val === null) {
        return 'null';
      }
      if (typeof val === 'string') {
        return val;
      }
      if (this.metricKey !== 'step' && this.metricKey !== 'epoch' && this.metricKey !== 'batch' &&
            this.metricKey !== 'max_step' && this.metricKey !== 'max_epoch' && this.metricKey !== 'max_batch' &&
            this.metricKey !== 'total_steps' && this.metricKey !== 'total_epochs' && this.metricKey !== 'total_batches') {
        // for counters, we shall not format it as real value
        if (typeof val === 'number') {
          let ret = val.toPrecision(6);
          if (ret.indexOf('.') >= 0) {
            ret = ret.replace(/0+$/, '');
            ret = ret.replace(/\.$/, '');
          }
          return ret;
        }
      }
      if (typeof val === 'object' && Object.getPrototypeOf(val).toString === val.toString) {
        return JSON.stringify(val, null, 2);
      }
      return String(val);
    }
  }
};
</script>

<style scoped>

</style>
