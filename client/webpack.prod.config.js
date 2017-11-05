/*
 * Production configuration
 */

const path = require('path');
const BundleTracker = require('webpack-bundle-tracker');
const webpack = require('webpack');

const envPlugin = new webpack.DefinePlugin({
  'process.env':{
    'NODE_ENV': JSON.stringify('production'),
    'API_URL': JSON.stringify('//api')
  }
});


module.exports = require('./webpack.base.config.js')({
  entry: 'app/app.jsx',
  output: {
    path: path.resolve(__dirname, "dist"),
    filename: '[name]-[hash].js',
    chunkFilename: '[id].chunk.js',
  },
  plugins: [
    envPlugin,
    new BundleTracker({filename: './webpack-stats.json'})
  ],
});
