import Vue from 'vue';
import { BootstrapVue, IconsPlugin } from 'bootstrap-vue';
import ToastPlugin from 'vue-toast-notification';
import App from './App.vue';
import store from './store';

import './assets/styles/dark.scss';
import 'vue-toast-notification/dist/theme-sugar.css';



Vue.use(BootstrapVue);
Vue.use(IconsPlugin);
Vue.use(ToastPlugin, {
  position: 'top-right',
});

Vue.config.productionTip = false;

new Vue({
  render: (h) => h(App),
  store,
}).$mount('#app');
