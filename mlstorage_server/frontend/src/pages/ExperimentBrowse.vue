<template>
  <b-container fluid style="padding-top: 15px">
    <b-row>
      <b-col>
        <b-input-group class="toolbar">
          <b-form-input v-model="itemFilter" type="text" size="sm"
                        placeholder="Enter your filter"></b-form-input>
          <b-button-group class="mx-1" size="sm">
            <b-button :disabled="!hasParentPath" :to="`/${id}/browse` + resolvePath('..', true)">Cd Up</b-button>
          </b-button-group>
        </b-input-group>

        <b-table v-if="filteredItems" striped hover small class="file-table"
                 :items="filteredItems" :fields="fields" primary-key="name" :sort-compare="sortCompare">
          <template slot="isdir" slot-scope="data">
            <v-icon v-if="data.value" name="folder"></v-icon>
            <v-icon v-else name="file"></v-icon>
          </template>

          <template slot="name" slot-scope="data">
            <b-link v-if="data.item.isdir" :to="`/${id}/browse` + resolvePath(data.value, true)">{{ data.value }}</b-link>
            <a v-else :href="`/v1/_getfile/${id}` + resolvePath(data.value)">{{ data.value }}</a>
          </template>

          <template slot="size" slot-scope="data">
            <span v-if="!data.item.isdir">{{ fileSize(data.value) }}</span>
          </template>

          <template slot="mtime" slot-scope="data">
            {{ formatDateTime(data.value) }}
          </template>
        </b-table>
      </b-col>
    </b-row>
  </b-container>
</template>

<script>
import axios from 'axios';
import filesize from 'filesize';
import natsort from 'natsort';
import eventBus from '../libs/eventBus';
import { formatDateTime } from '../libs/utils';

const sorter = natsort({ insensitive: true });

export default {
  data () {
    return {
      itemFilter: '',
      items: null,
      fields: [
        {
          key: 'isdir',
          label: '',
          sortable: false,
          class: 'shrink',
        },
        {
          key: 'name',
          label: 'Name',
          sortable: true,
          class: 'expand',
        },
        {
          key: 'size',
          label: 'Size',
          sortable: true,
          class: 'shrink',
        },
        {
          key: 'mtime',
          label: 'Modify Time',
          sortable: true,
          class: 'shrink',
        }
      ],
      path: this.routePath
    };
  },

  mounted () {
    this.load(this.routePath);
    eventBus.addReloader(this.load);
  },

  destroyed () {
    eventBus.removeReloader(this.load);
  },

  computed: {
    id () {
      return this.$route.params.id;
    },

    filteredItems () {
      if (!this.items)
        return [];
      let sortArray = this.items;
      if (this.itemFilter) {
        sortArray = sortArray.filter(
          s => s.name.toLowerCase().indexOf(this.itemFilter.toLowerCase()) >= 0);
      } else {
        sortArray = sortArray.map(s => s);
      }
      sortArray.sort((a, b) => -this.sortCompare(a, b));
      return sortArray;
    },

    hasParentPath () {
      return this.path !== '/';
    },

    routePath () {
      return this.normalizePath(this.$route.params.path || '');
    }
  },

  watch: {
    routePath (value) {
      this.load(value);
    }
  },

  methods: {
    load (path) {
      path = path || this.path;
      eventBus.setLoadingFlag(true);
      axios.get(`/v1/_listdir/${this.id}${path}`)
        .then((resp) => {
          this.itemFilter = '';
          this.items = resp.data;
          this.path = path;
          eventBus.setLoadingFlag(false);
          eventBus.unsetError();
        })
        .catch((error) => {
          this.itemFilter = '';
          this.items = null;
          this.path = path;
          eventBus.setLoadingFlag(false);
          eventBus.setError({
            title: 'Failed to list directory',
            message: error.response ? error.response.statusText : error
          });
        });
    },

    sortCompare (a, b, key) {
      // field-specific order functions
      const getTypeOrder = () => (
        a.isdir ? (
          b.isdir ? 0 : -1
        ) : (
          b.isdir ? 1 : 0
        )
      );
      const getNameOrder = () => sorter(a.name, b.name);
      const getSizeOrder = () => (a.size - b.size);
      const getMtimeOrder = () => (a.mtime - b.mtime);
      const getOrder = function (orderFunc) {
        for (let i=0; i<orderFunc.length; ++i) {
          const order = orderFunc[i]();
          if (order !== 0)
            return -order;
        }
        return 0;
      };

      // compute the orders according to 'key'.
      if (key === 'size') {
        return getOrder([getTypeOrder, getSizeOrder, getNameOrder]);
      } else if (key === 'mtime') {
        return getOrder([getTypeOrder, getMtimeOrder, getNameOrder]);
      }
      return getOrder([getTypeOrder, getNameOrder]);
    },

    formatDateTime (timestamp) {
      return formatDateTime(timestamp, 'YYYY-MM-DD H:mm:ss');
    },

    fileSize (size) {
      return filesize(size);
    },

    normalizePath (path) {
      const segments = path.split('/');
      const ret = [];
      for (let i = 0; i < segments.length; ++i) {
        if (segments[i] === '..') {
          if (segments.length > 0) {
            ret.pop();
          }
        } else if (segments[i] !== '.' && segments[i] !== '') {
          ret.push(segments[i]);
        }
      }
      return '/' + ret.join('/');
    },

    resolvePath (name, tailSlash) {
      let ret = this.normalizePath(`${this.path}/${name}`);
      if (tailSlash && !ret.endsWith('/')) {
        ret += '/';
      }
      return ret;
    }
  }
};
</script>

<style lang="scss">
.toolbar {
  margin-bottom: 10px;
}
.file-table {
  table {
    table-layout: fixed;
  }
  .shrink {
    white-space: nowrap;
  }
  .expand {
    width: 99%;
  }
}
</style>
