<template>
  <div>
    <b-navbar toggleable="md" type="dark" variant="dark" fixed="top">
      <b-navbar-toggle target="nav_collapse"></b-navbar-toggle>
      <b-navbar-brand href="#">MLStorage</b-navbar-brand>
      <b-collapse is-nav id="nav_collapse">
        <b-navbar-nav>
          <b-nav-item to="/" @click="navToMain" exact>All</b-nav-item>
        </b-navbar-nav>
        <b-navbar-nav>
          <b-nav-item to="/?q=tags:star" @click="navToStarred" exact>Stared</b-nav-item>
        </b-navbar-nav>
        <b-navbar-nav>
          <b-nav-item to="/?q=status:running" @click="navToRunning" exact>Running</b-nav-item>
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
import userConfig from '../libs/userConfig';

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
    const pageId = Number.parseInt(this.$route.params.pageId || 1);
    const queryString = this.$route.query.q || "";
    this.setLastVisit(pageId, queryString);
    return {
      loadVersion: 0,
      pageId: pageId,
      queryString: queryString
    };
  },

  methods: {
    refresh () {
      eventBus.callReloader();
    },

    setLastVisit (pageId, queryString) {
      userConfig.dashboard.lastPageId = pageId;
      userConfig.dashboard.lastQueryString = queryString;
    },

    navToPage (pageId, queryString) {
      pageId = pageId || 1;
      queryString = queryString || "";

      const dst = {};
      if (pageId) {
        dst['path'] = `/page/${pageId}`;
      }
      if (queryString) {
        dst["query"] = { q: queryString };
      }
      this.$router.push(dst);
      this.setLastVisit(pageId, queryString);
      this.pageId = pageId;
      this.queryString = queryString;
      this.loadVersion += 1;
    },

    navToMain () {
      this.navToPage(null, '');
    },

    navToStarred () {
      this.navToPage(null, 'tags:star');
    },

    navToRunning () {
      this.navToPage(null, 'status:running');
    }
  }
};
</script>

<style>
.main-wrapper {
  padding-top: 56px;
}
</style>
