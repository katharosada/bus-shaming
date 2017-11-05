/*
 * Development configuration
 */

const path = require('path');
const webpack = require('webpack');

const envPlugin = new webpack.DefinePlugin({
  'process.env':{
    'NODE_ENV': JSON.stringify('development'),
    'API_URL': JSON.stringify('http://localhost:8000/api')
  }
});

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
    envPlugin,
    new webpack.HotModuleReplacementPlugin(),
    new webpack.NoEmitOnErrorsPlugin(),
  ],
});
