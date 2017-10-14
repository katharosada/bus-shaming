/*
 * Production configuration
 */

const path = require('path');
const BundleTracker = require('webpack-bundle-tracker');

module.exports = require('./webpack.base.config.js')({
  entry: 'app/app.jsx',
  output: {
    path: path.resolve(__dirname, "dist"),
    filename: '[name]-[hash].js',
    chunkFilename: '[id].chunk.js',
  },
  plugins: [
    new BundleTracker({filename: './webpack-stats.json'})
  ],
});
