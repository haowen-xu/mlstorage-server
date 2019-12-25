<template>
  <div class="d-flex justify-content-start">
    <div class="stageName d-flex justify-content-start">
      {{ stageName }}
    </div>
    <div v-if="value.epoch !== undefined" class="resultItem d-flex justify-content-start">
      <div class="resultKey">epoch</div>
      <div class="resultValue">{{ value.epoch }}<span v-if="value.max_epoch !== undefined">/{{ value.max_epoch }}</span></div>
    </div>
    <div v-if="value.batch !== undefined" class="resultItem d-flex justify-content-start">
      <div class="resultKey">batch</div>
      <div class="resultValue">{{ value.batch }}<span v-if="value.max_batch !== undefined">/{{ value.max_batch }}</span></div>
    </div>
    <div v-if="eta" class="resultItem d-flex justify-content-start">
      <div class="resultKey">eta</div>
      <div class="resultValue">{{ eta }}</div>
    </div>
  </div>
</template>

<script>
import natsort from 'natsort';
import MetricValue from './MetricValue';
import { formatDuration } from '../libs/utils';

export default {
  components: {MetricValue},

  props: ['value', 'stageName'],

  computed: {
    eta () {
      if (this.value.eta) {
        return formatDuration(this.value.eta, 3);
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
  .stageName {
    font-weight: bold;
    padding-right: 10px;
  }
  .resultItem {
    padding-right: 10px;
    .resultKey {
      font-weight: bold;
      padding-right: 5px;
    }
    .resultKey:after {
      content: ':';
    }
    .resultStage {
      font-weight: bold;
    }
  }
  .resultItem:last-child {
    padding-right: 0;
  }
</style>
