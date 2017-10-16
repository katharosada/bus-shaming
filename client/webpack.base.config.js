const path = require('path');
const ExtractTextPlugin = require('extract-text-webpack-plugin');
const HtmlWebpackPlugin = require('html-webpack-plugin');

const HtmlWebpackPluginConfig = new HtmlWebpackPlugin({
  inject: 'true',
  template: 'app/index.html'
});

const extractLess = new ExtractTextPlugin({
  filename: "[name].css",
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
      },
      {
        test: /\.less$/,
        use: extractLess.extract({
          use: [
            {loader: "css-loader"},
            {loader: "less-loader"}
          ],
            fallback: "style-loader"
          }),
      },
    ]
  },
  plugins: options.plugins.concat([HtmlWebpackPluginConfig, new ExtractTextPlugin('[name].css', {allChunks: true})])
});
