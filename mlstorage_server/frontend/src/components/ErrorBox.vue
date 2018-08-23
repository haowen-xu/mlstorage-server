<template>
  <div>
    <b-container v-if="hasError" fluid style="padding-top: 15px">
      <b-row>
        <b-col>
          <b-alert variant="danger" show>
            <h4 v-if="errorTitle" class="alert-heading">{{ errorTitle }}</h4>
            <div>{{ errorMessage }}</div>
          </b-alert>
        </b-col>
      </b-row>
    </b-container>
  </div>
</template>

<script>
import eventBus from '../libs/eventBus';

export default {
  data () {
    return {
      hasError: false,
      errorTitle: null,
      errorMessage: null
    };
  },

  mounted () {
    eventBus.addErrorHandler(this.setError);
  },

  destroyed () {
    eventBus.removeErrorHandler(this.setError);
  },

  methods: {
    setError ({hasError, title, message}) {
      this.hasError = hasError;
      this.errorTitle = title;
      this.errorMessage = message;
    }
  }
};
</script>
