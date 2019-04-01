<template>
  <div class="main-container">
    <iframe :src="`/v1/_getfile/${id}/report.html`"></iframe>
  </div>
</template>

<script>
export default {
  computed: {
    id () {
      return this.$route.params.id;
    }
  }
};
</script>

<style lang="scss" scoped>
  .main-container {
    height: 100%;
    overflow: auto;
    iframe {
      border: none;
      width: 100%;
      height: 100%;
      overflow: auto;
    }
  }
</style>
