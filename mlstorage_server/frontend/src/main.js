// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue';
import BootstrapVue from 'bootstrap-vue';
//import Octicon from 'vue-octicon/components/Octicon.vue';
import 'bootstrap/dist/css/bootstrap.css';
import 'bootstrap-vue/dist/bootstrap-vue.css';
//import 'vue-octicon/icons';
import 'vue-awesome/icons';

import App from './App';
import router from './router/index';
import Icon from 'vue-awesome/components/Icon';

Vue.use(BootstrapVue);
//Vue.component('octicon', Octicon);
Vue.component('v-icon', Icon);

Vue.config.productionTip = false;

/* eslint-disable no-new */
new Vue({
  el: '#app',
  router,
  components: { App },
  template: '<App/>'
});
