const VueLoaderPlugin = require('vue-loader/lib/plugin')
const webpack = require('webpack')
const path = require('path')
const MiniCssExtractPlugin = require("mini-css-extract-plugin");

module.exports = (env, argv) => {
  const mode = !!argv && !!argv.mode ? argv.mode : env

  let devtool
  switch(mode) {
    case 'production':
      devtool = false
      break

    case 'development':
      devtool = 'inline-source-map'
      break

    case 'test':
      break

    default:
      throw `not supported mode: ${mode}`
  }

  return {
    devtool: devtool,
    entry: {
      'consumption/static/consumption/packed/js/summary': './src/consumption/summary',
    },
    output: {
      path: path.resolve(__dirname, '../'),
      filename: '[name].js'
    },
    plugins: [
      new webpack.ProvidePlugin({ $: 'jquery', jQuery: 'jquery' }),
      new VueLoaderPlugin(),
      new MiniCssExtractPlugin({
        filename: "[name].css",
      }),
    ],
    module: {
      rules: [
        {test: /\.js$/, exclude: /node_modules/, use: ['babel-loader', 'eslint-loader']},
        {test: /\.vue$/, use: ['vue-loader', 'eslint-loader']},
        {
          test: /\.css$/,
          use: [MiniCssExtractPlugin.loader, 'css-loader']
        },
      ],
    },
    resolve: {
      alias: {
        'vue': 'vue/dist/vue.common.js',
      },
    }
  }
}
