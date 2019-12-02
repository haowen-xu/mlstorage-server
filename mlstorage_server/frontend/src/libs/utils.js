/* eslint-disable camelcase */
import moment from 'moment';

export function getExtendedStatus ({status, exit_code}, dateDiff) {
  if (status === 'RUNNING') {
    if (dateDiff > 3600) {
      return 'LOST';
    } else if (dateDiff > 300) {
      return 'Maybe LOST';
    }
  }
  if (status === 'COMPLETED' && exit_code) {
    return 'FAILED';
  }
  return status;
}

export function statusToBootstrapClass ({status, exit_code}, dateDiff, completeClass) {
  status = getExtendedStatus({status: status, exit_code: exit_code}, dateDiff);
  if (status === 'RUNNING') {
    return 'primary';
  } else if (status === 'Maybe LOST') {
    return 'warning';
  } else if (status === 'FAILED' || status === 'LOST') {
    return 'danger';
  } else {
    return completeClass;
  }
}

export function formatDateTime (timestamp, format) {
  return moment.utc(timestamp * 1000).local().format(format || 'LLL');
}

export const defaultResultFilter = '^(?!__)((.*_)?(n?ll|bpd|loss|acc(uracy)?|lb)(_.*)?|epoch|eta|lr)$';
