module.exports = {
    devServer: {
        proxy: {
            '^/v1': {
                target: 'http://mlserver.ipwx.me:7965',
                ws: true,
                changeOrigin: true
            }
        }
    },
    runtimeCompiler: true,
    outputDir: "../assets/",
    assetsDir: "static/",
};
