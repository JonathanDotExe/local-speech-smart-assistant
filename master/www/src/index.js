import '../styles/style.scss'
import 'www-util'
import './app.js'
import './login.js'
import './plugins.js'
import './settings.js'
import 'material-icons/iconfont/material-icons.css'
import 'jsoneditor/dist/jsoneditor.min.css'
import { services } from './rest';
import './clients.js'
import './rooms.js'

window.addEventListener('load', async () => {
    //Login
    if (!(await services.login.isLoggedIn()) && !window.location.href.includes('login.html')) { //FIXME
        window.location.href = 'login.html?redir=' + window.location.href;
    }
});