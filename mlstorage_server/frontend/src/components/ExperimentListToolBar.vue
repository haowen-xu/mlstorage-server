<template>
  <div>
    <div class="clearfix"></div>

    <b-button-toolbar class="operation-bar">
      <b-button-group class="mx-1" size="sm">
        <b-button :pressed.sync="myShowCheckbox">Select</b-button>
        <b-button variant="primary" v-if="showCheckbox" @click="selectAllClicked">
          <span>{{ selectAllMode }}</span>All
        </b-button>
        <b-button variant="danger" v-if="showCheckbox" :disabled="!selectedCount"
                  v-b-modal.deleteConfirm>
          Delete<span v-if="showCheckbox"> ({{selectedCount}})</span>
        </b-button>
        <b-button v-if="showCheckbox" :disabled="!selectedCount" @click="starClicked">
          Star<span v-if="showCheckbox"> ({{selectedCount}})</span>
        </b-button>
        <b-button v-if="showCheckbox" :disabled="!selectedCount" @click="unStarClicked">
          UnStar<span v-if="showCheckbox"> ({{selectedCount}})</span>
        </b-button>
      </b-button-group>

      <b-button-group class="mx-1" size="sm">
        <b-button v-b-modal.dashBoardOption>Options</b-button>
      </b-button-group>
    </b-button-toolbar>

    <b-button-toolbar v-if="hasNavigation"
                      key-nav aria-label="Toolbar with button groups"
                      class="navigation-bar">
      <b-button-group class="mx-1" size="sm">
        <b-btn :disabled="!hasPrevPage" @click="prevPage">&lsaquo;</b-btn>
      </b-button-group>
      <b-button-group class="mx-1" size="sm">
        <b-btn>{{ pageId }}</b-btn>
      </b-button-group>
      <b-button-group class="mx-1" size="sm">
        <b-btn :disabled="!hasNextPage" @click="nextPage">&rsaquo;</b-btn>
      </b-button-group>
    </b-button-toolbar>
    <div class="clearfix"></div>
  </div>
</template>

<script>
export default {
  props: {
    pageId: {
      type: Number
    },
    hasNextPage: {
      type: Boolean
    },
    hasPrevPage: {
      type: Boolean
    },
    showCheckbox: {
      type: Boolean
    },
    selectedExperiments: {
      type: Array
    },
    selectAllMode: {
      type: String
    }
  },

  data () {
    return {
      myShowCheckbox: this.showCheckbox
    };
  },

  computed: {
    hasNavigation () {
      return this.hasPrevPage || this.hasNextPage;
    },

    selectedCount () {
      return (this.selectedExperiments && this.selectedExperiments.length) || 0;
    }
  },

  watch: {
    showCheckbox (value) {
      this.myShowCheckbox = value;
    },

    myShowCheckbox (value) {
      this.$emit('showCheckboxChanged', value);
    },

    resultFilterRegExp (value) {
      this.$emit('resultFilterChanged', value);
    }
  },

  methods: {
    prevPage () {
      if (this.hasPrevPage) {
        this.$emit('navToPage', this.pageId - 1);
      }
    },

    nextPage () {
      if (this.hasNextPage) {
        this.$emit('navToPage', this.pageId + 1);
      }
    },

    starClicked () {
      this.$emit('starDocs');
    },

    unStarClicked () {
      this.$emit('unStarDocs');
    },

    selectAllClicked () {
      this.$emit('selectAllClicked');
    }
  }
};
</script>

<style lang="scss" scoped>
.clearfix {
  clear: both;
}
.operation-bar {
  float: left;
}
.navigation-bar {
  float: right;
}
</style>
