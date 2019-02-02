<template>
  <b-container fluid class="main-container">
    <b-modal id="deleteConfirm"
             title="Confirm to Delete"
             ok-variant="danger"
             ok-title="Delete Them"
             @ok="deleteDocs">
      Really want to delete these experiments?
      <ul>
        <li v-for="doc in selectedExperiments" :key="doc.id">
          <span v-if="doc.name">"{{ doc.name }}" ({{ doc.id }})</span>
          <span v-else>"{{ doc.id }}"</span>
        </li>
      </ul>
    </b-modal>

    <b-row>
      <b-col>
        <div v-if="docs">
          <experiment-list-tool-bar v-if="this.docs && this.docs.length > 0"
                                    :page-id="thePageId"
                                    :has-next-page="hasNextPage"
                                    :has-prev-page="hasPrevPage"
                                    :show-checkbox="showCheckbox"
                                    :selected-experiments="selectedExperiments"
                                    :sort-by="sortBy"
                                    @navToPage="navToPage"
                                    @showCheckboxChanged="showCheckboxChanged"
                                    @sortByChanged="sortByChanged"
                                    @deleteDocs="deleteDocs"
                                    class="top-tool-bar">
          </experiment-list-tool-bar>

          <b-list-group class="experiment-list">
            <experiment-list-entry v-for="doc in docs" :key="doc.id" :doc="doc"
                                   @selectChanged="experimentSelectChanged"
                                   :show-checkbox="showCheckbox">
            </experiment-list-entry>
          </b-list-group>
          <experiment-list-tool-bar v-if="this.docs && this.docs.length > 0"
                                    :page-id="thePageId"
                                    :has-next-page="hasNextPage"
                                    :has-prev-page="hasPrevPage"
                                    :show-checkbox="showCheckbox"
                                    :selected-experiments="selectedExperiments"
                                    :sort-by="sortBy"
                                    @navToPage="navToPage"
                                    @showCheckboxChanged="showCheckboxChanged"
                                    @sortByChanged="sortByChanged"
                                    @deleteDocs="deleteDocs"
                                    class="bottom-tool-bar">
          </experiment-list-tool-bar>
        </div>
      </b-col>
    </b-row>
  </b-container>
</template>

<script>
import axios from 'axios';
import eventBus from '../libs/eventBus';
import userConfig from '../libs/userConfig';
import ExperimentListToolBar from './ExperimentListToolBar';
import ExperimentListEntry from './ExperimentListEntry';

export default {
  components: {
    ExperimentListToolBar,
    ExperimentListEntry
  },

  props: {
    query: {
      type: Object,
      default: () => {}
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
      pageSize: userConfig.dashboard.pageSize,
      hasNextPage: true,
      selectedExperiments: [],
      showCheckbox: false,
      sortBy: userConfig.dashboard.sortBy
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

  computed: {
    hasPrevPage () {
      return this.thePageId > 1;
    },

    selectedCount () {
      return this.selectedExperiments.size;
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
      axios.post(`/v1/_query?timestamp=1&strict=1&sort=${this.sortBy}&` +
                 `skip=${(pageId - 1) * this.pageSize}&limit=${this.pageSize + 1}`, {
        body: this.query
      })
        .then((resp) => {
          this.selectedExperiments = [];
          this.showCheckbox = false;
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
          this.selectedExperiments = [];
          this.showCheckbox = false;
          eventBus.setLoadingFlag(false);
          eventBus.setError({
            message: error.response ? error.response.statusText : error,
            title: 'Failed to load experiments'
          });
        });
    },

    navToPage (pageId) {
      this.$emit('navToPage', pageId);
    },

    sortByChanged (sortBy) {
      this.sortBy = sortBy;
      userConfig.dashboard.sortBy = sortBy;
      this.load();
    },

    experimentSelectChanged (id, selected) {
      if (!selected) {
        if (this.selectedExperiments && this.selectedExperiments.length > 0) {
          for (let i = this.selectedExperiments.length - 1; i >= 0; --i) {
            const doc = this.selectedExperiments[i];
            if (doc.id === id) {
              this.selectedExperiments.splice(i, 1);
            }
          }
        }
      } else {
        if (this.docs && this.docs.length > 0) {
          for (let i = 0; i < this.docs.length; ++i) {
            const doc = this.docs[i];
            if (doc.id === id) {
              this.selectedExperiments.push(doc);
            }
          }
        }
      }
    },

    showCheckboxChanged (showCheckbox) {
      this.showCheckbox = showCheckbox;
    },

    deleteDocs () {
      eventBus.setLoadingFlag(true);
      if (this.selectedExperiments && this.selectedExperiments.length > 0) {
        const docIdList = this.selectedExperiments.map(doc => doc.id);
        const self = this;

        const doDeleteOne = function (i) {
          axios.post(`/v1/_delete/${docIdList[i]}`)
            .then(() => {
              if (i > 0) {
                doDeleteOne(i - 1);
              } else {
                eventBus.setLoadingFlag(false);
                eventBus.unsetError();
                self.load();
              }
            })
            .catch((error) => {
              eventBus.setLoadingFlag(false);
              eventBus.setError({
                title: 'Failed to delete an experiment',
                message: error.response ? error.response.statusText : error
              });
              self.docs = null;
              self.selectedExperiments = [];
              self.showCheckbox = false;
            });
        };

        doDeleteOne(docIdList.length - 1);
      }
    }
  }
};
</script>

<style lang="scss" scoped>
.top-tool-bar, .bottom-tool-bar {
  margin: 10px 0;
}
</style>
