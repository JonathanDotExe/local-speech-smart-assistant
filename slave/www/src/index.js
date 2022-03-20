import 'www-util'
import './login.js'
import './app.js'
import './system.js'
import './models.js'
import 'material-icons/iconfont/material-icons.css'
import './assistant.js'
import { services } from './rest';
import '../styles/style.scss'

window.addEventListener('load', async () => {
    //Login
    if (!(await services.login.isLoggedIn()) && !window.location.href.includes('login.html')) { //FIXME
        window.location.href = 'login.html?redir=' + window.location.href;
    }
});