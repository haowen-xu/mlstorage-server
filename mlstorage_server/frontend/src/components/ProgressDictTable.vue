<template>
  <table class="table table-sm dict-table">
    <tbody>
    <tr v-if="value.epoch !== undefined">
      <th class="fieldName">epoch</th>
      <td class="fieldValue">{{ value.epoch }}<span v-if="value.max_epoch !== undefined">/{{ value.max_epoch }}</span></td>
    </tr>
    <tr v-if="value.batch !== undefined">
      <th class="fieldName">batch</th>
      <td class="fieldValue">{{ value.batch }}<span v-if="value.max_batch !== undefined">/{{ value.max_batch }}</span></td>
    </tr>
    <tr v-if="value.step !== undefined">
      <th class="fieldName">step</th>
      <td class="fieldValue">{{ value.step }}</td>
    </tr>
    <tr v-if="eta">
      <th class="fieldName">eta</th>
      <td class="fieldValue">{{ eta }}</td>
    </tr>
    <tr v-if="elapsed">
      <th class="fieldName">elapsed</th>
      <td class="fieldValue">{{ elapsed }}</td>
    </tr>
    <tr v-if="epochTime">
      <th class="fieldName">epoch time</th>
      <td class="fieldValue">{{ epochTime }}</td>
    </tr>
    <tr v-if="batchTime">
      <th class="fieldName">batch time</th>
      <td class="fieldValue">{{ batchTime }}</td>
    </tr>
<!--    <tr v-for="item in sortedMetrics" :key="item.key">-->
<!--      <th class="fieldName">{{ item.key }}</th>-->
<!--      <td class="fieldValue"><metric-value :metric-key="item.key" :metric-value="item.value"/></td>-->
<!--    </tr>-->
    </tbody>
  </table>
</template>

<script>
import natsort from 'natsort';
import MetricValue from './MetricValue';
import { formatDuration } from '../libs/utils';

export default {
  components: {MetricValue},

  props: ['value'],

  computed: {
    eta () {
      if (this.value.eta) {
        return formatDuration(this.value.eta, 0, true);
      }
    },

    elapsed () {
      if (this.value.elapsed) {
        return formatDuration(this.value.elapsed, 3);
      }
    },

    epochTime () {
      if (this.value.epoch_time) {
        return formatDuration(this.value.epoch_time, 3);
      }
    },

    batchTime () {
      if (this.value.batch_time) {
        return formatDuration(this.value.batch_time, 3);
      }
    },

    sortedMetrics () {
      const metrics = this.value.batch_metrics || {};
      const keys = Object.keys(metrics);
      keys.sort(natsort({ insensitive: true }));
      return keys.map((k) => (
        { key: k, value: metrics[k] }
      ));
    }
  }
};
</script>

<style lang="scss" scoped>
.dict-table {
  margin-bottom: 0;
  tr:first-child {
    td, th {
      border-top: none;
    }
  }
  .fieldName {
    width: 30%;
  }
  .fieldValue {
    word-wrap: break-word;
  }
  .boldItem {
    font-weight: bold;
  }
}
</style>
