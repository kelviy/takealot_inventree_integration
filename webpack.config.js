const path = require('path');

module.exports = {
  entry: './static/takealot_integration/js/TakealotPlugin.js', // your entry file
  output: {
    path: path.resolve(__dirname, 'static/takealot_integration/dist'),
    filename: 'bundle.js',
    library: 'TakealotPlugin', // expose globally
    libraryTarget: 'window',   // attach to window.TakealotPlugin
  },
  module: {
    rules: [
      {
        test: /\.(js|jsx)$/,
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader',
        },
      }
    ]
  },
  resolve: {
    extensions: ['.js', '.jsx'],
  },
  mode: 'production' // or 'development' while debugging
};