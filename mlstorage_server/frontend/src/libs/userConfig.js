import store from 'store';

/** Make a config proxy from the specified object. */
function makeConfig (obj) {
  const ret = {};
  for (const key of Object.keys(obj)) {
    const defaultValue = obj[key];
    Object.defineProperty(ret, key, {
      get: () => {
        const ret = store.get(key);
        if (typeof ret === 'undefined') {
          return defaultValue;
        }
        return ret;
      },
      set: (value) => {
        store.set(key, value);
      }
    });
  }
  return ret;
} // makeConfig

class UserConfig {
  constructor () {
    this._dashboard = makeConfig({
      pageId: 1,
      pageSize: 10,
      queryString: ''
    });
  }

  get dashboard () { return this._dashboard; }
}

const userConfig = new UserConfig();
export default userConfig;
