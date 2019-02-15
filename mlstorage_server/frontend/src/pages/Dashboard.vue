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
        <b-navbar-nav class="ml-auto">
          <b-nav-item @click="refresh">Reload</b-nav-item>
        </b-navbar-nav>
      </b-collapse>
    </b-navbar>

    <delayed-progress-bar class="fixed-top" z-index="9999"></delayed-progress-bar>

    <div class="main-wrapper">
      <error-box></error-box>
      <experiment-list :page-id="pageId"
                       :query-string="queryString"
                       :load-version="loadVersion"
                       @navToPage="navToPage" />
    </div>
  </div>
</template>

<script>
import DelayedProgressBar from '../components/DelayedProgressBar';
import ErrorBox from '../components/ErrorBox';
import ExperimentList from '../components/ExperimentList.vue';
import eventBus from '../libs/eventBus';

export default {
  components: {
    DelayedProgressBar,
    ErrorBox,
    ExperimentList
  },

  mounted () {
    document.title = 'Dashboard - MLStorage';
  },

  data() {
    return {
      loadVersion: 0
    };
  },

  computed: {
    pageId () {
      return Number.parseInt(this.$route.params.pageId || 1);
    },
    queryString () {
      return this.$route.query.q || "";
    }
  },

  methods: {
    refresh () {
      eventBus.callReloader();
    },

    navToPage (pageId, queryString) {
      const dst = { path: `/page/${pageId}` };
      if (queryString) {
        dst["query"] = { q: queryString };
      }
      this.$router.push(dst);
      this.loadVersion += 1;
    }
  }
};
</script>

<style>
.main-wrapper {
  padding-top: 56px;
}
</style>
