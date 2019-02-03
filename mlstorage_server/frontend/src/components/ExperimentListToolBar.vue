<template>
  <div>
    <div class="clearfix"></div>

    <b-button-toolbar class="operation-bar">
      <b-button-group class="mx-1" size="sm">
        <b-button :pressed.sync="myShowCheckbox">Select</b-button>
        <b-button variant="danger" v-if="showCheckbox" :disabled="!selectedCount"
                  v-b-modal.deleteConfirm>
          Delete<span v-if="showCheckbox"> ({{selectedCount}})</span>
        </b-button>
      </b-button-group>

      <b-dropdown class="mx-1" size="sm" left text="Options">
        <b-dropdown-header size="sm">Sort By</b-dropdown-header>
        <b-form-select size="sm" v-model="theSortBy" :options="sortByOptions" class="select-input"></b-form-select>
      </b-dropdown>
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
    sortBy: {
      type: String
    }
  },

  data () {
    return {
      myShowCheckbox: this.showCheckbox,
      theSortBy: this.sortBy,
      sortByOptions: [
        { value: '-heartbeat', text: 'Last Update' },
        { value: '-start_time', text: 'Start Time' }
      ]
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

    sortBy (value) {
      this.theSortBy = value;
    },

    theSortBy (value) {
      this.$emit('sortByChanged', value);
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
    }
  }
}
</script>

<style lang="scss" scoped>
.clearfix {
  clear: both;
}
.operation-bar {
  float: left;
  .select-input {
  }
}
.navigation-bar {
  float: right;
}
</style>
