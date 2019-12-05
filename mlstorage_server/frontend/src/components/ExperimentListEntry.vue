<template>
  <b-list-group-item :variant="statusClass" class="flex-column align-items-start" @click="onItemClick" href="#">
    <div class="d-flex w-100 justify-content-between flex-md-row flex-column">
      <h5 class="mb-1 word-wrap">
        <b-form-checkbox v-if="showCheckbox" @change="onSelectChanged" v-model="checked"
                         class="experimentCheckbox"></b-form-checkbox>
        <v-icon name="star" class="star-icon" v-if="hasStarTag"></v-icon>
        <span>{{ doc.name }}</span>
      </h5>
      <small class="text-muted">{{ dateText }}</small>
    </div>
    <div v-if="doc.description">
      {{ doc.description }}
    </div>
    <div v-if="progressItems || doc.result" class="results d-flex justify-content-start flex-wrap">
      <div v-for="progressItem in progressItems" :key="'progress.' + progressItem.key"
           class="resultItem d-flex justify-content-start">
        <div class="resultKey">{{ progressItem.key }}</div>
        <div class="resultValue">{{ progressItem.value }}</div>
      </div>
      <div v-for="metricItem in metricItems" :key="'result.' + metricItem.key"
           class="resultItem d-flex justify-content-start">
        <div class="resultKey">{{ metricItem.key }}</div>
        <div class="resultValue">{{ metricItem.value }}</div>
      </div>
    </div>
    <div v-if="filteredTags" class="tags">
      <b-badge v-for="tag in filteredTags" :key="tag" :variant="statusClass || 'secondary'">{{ tag }}</b-badge>
    </div>
  </b-list-group-item>
</template>

<script>
import TimeDiff from '../libs/timeDiff';
import { statusToBootstrapClass, formatMetricValue } from '../libs/utils';

export default {
  props: {
    doc: {
      type: Object
    },
    showCheckbox: {
      type: Boolean,
      default: true
    },
    selectedExperiments: {
      type: Array
    }
  },

  data () {
    return {
      expanded: false,
      checked: (this.selectedExperiments && this.selectedExperiments.filter(d => d.id === this.doc.id).length > 0),
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
    progressItems () {
      if (this.doc.progress) {
        const progress = this.doc.progress;
        const totalEpochs = progress.total_epochs || progress.max_epoch;
        const totalBatches = progress.total_batches || progress.max_batch;
        const totalSteps = progress.total_steps || progress.max_step;
        const keys = ['stage', 'epoch', 'batch', 'step', 'eta'].filter(s => progress[s] ? s : null);
        return keys.map(key => {
          let value = progress[key];
          // if `key` is a counter, then append the maximnum value to the counter
          if (key === 'epoch' && totalEpochs) {
            value = `${value}/${totalEpochs}`;
          } else if (key === 'batch' && totalBatches) {
            value = `${value}/${totalBatches}`;
          } else if (key === 'step' && totalSteps) {
            value = `${value}/${totalSteps}`;
          }
          return {key: key, value: value};
        });
      } else {
        return [];
      }
    },

    metricItems () {
      if (this.doc.result) {
        const keys = Object.keys(this.doc.result);
        keys.sort();
        return keys.map(key => {
          return {
            key: key,
            value: formatMetricValue(this.doc.result[key])
          };
        });
      } else {
        return [];
      }
    },

    hasStarTag () {
      return this.doc.tags && (this.doc.tags.indexOf('star') >= 0);
    },

    filteredTags () {
      return this.doc.tags && this.doc.tags.filter(s => s !== 'star');
    }
  },

  watch: {
    doc (doc) {
      this.timeDiff.setTimestamp(doc.heartbeat);
    },

    selectedExperiments (value) {
      this.checked = (value && value.filter(d => d.id === this.doc.id).length > 0);
    }
  }
};
</script>

<style lang="scss" scoped>
  .star-icon {
    margin-right: 5px;
  }
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
      .resultStage {
        font-weight: bold;
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
  .word-wrap {
    word-wrap: break-word;
  }
</style>
