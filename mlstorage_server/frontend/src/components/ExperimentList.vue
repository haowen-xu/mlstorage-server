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
        <b-form-input v-model="inputQueryString"
                      type="text"
                      class="query-input"
                      placeholder="Enter your query"
                      @keyup.native.enter="queryStringKeyEnter"></b-form-input>
      </b-col>
    </b-row>

    <b-row>
      <b-col>
        <div v-if="docs">
          <experiment-list-tool-bar :page-id="pageId"
                                    :has-next-page="hasNextPage"
                                    :has-prev-page="hasPrevPage"
                                    :show-checkbox="showCheckbox"
                                    :selected-experiments="selectedExperiments"
                                    :sort-by="sortBy"
                                    @navToPage="navToPage"
                                    @showCheckboxChanged="showCheckboxChanged"
                                    @sortByChanged="sortByChanged"
                                    @deleteDocs="deleteDocs"
                                    @starDocs="starDocs"
                                    @unStarDocs="unStarDocs"
                                    class="top-tool-bar">
          </experiment-list-tool-bar>

          <b-list-group class="experiment-list">
            <experiment-list-entry v-for="doc in docs" :key="doc.id" :doc="doc"
                                   @selectChanged="experimentSelectChanged"
                                   :show-checkbox="showCheckbox"
                                   :selected-experiments="selectedExperiments">
            </experiment-list-entry>
          </b-list-group>
          <experiment-list-tool-bar v-if="this.docs && this.docs.length > 0"
                                    :page-id="pageId"
                                    :has-next-page="hasNextPage"
                                    :has-prev-page="hasPrevPage"
                                    :show-checkbox="showCheckbox"
                                    :selected-experiments="selectedExperiments"
                                    :sort-by="sortBy"
                                    @navToPage="navToPage"
                                    @showCheckboxChanged="showCheckboxChanged"
                                    @sortByChanged="sortByChanged"
                                    @deleteDocs="deleteDocs"
                                    @starDocs="starDocs"
                                    @unStarDocs="unStarDocs"
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
    pageId: {
      type: Number,
      default: 1
    },
    queryString: {
      type: String,
      default: ""
    },
    loadVersion: {
      type: Number,
      default: 0,
    }
  },

  data () {
    return {
      docs: null,
      pageSize: userConfig.dashboard.pageSize,
      hasNextPage: true,
      selectedExperiments: [],
      showCheckbox: false,
      sortBy: userConfig.dashboard.sortBy,
      inputQueryString: this.queryString
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
      return this.pageId > 1;
    },

    selectedCount () {
      return this.selectedExperiments.size;
    }
  },

  watch: {
    loadVersion () {
      this.load();
    },

    queryString (value) {
      this.inputQueryString = value;
    }
  },

  methods: {
    load () {
      if (this.stopLoading)
        return;

      const pageId = this.pageId;

      eventBus.setLoadingFlag(true);
      const uri = `/v1/_query?timestamp=1&strict=1&sort=${this.sortBy}&` +
        `skip=${(pageId - 1) * this.pageSize}&limit=${this.pageSize + 1}&core=1`;
      const body = this.queryString || {};
      const headers = {};
      if (this.queryString) {
        headers['Content-Type'] = 'text/plain';
      }

      axios.post(uri, body, {headers: headers})
        .then((resp) => {
          this.selectedExperiments = [];
          this.showCheckbox = false;
          if (pageId === this.pageId) {
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
      this.$emit('navToPage', pageId, this.queryString);
    },

    sortByChanged (sortBy) {
      this.sortBy = sortBy;
      userConfig.dashboard.sortBy = sortBy;
      this.load();
    },

    queryStringKeyEnter () {
      this.$emit('navToPage', 1, this.inputQueryString);
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
    },

    starDocs () {
      this.setDocsStar(true);
    },

    unStarDocs () {
      this.setDocsStar(false);
    },

    setDocsStar (star) {
      eventBus.setLoadingFlag(true);
      if (this.selectedExperiments && this.selectedExperiments.length > 0) {
        const docList = this.selectedExperiments.map(doc => doc);
        const self = this;

        const doStarOne = function (i) {
          let tags = docList[i].tags || [];
          if (star) {
            if (tags.indexOf('star') < 0) {
              tags.push('star');
            }
          } else {
            tags = tags.filter(s => s !== 'star');
          }

          axios.post(`/v1/_update/${docList[i].id}`, {'tags': tags})
            .then(() => {
              if (i > 0) {
                doStarOne(i - 1);
              } else {
                eventBus.setLoadingFlag(false);
                eventBus.unsetError();
                self.load();
              }
            })
            .catch((error) => {
              eventBus.setLoadingFlag(false);
              eventBus.setError({
                title: `Failed to ${star ? 'star' : 'un-star'} an experiment`,
                message: error.response ? error.response.statusText : error
              });
              self.docs = null;
              self.selectedExperiments = [];
              self.showCheckbox = false;
            });
        };

        doStarOne(docList.length - 1);
      }
    }
  }
};
</script>

<style lang="scss" scoped>
.top-tool-bar, .bottom-tool-bar, .experiment-list {
  margin: 10px 0;
}
.query-input {
  margin-top: 10px;
}
</style>
