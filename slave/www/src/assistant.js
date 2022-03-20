import { render, html } from 'lit-html';
import { services } from './rest';
import { AppModalDialog } from 'www-util/util';


const configTemplate = (langs) => html`
    <link href="style.css" rel="stylesheet"/>
    <div class="w3-container">
        <h2>Config</h2>
    </div>
    <div class="w3-panel">
        <label>Name</label>
        <input type="text" id="name" class="w3-input">
    </div>
    <div class="w3-panel">
        <label>Wakeword</label>
        <input id="wakeword" class="w3-input" type="text"/>
    </div>
    <div class="w3-panel">
        <label>Noise Gate</label>
        <input id="noiseGate" class="w3-input" type="number" step="0.005"/>
    </div>
    <div class="w3-panel">
        <label>Language</label>
        <select id="languageSelect" class="w3-input">
            ${langs.map(l => html`
                <option value=${l.short} ?selected=${l.isActive}>${l.long}</option>
            `)}
        </select>
    </div>
    <div class="w3-panel">
        <label>Wakeword Beam Width</label>
        <input id="wakewordBeamWidth" class="w3-input" type="number" min="10" max="5000" step="1"/>
    </div>
    <div class="w3-panel">
        <label>Wakeword Record Time Out</label>
        <input id="wakewordRecordTimeOut" class="w3-input" type="number" min="0" max="5" step="0.05"/>
    </div>
    <div class="w3-panel">
        <label>Active Beam Width</label>
        <input id="activeBeamWidth" class="w3-input" type="number" min="10" max="5000" step="1"/>
    </div>
    <div class="w3-panel">
        <label>Active Record Time Out</label>
        <input id="activeRecordTimeOut" class="w3-input" type="number" min="0" max="5" step="0.05"/>
    </div>

    <div class="w3-panel">
        <button id="save" class="w3-button" style="background-color: lightblue">Save</button>
    </div>
`

export class AppConfig extends HTMLElement {

    constructor() {
        super();
    }

    async connectedCallback() {
        const wakeword = await services.config.getConfigValue('wakeword')
        const noiseGate = await services.config.getConfigValue('noise_gate')
        const selectedLang = await services.config.getConfigValue('language')
        // TODO save available languages somewhere
        const langs = [
            {
                short: "de",
                long: "German",
                isActive: (selectedLang.language == "de")
            }, 
            {
                short: "en",
                long: "English",
                isActive: (selectedLang.language == "en")
            }
        ]

        this.attachShadow({mode: 'open'});
        render(configTemplate(langs), this.shadowRoot);

        this.nameInput = this.shadowRoot.querySelector('#name');
        this.wakewordInput = this.shadowRoot.querySelector('#wakeword');
        this.noiseGateInput = this.shadowRoot.querySelector('#noiseGate');
        this.langSelect = this.shadowRoot.querySelector('#languageSelect');
        this.wakewordBeamWidthInput = this.shadowRoot.querySelector('#wakewordBeamWidth');
        this.wakewordRecordTimeOutInput = this.shadowRoot.querySelector('#wakewordRecordTimeOut');
        this.activeBeamWidthInput = this.shadowRoot.querySelector('#activeBeamWidth');
        this.activeRecordTimeOutInput = this.shadowRoot.querySelector('#activeRecordTimeOut');
        this.saveButton = this.shadowRoot.querySelector('#save');

        this.saveButton.addEventListener('click', async () => {
            let response = await services.config.setConfigValue('name', this.nameInput.value);
            if (response.status == 200)
                response = await services.config.setConfigValue('wakeword', this.wakewordInput.value);
            if (response.status == 200)
                response = await services.config.setConfigValue('noise_gate', this.noiseGateInput.value);
            if (response.status == 200)
                response = await services.config.setConfigValue('language', this.langSelect.value);
            if (response.status == 200)
                response = await services.config.setConfigValue('wakeword_beam_width', this.wakewordBeamWidthInput.value);
            if (response.status == 200)
                response = await services.config.setConfigValue('wakeword_record_time_out', this.wakewordRecordTimeOutInput.value);
            if (response.status == 200)
                response = await services.config.setConfigValue('active_beam_width', this.activeBeamWidthInput.value);
            if (response.status == 200)
                response = await services.config.setConfigValue('active_record_time_out', this.activeRecordTimeOutInput.value);
            this.openConfigDialog(response.status, 'The changes have been successfully applied!');
        });

        this.wakewordInput.value = wakeword.wakeword;
        this.noiseGateInput.value = noiseGate.noise_gate;
        this.nameInput.value = (await services.config.getConfigValue('name')).name;
        this.wakewordBeamWidthInput.value = (await services.config.getConfigValue('wakeword_beam_width')).wakeword_beam_width;
        this.wakewordRecordTimeOutInput.value = (await services.config.getConfigValue('wakeword_record_time_out')).wakeword_record_time_out;
        this.activeBeamWidthInput.value = (await services.config.getConfigValue('active_beam_width')).active_beam_width;
        this.activeRecordTimeOutInput.value = (await services.config.getConfigValue('active_record_time_out')).active_record_time_out;
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

customElements.define('app-config', AppConfig)


const connectTemplate = (connected) => html`
    <link href="style.css" rel="stylesheet"/>
    <div class="w3-container">
        <h2>Connect to Master</h2>
    </div>
    <div class="w3-panel">
        <label>URL</label>
        <input type="text" id="url" class="w3-input">
    </div>
    <div class="w3-panel">
        <label>Password</label>
        <input type="password" id="password" class="w3-input">
    </div>
    <div class="w3-panel">
        <button id="connect" class="w3-button" style="background-color: lightblue">
            ${connected ? html`<span class="material-icons-outlined" style="color: green; vertical-align: middle;">check_circle</span>` :
            html`<span class="material-icons-outlined" style="color: red; vertical-align: middle;">cancel</span>`}
            <span class="vertical-align: middle;"> Connect</span>
        </button>
    </div>
    <div id="alert" class="w3-container w3-red" style="display: none">
        <h3>Error</h3>
        <p>Couldn't connect to the master! Make sure the master online and your password and URL are correct!</p>
    </div>
    <div id="success" class="w3-container w3-green" style="display: none">
        <h3>Success</h3>
        <p>Connected to new master!</p>
    </div>
`

export class AppConnector extends HTMLElement {

    constructor() {
        super();
    }

    async render() {
        const connected = await services.system.isConnected();
        render(connectTemplate(connected), this.shadowRoot);
        this.urlField = this.shadowRoot.querySelector('#url');
        this.passwordField = this.shadowRoot.querySelector('#password');
        this.connectButton = this.shadowRoot.querySelector('#connect');
        this.successDialog = this.shadowRoot.querySelector('#success')
        this.alertDialog = this.shadowRoot.querySelector('#alert');
        this.connectButton.addEventListener('click', async () => {
            const success = await services.system.connect(this.urlField.value, this.passwordField.value);
            if (success) {
                await this.render();
                //Success
                this.alertDialog.style.display = 'none';
                this.successDialog.style.display = 'block';
            }
            else {
                await this.render();
                //Try again
                this.alertDialog.style.display = 'block';
                this.successDialog.style.display = 'none';
            }
        });
        this.urlField.value = (await services.config.getConfigValue('api_url')).api_url;
    }

    async connectedCallback() {
        this.attachShadow({mode: 'open'});
        await this.render();
    }

}

customElements.define('app-connector', AppConnector)