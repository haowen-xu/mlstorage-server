<template>
  <div id="app" class="app-wrapper">
    <router-view class="app-content"/>
  </div>
</template>

<style>
html, body {
  margin: 0;
  padding: 0;
  width: 100%;
  height: 100%;
}
html, body, h1, h2, h3, h4, h5, h6 {
  font-family: "Helvetica Neue", Helvetica, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "微软雅黑",
               "WenQuanYi Micro Hei", "Liberation Sans", Arial, sans-serif;
}
.app-wrapper, .app-content {
  height: 100%;
  overflow: auto;
}
</style>
