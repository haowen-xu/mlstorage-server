<template>
  <b-progress v-if="isLoading"
              :value="100"
              variant="dark"
              :animated="true"
              :striped="true"
              style="width: 100%; height: 5px"></b-progress>
</template>

<script>
import eventBus from '../libs/eventBus';

export default {
  props: ['loading'],

  data () {
    return {
      isLoading: false
    };
  },

  created () {
    this.showInterval = null;
    eventBus.watchLoadingFlag(this.watchLoadingFlag);
  },

  destroyed () {
    eventBus.unwatchLoadingFlag(this.watchLoadingFlag);
    if (this.showInterval) {
      clearInterval(this.showInterval);
      this.showInterval = null;
    }
  },

  methods: {
    watchLoadingFlag (val) {
      if (val) {
        if (!this.showInterval) {
          this.showInterval = setInterval(() => {
            clearInterval(this.showInterval);
            this.isLoading = true;
            this.showInterval = null;
          }, 500);
        }
      } else {
        if (this.showInterval) {
          clearInterval(this.showInterval);
          this.showInterval = null;
        }
        this.isLoading = false;
      }
    }
  }
};
</script>
