// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue';
import App from './App';
import router from './router';

Vue.config.productionTip = false;

Vue.filter('rudate', function (value) {
  if (!value) return ''
  var str = new Date(value)
  return ((str.getDate() < 10) ? '0' : '') + str.getDate() + '.' + ((str.getMonth() < 9) ? '0' : '') + (str.getMonth() + 1) + '.' + str.getFullYear()
})

/* eslint-disable no-new */
new Vue({
  el: '#app',
  router,
  components: { App },
  template: '<App/>'
});
