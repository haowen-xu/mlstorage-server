<template>
  <b-container fluid style="padding-top: 15px">
    <b-row>
      <b-col>
        <div v-if="docs" :class="hasNavigation ? ['has-navigation']: []">
          <b-list-group class="experiment-list">
            <experiment-list-entry v-for="doc in docs" :key="doc.id" :doc="doc">
            </experiment-list-entry>

          </b-list-group>
          <b-button-toolbar v-if="hasNavigation"
                            key-nav aria-label="Toolbar with button groups"
                            class="d-flex w-100 justify-content-center fixed-bottom navigation-bar">
            <b-button-group class="mx-1">
              <b-btn :disabled="!hasPrevPage" @click="prevPage">&lsaquo;</b-btn>
            </b-button-group>
            <b-button-group class="mx-1">
              <b-btn>{{ this.thePageId }}</b-btn>
            </b-button-group>
            <b-button-group class="mx-1">
              <b-btn :disabled="!hasNextPage" @click="nextPage">&rsaquo;</b-btn>
            </b-button-group>
          </b-button-toolbar>
        </div>
      </b-col>
    </b-row>
  </b-container>
</template>

<script>
import axios from 'axios';
import eventBus from '../libs/eventBus';
import ExperimentListEntry from './ExperimentListEntry';

export default {
  components: {
    ExperimentListEntry
  },

  props: {
    query: {
      type: Object,
      default: () => {}
    },
    pageSize: {
      type: Number,
      default: 10
    },
    pageId: {
      type: Number,
      default: 1
    }
  },

  data () {
    return {
      docs: null,
      thePageId: this.pageId,
      hasNextPage: true
    };
  },

  mounted () {
    this.load();
    eventBus.addReloader(this.load);
    this.autoReloader = setInterval(() => this.load(), 120 * 1000);
  },

  destroyed () {
    eventBus.removeReloader(this.load);
    if (this._autoReloader) {
      clearInterval(this._autoReloader);
      this.autoReloader = null;
    }
  },

  watch: {
    query () {
      this.load();
    },
    pageSize () {
      this.load();
    },
    pageId (pageId) {
      this.thePageId = pageId;
      this.load();
    }
  },

  methods: {
    load () {
      const pageId = this.thePageId;
      eventBus.setLoadingFlag(true);
      axios.post(`/v1/_query?timestamp=1&skip=${(pageId - 1) * this.pageSize}&limit=${this.pageSize + 1}`, {
        body: this.query
      })
        .then((resp) => {
          if (pageId === this.thePageId) {
            const docs = resp.data;
            if (docs.length > this.pageSize) {
              this.hasNextPage = true;
              this.docs = resp.data.slice(0, resp.data.length - 1);
            } else {
              this.hasNextPage = false;
              this.docs = resp.data;
            }
            eventBus.setLoadingFlag(false);
            eventBus.unsetError();
          }
        })
        .catch((error) => {
          this.docs = null;
          eventBus.setLoadingFlag(false);
          eventBus.setError({
            message: error.response ? error.response.statusText : error,
            title: 'Failed to load experiments'
          });
        });
    },

    prevPage () {
      if (this.hasPrevPage) {
        this.thePageId -= 1;
        this.$emit('pageIdChanged', this.thePageId);
        this.load();
      }
    },

    nextPage () {
      if (this.hasNextPage) {
        this.thePageId += 1;
        this.$emit('pageIdChanged', this.thePageId);
        this.load();
      }
    },

    hasNavigation () {
      return this.docs && (this.hasPrevPage || this.hasNextPage);
    }
  },

  computed: {
    hasPrevPage () {
      return this.thePageId > 1;
    }
  }
};
</script>

<style lang="scss" scoped>
.has-navigation .experiment-list {
  padding-bottom: 58px;
}
.navigation-bar {
  padding: 15px 0 5px;
  // background: white;
}
</style>
