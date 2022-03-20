const path = require('path')
const HtmlWebpackPlugin = require('html-webpack-plugin')
const MiniCssExtractPlugin = require('mini-css-extract-plugin')

module.exports = {
    mode: 'development',
    entry: './src/index.js',
    output: {
        filename: 'bundle.js',
        path: path.resolve(__dirname, 'dist')
    },
    module: {
        rules: [
            {
                test: /\.s[ac]ss$/,
                use: [MiniCssExtractPlugin.loader, 'css-loader', 'sass-loader']
            },
            {
                test: /\.css$/i,
                use: [MiniCssExtractPlugin.loader, 'css-loader']
            },
            {
                test: /\.(woff(2)?|ttf|eot|svg)(\?v=[0-9]\.[0-9]\.[0.9])?$/,
                loader: 'url-loader',
                options: {
                    limit: 8192,
                    name: '[name].[ext]',
                    outputPath: 'assets'
                }
            }
        ]
    },
    plugins: [
        new MiniCssExtractPlugin({
            filename: 'style.css'
        }),
        new HtmlWebpackPlugin({
            filename: 'index.html',
            template: './static/index.html'
        }),
        new HtmlWebpackPlugin({
            filename: 'login.html',
            template: './static/login.html'
        }),
        new HtmlWebpackPlugin({
            filename: 'system.html',
            template: './static/system.html'
        }),
        new HtmlWebpackPlugin({
            filename: 'models.html',
            template: './static/models.html'
        })
    ],
    devServer: {
        proxy: {
            '/api': {
                target: 'https://localhost:8070',
                pathRewrite: { '^/api': '' },
                secure: false
            }
        },
        disableHostCheck: true
    }
}