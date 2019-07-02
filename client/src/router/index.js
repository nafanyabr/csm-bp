import '@fortawesome/fontawesome-free/css/all.min.css';
import '@/assets/css/style.css';
import Vue from 'vue';
import Router from 'vue-router';
import ZK from '@/components/ZK';

Vue.use(Router);

export default new Router({
  routes: [
    {
      path: '/:userid',
      name: 'ZK',
      component: ZK,
      props: true
    },
  ],
  mode: 'history'
});
