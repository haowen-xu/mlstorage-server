<template>
  <div>
    <b-modal id="deleteConfirm"
             title="Confirm to Delete"
             ok-variant="danger"
             ok-title="Delete It"
             @ok="deleteDoc">
      Really want to delete the experiment
        <span v-if="doc.name">"{{ doc.name }}" ({{ doc.id }})</span>
        <span v-else>"{{ doc.id }}"</span>
      ?
    </b-modal>

    <b-container fluid style="padding-top: 15px">
      <b-row>
        <b-col>
          <b-button-toolbar class="toolbar justify-content-end"
                            key-nav aria-label="Toolbar with button groups">
            <b-button-group v-if="doc && sortedWebUIKeys"
                            class="mx-1" size="sm">
              <b-button v-for="key in sortedWebUIKeys"
                        :key="`webui:${key}`"
                        :href="doc.webui[key]">
                {{ key }}
              </b-button>
            </b-button-group>
            <b-button-group class="mx-1" size="sm">
              <b-button variant="secondary" :href="`/v1/_tarball/${id}`">Download</b-button>
              <b-button v-b-modal.deleteConfirm variant="danger">Delete</b-button>
            </b-button-group>
            <div style="clear:both"></div>
          </b-button-toolbar>

          <table class="table table-hover info-table">
            <tbody>
            <tr>
              <th scope="row" class="fieldName">ID</th>
              <td class="id fieldValue">
                <span>{{ doc.id }}</span>
              </td>
            </tr>
            <tr>
              <th scope="row" class="fieldName">Name</th>
              <td class="fieldValue">
                <editable-text :value="doc.name"
                               @change="onNameChanged">
                  {{ doc.name }}
                </editable-text>
              </td>
            </tr>
            <tr>
              <th scope="row" class="fieldName">Description</th>
              <td class="fieldValue">
                <editable-text :value="doc.description"
                               @change="onDescriptionChanged">
                  {{ doc.description }}
                </editable-text>
              </td>
            </tr>
            <tr>
              <th scope="row" class="fieldName">Tags</th>
              <td class="tags fieldValue">
                <editable-text :value="doc.tags"
                               :valueToText="tagsToText"
                               :textToValue="textToTags"
                               @change="onTagsChanged">
                  <span v-for="tag in doc.tags" :key="tag">{{ tag }}</span>
                </editable-text>
              </td>
            </tr>
            <tr>
              <th scope="row" class="fieldName">Status</th>
              <td class="fieldValue">
                <editable-text :value="doc.status"
                               :text-to-value="validateStatus"
                               @change="onStatusChanged">
                  <span :class="'text-' + statusClass">{{ statusText }}</span>
                </editable-text>
              </td>
            </tr>
            <tr v-if="doc.error && doc.error.message">
              <th scope="row" class="fieldName">Error</th>
              <td class="fieldValue">
                <div>
                  <pre>{{ doc.error.message }}</pre>
                  <b-button v-if="doc.error.traceback" class="show-traceback-btn"
                            :pressed.sync="showTraceback" variant="secondary" size="sm">
                    Show Traceback
                  </b-button>
                  <pre v-if="doc.error.traceback && showTraceback"
                       class="traceback">{{ doc.error.traceback }}</pre>
                </div>
              </td>
            </tr>
            <tr v-if="doc.result">
              <th scope="row" class="fieldName">Result</th>
              <td class="fieldValue">
                <dict-table :items="doc.result" />
              </td>
            </tr>
            <tr v-if="doc.config || doc.default_config">
              <th scope="row" class="fieldName">Config</th>
              <td v-if="doc.default_config" class="fieldValue">
                <b-button :pressed.sync="showDefaultConfig" variant="secondary" size="sm">
                  Show Default Config
                </b-button>
                <dict-table v-if="showDefaultConfig && mergedConfig"
                            :items="mergedConfig"
                            :boldKeys="configKeys"
                            style="margin-top: 5px"/>
                <dict-table v-else-if="doc.config"
                            :items="doc.config"
                            style="margin-top: 5px"/>
              </td>
              <td v-else class="fieldValue">
                <dict-table :items="mergedConfig" />
              </td>
            </tr>
            <tr v-if="doc.args">
              <th scope="row" class="fieldName">Args</th>
              <td class="fieldValue">
                <ul class="arg-list">
                  <li v-for="(arg, index) in doc.args" :key="index">
                    <pre>{{ arg }}</pre>
                  </li>
                </ul>
              </td>
            </tr>
            <tr v-if="doc.exit_code !== undefined && doc.exit_code !== null">
              <th scope="row" class="fieldName">Exit Code</th>
              <td class="fieldValue">{{ doc.exit_code }}</td>
            </tr>
            <tr v-if="doc.storage_dir">
              <th scope="row" class="fieldName">Storage Dir</th>
              <td class="fieldValue">{{ doc.storage_dir }}</td>
            </tr>
            <tr v-if="doc.exc_info && doc.exc_info.work_dir">
              <th scope="row" class="fieldName">Work Dir</th>
              <td class="fieldValue">{{ doc.exc_info.work_dir }}</td>
            </tr>
            <tr>
              <th scope="row" class="fieldName">File Size</th>
              <td class="fieldValue">
                <span v-if="storageSize" style="margin-right: 12px">{{ storageSize }}</span>
                <b-button v-if="!storageSize || (doc.status !== 'COMPLETED' && doc.status !== 'FAILED')"
                          variant="secondary" size="sm" @click="updateStorageSize">Update</b-button>
              </td>
            </tr>
            <tr v-if="doc.start_time">
              <th scope="row" class="fieldName">Start Time</th>
              <td class="fieldValue">{{ startTime }}</td>
            </tr>
            <tr>
              <th scope="row" class="fieldName">Last Update</th>
              <td class="fieldValue">{{ dateText }}</td>
            </tr>
            <tr v-if="doc.exc_info && doc.exc_info.hostname">
              <th scope="row" class="fieldName">Hostname</th>
              <td class="fieldValue">{{ doc.exc_info.hostname }}</td>
            </tr>
            <tr v-if="doc.exc_info && doc.exc_info.pid">
              <th scope="row" class="fieldName">PID</th>
              <td class="fieldValue">{{ doc.exc_info.pid }}</td>
            </tr>
            <tr v-if="doc.exc_info && doc.exc_info.env">
              <th scope="row" class="fieldName">Environ</th>
              <td class="fieldValue">
                <b-button :pressed.sync="showEnviron" variant="secondary" size="sm">
                  Show Environmental Variables
                </b-button>
                <dict-table v-if="showEnviron" :items="doc.exc_info.env" />
              </td>
            </tr>
            </tbody>
          </table>
        </b-col>
      </b-row>
    </b-container>
  </div>
</template>

<script>
import filesize from 'filesize';
import moment from 'moment';
import natsort from 'natsort';
import arrayEquals from 'array-equal';
import arrayUnique from 'array-unique';
import EditableText from '../components/EditableText';
import DictTable from '../components/DictTable';
import TimeDiff from '../libs/timeDiff';
import eventBus from '../libs/eventBus';
import { statusToBootstrapClass, getExtendedStatus } from '../libs/utils';

export default {
  components: {
    EditableText,
    DictTable
  },

  props: ['doc'],

  data () {
    return {
      dateText: null,
      dateDiff: 0,
      statusClass: null,
      statusText: null,
      showTraceback: false,
      showDefaultConfig: false,
      showEnviron: false
    };
  },

  mounted () {
    eventBus.unsetError();
    this.timeDiff = new TimeDiff();
    this.timeDiff.addWatcher(
      (dateText, dateDiff) => this.timeDiffWatcher(dateText, dateDiff));
    this.timeDiff.setTimestamp(this.doc.heartbeat);
  },

  destroyed () {
    if (this.timeDiff) {
      this.timeDiff.destroy();
      this.timeDiff = null;
    }
  },

  computed: {
    id () {
      return this.$route.params.id;
    },

    sortedWebUIKeys () {
      if (this.doc.webui) {
        let keys = Object.keys(this.doc.webui);
        keys.sort(natsort({ insensitive: true }));
        return keys;
      }
      return null;
    },

    startTime () {
      return moment.utc(this.doc.start_time * 1000).local().format('LLL');
    },

    mergedConfig () {
      let obj = Object.assign({}, this.doc.default_config || {});
      obj = Object.assign(obj, this.doc.config || {});
      return obj;
    },

    configKeys () {
      return Object.keys(this.doc.config || {});
    },

    storageSize () {
      if (this.doc.storage_size) {
        return filesize(this.doc.storage_size);
      }
      return null;
    }
  },

  methods: {
    timeDiffWatcher (dateText, dateDiff) {
      this.dateText = dateText;
      this.dateDiff = dateDiff;
      this.statusClass = statusToBootstrapClass(this.doc, this.dateDiff, 'success');
      this.statusText = getExtendedStatus(this.doc, this.dateDiff);
    },

    updateDoc (update) {
      if (update) {
        this.$emit('update', update);
      }
    },

    deleteDoc () {
      this.$emit('delete');
    },

    updateStorageSize () {
      this.$emit('updateStorageSize');
    },

    onNameChanged (name) {
      if (name !== this.doc.name) {
        this.updateDoc({'name': name});
      }
    },

    onDescriptionChanged (description) {
      if (description !== this.doc.description) {
        this.updateDoc({'description': description});
      }
    },

    onStatusChanged (status) {
      status = this.validateStatus(status);
      if (status !== this.doc.status) {
        this.updateDoc({'status': status});
      }
    },

    validateStatus (status) {
      const theStatus = (status || "").toUpperCase();
      if (theStatus !== "RUNNING" && theStatus !== "FAILED" && theStatus !== "COMPLETED") {
        throw "Invalid status: not one of 'RUNNING', 'FAILED', 'COMPLETED'.";
      }
      return theStatus;
    },

    tagsToText (tags) {
      return (tags || []).map(s => s.trim()).filter(s => !!s).join(', ');
    },

    textToTags (text) {
      return arrayUnique(text.split(',').map(s => s.trim()).filter(s => !!s));
    },

    onTagsChanged (tags) {
      tags = tags || [];
      const docTags = this.doc.tags || [];
      if (!arrayEquals(tags, docTags)) {
        this.updateDoc({'tags': tags});
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
.toolbar {
  margin-bottom: 10px;
}

.info-table {
  .id span {
    margin-right: 5px;
  }
  tr:first-child {
    th, td {
      border-top: none;
    }
  }
  .fieldName {
    width: 20%;
    min-width: 120px;
    max-width: 160px;
  }
  .fieldValue {
    font-family: SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
  }
  .arg-list {
    pre {
      margin-bottom: 0;
    }
    padding-left: 20px;
    margin-bottom: 0;
  }
  .show-traceback-btn {
    margin-left: 5px;
  }
  .traceback {
    margin-top: 10px;
    margin-bottom: 0;
  }
  .tags {
    span {
      margin-right: 5px;
    }
    span:after {
      content: ',';
    }
    span:last-child {
      margin-right: 0;
    }
    span:last-child:after {
      content: '';
    }
  }

}
</style>
