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

export function formatDuration (duration, precision = 0) {
  const isAgo = duration < 0;
  const precBase = Math.pow(10, precision);
  duration = Math.round(Math.abs(duration) * precBase) / precBase;

  function format02d (x) {
    const ret = '00' + x;
    return ret.substr(ret.length - 2);
  }

  function formatTime (seconds, popLeadingZero) {
    // first of all, extract the hours and minutes part
    const residual = [];
    for (const unit of [3600, 60]) {
      const thisUnitVal = Math.floor(seconds / unit);
      residual.push(thisUnitVal);
      seconds = seconds - thisUnitVal * unit;
    }

    // format the hours and minutes
    const segments = [];
    for (const r of residual) {
      if (segments.length === 0 && popLeadingZero) {
        if (r !== 0) {
          segments.push(String(r));
        }
      } else {
        segments.push(format02d(String(r)));
      }
    }

    // break seconds into int and real number part
    let secondsInt = Math.floor(seconds);
    let secondsReal = seconds - secondsInt;

    // format the seconds
    if (segments.length !== 0) {
      secondsInt = format02d(secondsInt);
    } else {
      secondsInt = String(secondsInt);
    }
    secondsReal = String(Math.round(secondsReal * precBase) / precBase).replace(/(^0+)|(0+$)/, '');
    if (secondsReal === '.') {
      secondsReal = '';
    }
    const secondsSuffix = segments.length === 0 ? 's' : '';
    segments.push(`${secondsInt}${secondsReal}${secondsSuffix}`);

    // now compose the final time str
    return segments.join(':');
  }

  let ret;
  if (duration < 86400) {
    ret = formatTime(duration, true);
  } else {
    const days = Math.ceil(duration / 86400);
    duration = duration - days * 86400;
    const timeStr = formatTime(duration, false);
    ret = `${days}d ${timeStr}`;
  }

  if (isAgo) {
    ret += ' ago';
  }

  return ret;
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
