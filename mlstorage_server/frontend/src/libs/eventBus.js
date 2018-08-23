import Vue from 'vue';

class EventBus {
  constructor () {
    this._bus = new Vue();
  }

  /** Register / unregister manual reloader */
  addReloader (handler) {
    this._bus.$on('reload', handler);
  }

  removeReloader (handler) {
    this._bus.$off('reload', handler);
  }

  callReloader () {
    this._bus.$emit('reload');
  }

  /** The loading flag. */
  watchLoadingFlag (handler) {
    this._bus.$on('loadingFlag', handler);
  }

  unwatchLoadingFlag (handler) {
    this._bus.$off('loadingFlag', handler);
  }

  setLoadingFlag (loading) {
    this._bus.$emit('loadingFlag', loading);
  }

  /** The error message event. */
  addErrorHandler (handler) {
    this._bus.$on('error', handler);
  }

  removeErrorHandler (handler) {
    this._bus.$off('error', handler);
  }

  setError ({ message, title }) {
    this._bus.$emit('error', {hasError: !!message, message: message, title: title});
  }

  unsetError () {
    this._bus.$emit('error', {hasError: false});
  }
}

const eventBus = new EventBus();
export default eventBus;
