<template>
  <div>
    <b-container fluid style="padding-top: 15px">
      <b-row>
        <b-col>
          <div v-for="item in items" :key="item.name" class="figure">
            <h3>{{ item.name }}</h3>
            <b-img :src="`/v1/_getfile/${id}/figures/${ encodeURIComponent(item.name) }`"
                   fluid :alt="item.name">
            </b-img>
          </div>
        </b-col>
      </b-row>
    </b-container>
  </div>
</template>

<script>
import axios from 'axios';
import natsort from 'natsort';
import eventBus from '../libs/eventBus';
const sorter = natsort({ insensitive: true, desc: false });

export default {
  props: ['doc'],

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
    }
  },

  methods: {
    isImageFile (name) {
      return !!name.match(/.*\.(png|jpg|jpeg|bmp)$/i);
    },

    load (path) {
      path = path || this.path;
      eventBus.setLoadingFlag(true);
      axios.get(`/v1/_listdir/${this.id}/figures`)
        .then((resp) => {
          this.items = resp.data.filter(i => this.isImageFile(i.name))
            .sort((a, b) => sorter(a.name, b.name));
          eventBus.setLoadingFlag(false);
          eventBus.unsetError();
        })
        .catch((error) => {
          this.items = null;
          eventBus.setLoadingFlag(false);
          eventBus.setError({
            title: 'Failed to list figures',
            message: error.response ? error.response.statusText : error
          });
        });
    }
  }
};
</script>

<style lang="scss" scoped>
  .word-wrap {
    word-wrap: break-word;
  }
  .figure {
    text-align: center;
    display: block;
    margin-bottom: 20px;
  }
</style>
