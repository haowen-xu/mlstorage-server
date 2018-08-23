<template>
  <div>
    <mu-icon v-if="status === 'running'" value="update" color="green500" />
    <mu-icon v-else-if="status === 'failed'" value="error_outline" color="red500" />
    <mu-icon v-else-if="status === 'lost'" value="help_outline" color="orange500" />
    <mu-icon v-else value="done" />
  </div>
</template>

<script>
export default {
  props: {
    status: {
      type: String,
      default: 'succeeded'
    }
  }
};
</script>
