/*
 * Development configuration
 */

const path = require('path');
const webpack = require('webpack');

module.exports = require('./webpack.base.config.js')({
  entry: [
    'webpack-hot-middleware/client?reload=true',
    'app/app.jsx',
  ],
  output: {
    path: path.resolve(__dirname, "build"),
    filename: '[name].js',
    chunkFilename: '[name].chunk.js',
  },
  plugins: [
    new webpack.HotModuleReplacementPlugin(),
    new webpack.NoEmitOnErrorsPlugin(),
  ],
});
