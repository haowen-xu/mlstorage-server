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

export function toString (val) {
  return val == null
    ? ''
    : typeof val === 'object' && Object.getPrototypeOf(val).toString === val.toString
      ? JSON.stringify(val, null, 2)
      : String(val);
}

export function formatMetricValue (value) {
  if (typeof value === 'object' && value !== null && !Array.isArray(value) &&
      value.mean !== undefined) {
    const std = value.std || value.stddev;
    if (std !== undefined) {
      return `${toString(value.mean)} (±${toString(std)})`;
    } else {
      return `${toString(value.mean)}`;
    }
  } else {
    return `${toString(value)}`;
  }
}

export function deepIsEqual (a, b) {
  if (Array.isArray(a) && Array.isArray(b)) {
    if (a.length !== b.length) {
      return false;
    }
    for (let i = 0; i < a.length; ++i) {
      if (!deepIsEqual(a[i], b[i])) {
        return false;
      }
    }
    return true;
  } else if (typeof a === 'object' && typeof b === 'object' &&
             a !== null && b !== null) {
    const aKeys = Object.keys(a);
    const bKeys = Object.keys(b);

    if (aKeys.length !== bKeys.length) {
      return false;
    }

    const aKeysHash = aKeys.map(key => {
      return {[key]: true};
    });
    for (const key of bKeys) {
      if (aKeysHash[key] !== true) {
        return false;
      }
    }

    // now the keys set of `a` and `b` must be equal
    for (const key of aKeys) {
      if (!deepIsEqual(a[key], b[key])) {
        return false;
      }
    }

    return true;
  } else {
    return a === b;
  }
}

export const defaultResultFilter = '^(?!__)((.*_)?(n?ll|bpd|loss|acc(uracy)?|lb)(_.*)?|epoch|eta|lr)$';
