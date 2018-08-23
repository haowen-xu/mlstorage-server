import moment from 'moment';

/**
 * Class to help compute and refresh time-difference related UI elements.
 */
export default class TimeDiff {
  constructor () {
    this._tm = null;
    this._dateText = '';
    this._dateDiff = 0;
    this._interval = null;
    this._refreshRate = null;
    this._hasDestroyed = false;
    this._watchers = [];
  }

  addWatcher (watcher) {
    this._watchers.push(watcher);
  }

  setTimestamp (tm) {
    this._tm = moment.utc(tm * 1000).local();
    this.updateText();
  }

  updateText () {
    const now = moment();
    const dateDiff = Math.floor(Math.abs(this._tm.diff(now)) / 1000);
    this._dateDiff = dateDiff;

    // get the desired refresh rate
    let refreshRate = 0;
    if (dateDiff <= 61) {
      refreshRate = 1;
    } else if (dateDiff <= 3660) {
      refreshRate = 60;
    } else if (dateDiff <= 90000) {
      refreshRate = 3600;
    } else {
      refreshRate = null;
    }

    // update the date text
    if (dateDiff < 60) {
      if (dateDiff >= 2) {
        this._dateText = `${dateDiff} seconds ago`;
      } else if (dateDiff >= 1) {
        this._dateText = '1 second ago';
      } else {
        this._dateText = 'just now';
      }
    } else if (dateDiff < 3600) {
      if (dateDiff >= 120) {
        this._dateText = `${Math.floor(dateDiff / 60)} minutes ago`;
      } else {
        this._dateText = '1 minute ago';
      }
    } else if (dateDiff < 86400) {
      if (dateDiff >= 7200) {
        this._dateText = `${Math.floor(dateDiff / 3600)} hours ago`;
      } else {
        this._dateText = '1 hour ago';
      }
    } else {
      this._dateText = this._tm.format('LLL');
    }

    // create the update updater if necessary
    if (!this._hasDestroyed) {
      if (!refreshRate || refreshRate !== this._refreshRate) {
        if (this._interval) {
          clearInterval(this._interval);
          this._interval = null;
        }
      }
      if (refreshRate && refreshRate !== this._refreshRate) {
        this._interval = setInterval(
          () => this.updateText(),
          refreshRate * 1000
        );
        this._refreshRate = refreshRate;
      }

      // call the watchers
      for (let i = 0; i < this._watchers.length; ++i) {
        this._watchers[i](this._dateText, this._dateDiff);
      }
    } // if (!hasDestroyed)
  }

  destroy () {
    this._hasDestroyed = true;
    if (this._interval) {
      clearInterval(this._interval);
      this._interval = null;
    }
  }
}
