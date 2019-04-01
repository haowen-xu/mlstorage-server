import Vue from 'vue';
import Router from 'vue-router';
import Dashboard from '../pages/Dashboard';
import Experiment from '../pages/Experiment';
import ExperimentInfo from '../pages/ExperimentInfo';
import ExperimentFigures from '../pages/ExperimentFigures';
import ExperimentReports from '../pages/ExperimentReports';
import ExperimentConsole from '../pages/ExperimentConsole';
import ExperimentBrowse from '../pages/ExperimentBrowse';
import ExperimentBrowseZip from '../pages/ExperimentBrowseZip';

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
          path: 'figures',
          component: ExperimentFigures
        },
        {
          path: 'reports',
          component: ExperimentReports
        },
        {
          path: 'console',
          component: ExperimentConsole
        },
        {
          path: 'browse:path(/.*)?',
          component: ExperimentBrowse
        },
        {
          path: 'browse_zip:path(/.*)?',
          component: ExperimentBrowseZip
        }
      ]
    }
  ]
});

export default router;
