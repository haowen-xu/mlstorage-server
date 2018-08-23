<template>
  <div>
    <b-navbar toggleable="md" type="dark" variant="dark" fixed="top">
      <b-navbar-toggle target="nav_collapse"></b-navbar-toggle>
      <b-navbar-brand href="#">MLStorage</b-navbar-brand>
      <b-collapse is-nav id="nav_collapse">
        <b-navbar-nav>
          <b-nav-item to="/" exact>Dashboard</b-nav-item>
        </b-navbar-nav>
        <b-dropdown-divider />
        <b-navbar-nav>
          <b-nav-item :to="`/${id}/`" exact>Experiment</b-nav-item>
          <b-nav-item :to="`/${id}/console`" exact>Console</b-nav-item>
          <b-nav-item :to="`/${id}/browse/`">Browse</b-nav-item>
        </b-navbar-nav>
        <b-dropdown-divider />
        <b-navbar-nav class="ml-auto">
          <b-nav-item @click="refresh">Reload</b-nav-item>
        </b-navbar-nav>
      </b-collapse>
    </b-navbar>

    <delayed-progress-bar class="fixed-top" z-index="9999"></delayed-progress-bar>

    <div class="main-wrapper">
      <error-box></error-box>
      <router-view v-if="doc" :doc="doc"
                   @update="updateDoc" @delete="deleteDoc"></router-view>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import DelayedProgressBar from '../components/DelayedProgressBar';
import ErrorBox from '../components/ErrorBox';
import eventBus from '../libs/eventBus';

export default {
  components: {
    DelayedProgressBar,
    ErrorBox
  },

  data () {
    return {
      doc: null
    };
  },

  computed: {
    id () {
      return this.$route.params.id;
    },

    name () {
      return this.doc && this.doc.name;
    }
  },

  mounted () {
    this.load();
    eventBus.addReloader(this.load);
    this.autoReloader = setInterval(() => this.load(), 120 * 1000);
  },

  destroyed () {
    if (this._autoReloader) {
      clearInterval(this._autoReloader);
      this.autoReloader = null;
    }
    eventBus.removeReloader(this.load);
  },

  methods: {
    refresh () {
      eventBus.callReloader();
    },

    setDoc (doc) {
      this.doc = doc;
      if (doc) {
        document.title = `${this.doc.name || this.doc.id} - MLStorage`;
      } else {
        document.title = 'Experiment - MLStorage';
      }
    },

    load () {
      eventBus.setLoadingFlag(true);
      axios.get(`/v1/_get/${this.id}?timestamp=1`)
        .then((resp) => {
          eventBus.setLoadingFlag(false);
          eventBus.unsetError();
          this.setDoc(resp.data);
        })
        .catch((error) => {
          eventBus.setLoadingFlag(false);
          eventBus.setError({
            title: 'Failed to load the experiment',
            message: error.response ? error.response.statusText : error
          });
          this.setDoc(null);
        });
    },

    updateDoc (update) {
      if (update) {
        eventBus.setLoadingFlag(true);
        axios.post(`/v1/_update/${this.id}?timestamp=1`, update)
          .then((resp) => {
            eventBus.setLoadingFlag(false);
            eventBus.unsetError();
            this.setDoc(resp.data);
          })
          .catch((error) => {
            eventBus.setLoadingFlag(false);
            eventBus.setError({
              title: 'Failed to load the experiment',
              message: error.response ? error.response.statusText : error
            });
            this.setDoc(null);
          });
      }
    },

    deleteDoc () {
      eventBus.setLoadingFlag(true);
      axios.post(`/v1/_delete/${this.id}`)
        .then((resp) => {
          eventBus.setLoadingFlag(false);
          eventBus.unsetError();
          this.$router.push('/');
        })
        .catch((error) => {
          eventBus.setLoadingFlag(false);
          eventBus.setError({
            title: 'Failed to delete the experiment',
            message: error.response ? error.response.statusText : error
          });
          this.setDoc(null);
        });
    }
  }
};
</script>

<style>
.main-wrapper {
  padding-top: 56px;
  height: 100%;
}
</style>
