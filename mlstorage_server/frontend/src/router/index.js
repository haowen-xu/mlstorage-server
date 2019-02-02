import Vue from 'vue';
import Router from 'vue-router';
import Dashboard from '../pages/Dashboard';
import Experiment from '../pages/Experiment';
import ExperimentInfo from '../pages/ExperimentInfo';
import ExperimentConsole from '../pages/ExperimentConsole';
import ExperimentBrowse from '../pages/ExperimentBrowse';

Vue.use(Router);

const router = new Router({
  mode: 'history',
  routes: [
    {
      path: '/',
      component: Dashboard
    },
    {
      path: '/page/:pageId(\\d+)',
      component: Dashboard
    },
    {
      path: '/:id([A-Za-z0-9]{24})',
      component: Experiment,
      children: [
        {
          path: '',
          component: ExperimentInfo
        },
        {
          path: 'console',
          component: ExperimentConsole
        },
        {
          path: 'browse:path(/.*)?',
          component: ExperimentBrowse
        }
      ]
    }
  ]
});

export default router;
