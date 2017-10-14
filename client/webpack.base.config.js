const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');

const HtmlWebpackPluginConfig = new HtmlWebpackPlugin({
  inject: 'true',
  template: 'app/index.html'
});


module.exports = (options) => ({
  entry: './app/app.jsx',
  output: Object.assign({
    path: path.resolve(__dirname, "build"),
  }, options.output),
  module: {
    loaders: [
      {
        test: /\.js$/,
        loader: 'babel-loader',
        exclude: /node_modules/,
        query: {
          presets: ['es2015','react']
        }
      },
      {
        test: /\.jsx$/,
        loader: 'babel-loader',
        exclude: /node_modules/,
        query: {
          presets: ['es2015','react']
        }
      }
    ]
  },
  plugins: options.plugins.concat([HtmlWebpackPluginConfig])
});
