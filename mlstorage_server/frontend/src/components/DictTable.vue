<template>
  <table class="table table-sm dict-table" v-if="sortedItems">
    <tbody>
    <tr v-for="item in sortedItems"
        :key="item.key"
        :class="item.bold ? ['table-primary', 'boldItem'] : []">
      <th class="fieldName">{{ item.key }}</th>
      <td class="fieldValue"><metric-value :value="item.value"/></td>
    </tr>
    </tbody>
  </table>
</template>

<script>
import natsort from 'natsort';
import MetricValue from './MetricValue';

export default {
  components: {MetricValue},

  props: {
    items: {
      default: null
    },
    boldKeys: {
      default: null
    }
  },

  computed: {
    sortedItems () {
      const items = this.items || {};
      const boldKeys = this.boldKeys || [];
      const keys = Object.keys(items);
      keys.sort(natsort({ insensitive: true }));
      return keys.map((k) => (
        { key: k, value: items[k], bold: boldKeys.includes(k) }
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
