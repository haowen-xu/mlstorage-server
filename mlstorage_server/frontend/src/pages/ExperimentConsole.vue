<template>
  <div class="log-wrapper bg-dark">
    <div v-if="logs" class="log-content">
      <pre class="text-light">{{ logs }}</pre>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import eventBus from '../libs/eventBus';

class AutoReloader {
  constructor (loaderFunc) {
    this.loaderFunc = loaderFunc;
    this.contentRangeSupported = true;
    this.rangeStart = 0;
    this._autoReloader = null;
    this._hasUnset = false;
  }

  setReloader (contentRangeSupported) {
    if (!this._hasUnset) {
      if (this.contentRangeSupported !== contentRangeSupported || !this._autoReloader) {
        if (this._autoReloader) {
          clearInterval(this._autoReloader);
          this._autoReloader = null;
        }
        this._autoReloader = setInterval(
          this.loaderFunc, this.contentRangeSupported ? 10 * 1000 : 120 * 1000);
      }
      this.contentRangeSupported = contentRangeSupported;
    }
  }

  unsetReloader () {
    if (!this._hasUnset) {
      if (this._autoReloader) {
        clearInterval(this._autoReloader);
        this._autoReloader = null;
      }
      this._hasUnset = true;
    }
  }
}

export default {
  props: ['doc'],

  data () {
    return {
      loading: false,
      finished: false,
      logs: null,
      rangeStart: 0
    };
  },

  mounted () {
    this.finished = this.doc.status === 'FAILED' || this.doc.status === 'COMPLETED';
    this.autoReloader = new AutoReloader(() => this.load());
    if (this.finished) {
      this.autoReloader.unsetReloader();
    } else {
      this.autoReloader.setReloader(true);
    }
    this.load();
    eventBus.addReloader(this.load);
  },

  destroyed () {
    eventBus.removeReloader(this.load);
    this.autoReloader.unsetReloader();
  },

  computed: {
    id () {
      return this.$route.params.id;
    }
  },

  methods: {
    load () {
      if (this.loading) {
        // because we track rangeStart, we can only run one request at one time.
        return;
      }
      this.loading = true;
      eventBus.setLoadingFlag(true);
      axios.get(`/v1/_getfile/${this.id}/console.log`,
        {
          headers: this.autoReloader.contentRangeSupported ? {
            'Range': `bytes=${this.rangeStart}-`
          } : {
            'Range': `bytes=0-`
          }
        }
      )
        .then((resp) => {
          const contentRange = resp.headers['content-range'];
          if (contentRange) {
            this.logs = (this.logs || '') + resp.data;
            try {
              this.rangeStart = Number.parseInt(contentRange.split('-')[1].split('/')[0]) + 1;
              this.autoReloader.setReloader(true);
            } catch (e) {
              // eslint-disable-next-line
              console.log('Could not parse Content-Range.');
              this.autoReloader.setReloader(false);
            }
          } else {
            this.logs = resp.data;
          }
          eventBus.setLoadingFlag(false);
          eventBus.unsetError();
          this.loading = false;
        })
        .catch((error) => {
          eventBus.setLoadingFlag(false);
          if (error.response && error.response.status === 404) {
            // help to recover from error afterwards
            this.autoReloader.setReloader(false);
            eventBus.unsetError();
            this.logs = '';
          } else if (error.response && error.response.status === 416) {
            // do nothing
            eventBus.unsetError();
          } else {
            // help to recover from error afterwards
            this.autoReloader.setReloader(false);
            this.logs = '';
            eventBus.setError({
              title: 'Failed to load console.log',
              message: error.response ? error.response.statusText : error
            });
          }

          this.loading = false;
        });
    }
  },

  updated () {
    const container = this.$el.getElementsByClassName('log-content');
    if (container && container[0]) {
      this.$el.scrollTop = container[0].scrollHeight;
    }
  },

  watch: {
    doc (doc) {
      this.finished = doc.status === 'FAILED' || doc.status === 'COMPLETED';
      if (this.finished) {
        this.autoReloader.unsetReloader();
      }
    }
  }
};
</script>

<style lang="scss" scoped>
.log-wrapper {
  height: 100%;
  overflow: auto;
}
.log-content {
  padding: 15px;
}
</style>
