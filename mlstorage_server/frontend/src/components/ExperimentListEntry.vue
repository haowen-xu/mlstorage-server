<template>
  <b-list-group-item :variant="statusClass" class="flex-column align-items-start" @click="onItemClick" href="#">
    <div class="d-flex w-100 justify-content-between flex-md-row flex-column">
      <h5 class="mb-1">
        <b-form-checkbox v-if="showCheckbox" @change="onSelectChanged" v-model="checked"
                         class="experimentCheckbox"></b-form-checkbox>
        <span>{{ doc.name }}</span>
      </h5>
      <small class="text-muted">{{ dateText }}</small>
    </div>
    <div v-if="doc.description">
      {{ doc.description }}
    </div>
    <div v-if="doc.result" class="results d-flex justify-content-start flex-wrap">
      <div v-for="key in sortedResultKeys" :key="key" class="resultItem d-flex justify-content-start">
        <div class="resultKey">{{ key }}</div>
        <div class="resultValue">{{ doc.result[key] }}</div>
      </div>
    </div>
    <div v-if="doc.tags" class="tags">
      <b-badge v-for="tag in doc.tags" :key="tag" :variant="statusClass || 'secondary'">{{ tag }}</b-badge>
    </div>
  </b-list-group-item>
</template>

<script>
import TimeDiff from '../libs/timeDiff';
import { statusToBootstrapClass } from '../libs/utils';

export default {
  props: {
    doc: {
      type: Object
    },
    showCheckbox: {
      type: Boolean,
      default: true
    }
  },

  data () {
    return {
      expanded: false,
      checked: false,
      dateText: null,
      dateDiff: 0,
      statusClass: null
    };
  },

  mounted () {
    this.timeDiff = new TimeDiff();
    this.timeDiff.addWatcher(
      (dateText, dateDiff) => this.timeDiffWatcher(dateText, dateDiff));
    this.timeDiff.setTimestamp(this.doc.heartbeat);
  },

  destroyed () {
    if (this.timeDiff) {
      this.timeDiff.destroy();
    }
  },

  methods: {
    timeDiffWatcher (dateText, dateDiff) {
      this.dateText = dateText;
      this.dateDiff = dateDiff;
      this.statusClass = statusToBootstrapClass(this.doc, this.dateDiff);
    },

    onSelectChanged (checked) {
      this.checked = checked;
      this.$emit('selectChanged', this.doc.id, this.checked);
    },

    onItemClick () {
      if (this.showCheckbox) {
        this.checked = !this.checked;
        this.$emit('selectChanged', this.doc.id, this.checked);
      } else {
        this.$router.push(`/${this.doc.id}/`);
      }
    }
  },

  computed: {
    sortedResultKeys () {
      if (this.doc.result) {
        const keys = Object.keys(this.doc.result);
        keys.sort();
        return keys;
      } else {
        return null;
      }
    }
  },

  watch: {
    doc (doc) {
      this.timeDiff.setTimestamp(doc.heartbeat);
    }
  }
};
</script>

<style lang="scss" scoped>
.tags {
  span { margin-right: 5px; }
  span:last-child { margin-right: 0; }
}
.results {
  .resultItem {
    padding-right: 10px;
    .resultKey {
      font-weight: bold;
      padding-right: 5px;
    }
    .resultKey:after {
      content: ':';
    }
  }
  .resultItem:last-child {
    padding-right: 0;
  }
}
.experimentCheckbox {
  display: inline;
  margin-right: 5px;
}
</style>