import { render, html } from 'lit-html';
import { services } from './rest';

const loginTemplate = () => html`
    <link href="style.css" rel="stylesheet"/>
    <div style="width: 700px;">
        <div class="w3-container" style="background-color: lightblue">
            <h2>Login</h2>
        </div>
        <div class="w3-panel">
            <label>Password</label>
            <input type="password" id="password" class="w3-input">
        </div>
        <div class="w3-panel">
            <button id="login" class="w3-button" style="background-color: lightblue">Login</button>
        </div>
        <div id="alert" class="w3-container w3-red" style="display: none">
            <h3>Error</h3>
            <p>Password is incorrect!</p>
        </div>
    </div>
`

export class AppLogin extends HTMLElement {

    constructor() {
        super();
    }

    async connectedCallback() {
        this.attachShadow({mode: 'open'});
        render(loginTemplate(), this.shadowRoot);
        this.passwordField = this.shadowRoot.querySelector('#password');
        this.loginButton = this.shadowRoot.querySelector('#login');
        this.alertDialog = this.shadowRoot.querySelector('#alert')
        this.loginButton.addEventListener('click', async () => {
            const success = await services.login.login(this.passwordField.value);
            if (success) {
                //Redirect
                const params = new URLSearchParams(window.location.search);
                let redir = params.get('redir');
                if (!redir) {
                    redir = "index.html";
                }
                window.location.href = redir;
            }
            else {
                //Try again
                this.alertDialog = this.alertDialog.style.display = 'block';
            }
        });
    }

}

customElements.define('app-login', AppLogin)