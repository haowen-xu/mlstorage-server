<template>
  <div class="editable-text" @click="onClick">
    <span v-if="!editing">
      <slot v-if="valueText"></slot>
      <span v-if="!valueText" class="placeholder">(click here to edit)</span>
    </span>
    <div v-else>
      <b-form-input v-model="valueText"
                    type="text"
                    :id="inputId"
                    :state="hasError"
                    @change="onValueChange"
                    @blur.native="onValueChange"
      ></b-form-input>
      <b-form-invalid-feedback :id="inputId">
        {{ errorMessage }}
      </b-form-invalid-feedback>
    </div>
  </div>
</template>

<script>
import Vue from 'vue';
import uuidv4 from 'uuid/v4';

export default {
  props: {
    value: {
      default: null
    },
    valueToText: {
      default: () => (s) => s
    },
    textToValue: {
      default: () => (v) => v
    }
  },

  data () {
    return {
      editing: false,
      errorMessage: null,
      valueText: this.valueToText(this.value),
      inputId: uuidv4()
    };
  },

  watch: {
    value (val) {
      this.valueText = this.valueToText(val);
    }
  },

  computed: {
    hasError () {
      return this.errorMessage ? false : null;
    }
  },

  methods: {
    onClick () {
      this.editing = true;
      this.errorMessage = null;
      Vue.nextTick(() => {
        this.$el.getElementsByTagName('input')[0].focus();
      });
    },

    onValueChange () {
      try {
        this.$emit('change', this.textToValue(this.valueText));
        this.errorMessage = null;
        this.editing = false;
      } catch (e) {
        this.errorMessage = e.toString();
      }
    }
  }
};
</script>

<style lang="scss" scoped>
.editable-text {
  display: block;
  width: 100%;
  .placeholder {
    color: #aaa;
  }
}
</style>
