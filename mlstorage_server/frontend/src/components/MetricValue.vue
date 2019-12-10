<template>
  <div>{{ this.meanStr }}<span v-if="this.hasStd"> (&pm;{{ this.stdStr }})</span></div>
</template>

<script>
export default {
  props: ['value'],

  computed: {
    isStatsDict () {
      if (typeof this.value === 'object' && this.value !== null && !Array.isArray(this.value) &&
          this.value.mean !== undefined) {
        const keys = Object.keys(this.value);
        if (keys.length === 1 || (keys.length === 2 && (keys.indexOf('std') >= 0 || keys.indexOf('stddev') >= 0))) {
          return true;
        }
      }
    },

    mean () {
      return this.isStatsDict ? this.value.mean : this.value;
    },

    std () {
      return this.isStatsDict ? (this.value.std || this.value.stddev) : undefined;
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
      if (typeof val === 'number') {
        let ret = val.toPrecision(6);
        if (ret.indexOf('.') >= 0) {
          ret = ret.replace(/0+$/, '');
          ret = ret.replace(/\.$/, '');
        }
        return ret;
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
