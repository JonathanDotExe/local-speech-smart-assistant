import { html, render } from "lit-html";
import { services } from "./rest";
import { AppModalDialog } from 'www-util/util.js';


const settingsTemplate = () => html`
    <link href="style.css" rel="stylesheet"/>
    <div class="w3-panel">
        <h3>Change Password</h3>
        <div class="w3-panel">
            <label>Current Password</label>
            <input type="password" id="password" class="w3-input">
        </div>
        <div class="w3-panel">
            <label>New Password</label>
            <input type="password" id="new_password" class="w3-input">
        </div>
        <div class="w3-panel">
            <label>Repeat Current Password</label>
            <input type="password" id="repeat_password" class="w3-input">
        </div>
        <div class="w3-panel">
            <button id="change" class="w3-button" style="background-color: lightblue">Change Password</button>
        </div>
        <div id="alert" class="w3-container w3-red" style="display: none">
            <h3>Error</h3>
            <p>The entered passwords are not the same!</p>
        </div>
        <div id="error" class="w3-container w3-red" style="display: none">
            <h3>Error</h3>
            <p>Password is incorrect!</p>
        </div>
        <div id="success" class="w3-container w3-green" style="display: none">
            <h3>Success</h3>
            <p>Successfully updated password!</p>
        </div>
        <hr>
        <h3>System</h3>
        <div class="w3-container">
            <button id="reboot" class="w3-button w3-red">Reboot</button>
            <button id="shutdown" class="w3-button w3-red">Shutdown</button>
        </div>
    </div>
`;

const rebootTemplate = () => html`
    <link href="style.css" rel="stylesheet"/>
    <div class="w3-container" style="background-color: lightblue">
        <h2>Success</h2>
        <p>Rebooting system now ...</p>
    </div>
    <div class="w3-container">
        <p>
            The system will be available again soon!
        </p>
    </div>
`

const shutdownTemplate = () => html`
    <link href="style.css" rel="stylesheet"/>
    <div class="w3-container" style="background-color: lightblue">
        <h2>Success</h2>
        <p>Shutting down system now ...</p>
    </div>
    <div class="w3-container">
        <p>
            You need to start the system again manually!
        </p>
    </div>
`

export class AppSettings extends HTMLElement {

    constructor() {
        super();
    }

    async connectedCallback() {
        this.attachShadow({mode: 'open'});
        render(settingsTemplate(), this.shadowRoot);
        this.passwordField = this.shadowRoot.querySelector('#password');
        this.newPasswordField = this.shadowRoot.querySelector('#new_password');
        this.repeatNewPasswordField = this.shadowRoot.querySelector('#repeat_password');
        this.changeButton = this.shadowRoot.querySelector('#change');
        this.alertDialog = this.shadowRoot.querySelector('#alert');
        this.errorDialog = this.shadowRoot.querySelector('#error');
        this.successDialog = this.shadowRoot.querySelector('#success');
        this.changeButton.addEventListener('click', async () => {
            if (this.newPasswordField.value == this.repeatNewPasswordField.value) {
                const success = await services.login.changePassword(this.passwordField.value, this.newPasswordField.value);
                if (success) {
                    this.alertDialog.style.display = 'none';
                    this.errorDialog.style.display = 'none';
                    this.successDialog.style.display = 'block';
                }
                else {
                    //Try again
                    this.alertDialog.style.display = 'none';
                    this.errorDialog.style.display = 'block';
                    this.successDialog.style.display = 'none';
                }
            }
            else {
                this.alertDialog.style.display = 'block';
                this.errorDialog.style.display = 'none';
                this.successDialog.style.display = 'none';
            }
        });

        this.rebootButton = this.shadowRoot.querySelector('#reboot');
        this.rebootButton.addEventListener('click', async () => {
            const dialog = new AppModalDialog(null);
            dialog.open();
            render(html`<link href="style.css" rel="stylesheet"/>
            <div class="w3-container" style="background-color: lightblue">
                <h2>Do you really want to reboot?</h2>
            </div>
            <div class="w3-container">
                <p>
                    It can take a few minutes until the system rebooted!
                </p>
                <button class="w3-button" @click=${() => dialog.close()}>Cancel</button>
                <button class="w3-button w3-red" @click=${async () => {
                    await services.system.reboot();
                    render(rebootTemplate(), dialog.contentElement)
                }}>Reboot</button>
            </div>`, dialog.contentElement)
        });
        this.shutdownButton = this.shadowRoot.querySelector('#shutdown');
        this.shutdownButton.addEventListener('click', async () => {
            const dialog = new AppModalDialog(null);
            dialog.open();
            render(html`<link href="style.css" rel="stylesheet"/>
            <div class="w3-container" style="background-color: lightblue">
                <h2>Do you really want to shut down?</h2>
            </div>
            <div class="w3-container">
                <p>
                    You will need to start the system again manually!
                </p>
                <button class="w3-button" @click=${() => dialog.close()}>Cancel</button>
                <button class="w3-button w3-red" @click=${async () => {
                    await services.system.shutdown();
                    render(shutdownTemplate(), dialog.contentElement)
                }}>Shutdown</button>
            </div>`, dialog.contentElement)
        });

        this.saveWakewordButton.addEventListener('click', async () => {
            const response = await services.config.setConfigValue('wakeword', this.wakewordInput.value);
            this.openConfigDialog(response.status, 'The changes have been successfully applied!');
        });

        this.saveLanguageButton.addEventListener('click', async () => {
            const response = await services.config.setConfigValue('language', this.langSelect.value);
            this.openConfigDialog(response.status, 'The changes will apply after the next reboot!')
        })

        this.wakewordInput.value = wakeword.wakeword;
    }

    openConfigDialog(response, text) {
        const dialog = new AppModalDialog(null);
        dialog.open();
        if(response == 200) {
            render(html`
                <link href="style.css" rel="stylesheet"/>
                <div class="w3-container" style="background-color: lightblue">
                    <h2>Success</h2>
                </div>
                <div class="w3-container">
                    <p>
                        ${text}
                    </p>
                </div>
            `, dialog.contentElement);
        } else {
            render(html`
                <link href="style.css" rel="stylesheet"/>
                <div class="w3-container w3-red">
                    <h2 style="color: white">Something went wrong</h2>
                </div>
                <div class="w3-container">
                    <p>
                        The changes could not be applied!
                    </p>
                </div>
            `, dialog.contentElement);
        }
    }

}

customElements.define('app-system-settings', AppSettings)