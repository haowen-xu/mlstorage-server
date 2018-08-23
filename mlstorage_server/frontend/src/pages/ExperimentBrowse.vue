<template>
  <b-container fluid style="padding-top: 15px">
    <b-row>
      <b-col>
        <table v-if="items || hasParentPath" class="table table-hover table-sm">
          <tr>
            <th scope="col" class="shrink"></th>
            <th scope="col" class="expand">Name</th>
            <th scope="col" class="shrink">Size</th>
            <th scope="col" class="shrink">Modify Time</th>
          </tr>
          <tr v-if="hasParentPath">
            <td class="shrink"><octicon name="file-directory"></octicon></td>
            <td class="expand">
              <b-link :to="`/${id}/browse` + resolvePath('..', true)">..</b-link>
            </td>
            <td class="shrink"></td>
            <td class="shrink"></td>
          </tr>
          <tr v-else>
            <td class="shrink"><octicon name="file-directory"></octicon></td>
            <td class="expand">
              <b-link :to="`/${id}/browse/`">.</b-link>
            </td>
            <td class="shrink"></td>
            <td class="shrink"></td>
          </tr>
          <tr v-for="item in sortedDirs" :key="item.name">
            <td class="shrink"><octicon name="file-directory"></octicon></td>
            <td class="expand">
              <b-link :to="`/${id}/browse` + resolvePath(item.name, true)">{{ item.name }}</b-link>
            </td>
            <td class="shrink"></td>
            <td class="shrink">{{ formatDateTime(item.mtime) }}</td>
          </tr>
          <tr v-for="item in sortedFiles" :key="item.name">
            <td class="shrink"><octicon name="file"></octicon></td>
            <td class="expand">
              <a :href="`/v1/_getfile/${id}` + resolvePath(item.name)">{{ item.name }}</a>
            </td>
            <td class="shrink">{{ fileSize(item.size) }}</td>
            <td class="shrink">{{ formatDateTime(item.mtime) }}</td>
          </tr>
        </table>
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

export default {
  data () {
    return {
      items: null
    };
  },

  mounted () {
    this.load();
    eventBus.addReloader(this.load);
  },

  destroyed () {
    eventBus.removeReloader(this.load);
  },

  computed: {
    id () {
      return this.$route.params.id;
    },

    path () {
      return this.normalizePath(this.$route.params.path || '');
    },

    hasParentPath () {
      return this.path !== '/';
    },

    sortedDirs () {
      return this.filterItems((item) => item.isdir);
    },

    sortedFiles () {
      return this.filterItems((item) => !item.isdir);
    }
  },

  watch: {
    path () {
      this.load();
    }
  },

  methods: {
    load () {
      eventBus.setLoadingFlag(true);
      axios.get(`/v1/_listdir/${this.id}${this.path}`)
        .then((resp) => {
          this.items = resp.data;
          eventBus.setLoadingFlag(false);
          eventBus.unsetError();
        })
        .catch((error) => {
          this.items = null;
          eventBus.setLoadingFlag(false);
          eventBus.setError({
            title: 'Failed to list directory',
            message: error.response ? error.response.statusText : error
          });
        });
    },

    filterItems (predicate) {
      if (this.items) {
        const sortArray = (
          this.items
            .map((item, index) => [item.name, index])
            .filter((_, index) => predicate(this.items[index]))
        );
        sortArray.sort(natsort({ insensitive: true }));
        return sortArray.map((item) => this.items[item[1]]);
      }
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

<style lang="scss" scoped>
table {
  tr:first-child {
    th { border-top: none; }
  }
  th.shrink, td.shrink {
    white-space: nowrap;
  }
  th.expand, td.expand {
    width: 99%;
  }
}
</style>
