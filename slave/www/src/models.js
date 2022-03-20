import { html, render } from "lit-html";
import { services } from "./rest";
import { AppModalDialog } from 'www-util/util';

const rowTemplateModels = (m, type, click, d) => html`
    <tr class="${m.invalid ? `w3-red` : ``}">
        <td>${m.filename}</td>
        <td>${m.size} MB</td>
        <td>
            ${m.invalid ? html`<b>Active</b> but this file could not be loaded properly` : 
            html`${m.future_active ? html`Active after reboot` : m.active ? 
            html`<span class="material-icons-outlined" style="color: green">check_circle</span>` : 
            html`<span class="material-icons-outlined">highlight_off</span>`}`}
        </td>
        <td>
            ${!m.future_active && !m.invalid ? html`<button class="w3-button w3-green" @click=${() => click(type, m.filename)}>Set active</button>` : html``}
        </td>
        <td>
            <span class="material-icons-outlined" style="cursor: pointer" @click=${() => d(type, m.filename)}>delete</span>
        </td>
    </tr>
`

const modelsTemplate = (models, scorers, click, d) => html`
    <link href="style.css" rel="stylesheet"/>
    <div id="responseGeneral"></div>
    <div class="w3-panel">
        <label>Speech Server: </label>
        <input id="speechServer" class="w3-input" type="text"/>
        <button id="save" class="w3-button" style="background-color: lightblue">Save</button>
    </div>
    <div class="w3-panel" >
        <h3>Models</h3>
        <p id="responseModel"></p>
        <div class="w3-panel">
            <table class="w3-table-all">
                <thead>
                    <th>Model</th>
                    <th>Size</th>
                    <th>Active</th>
                    <th style="width: 10%"></th>
                    <th style="width: 5%"></th>
                </thead>
                <tbody>
                    ${models.map(model => rowTemplateModels(model, "model", click, d))}
                </tbody>
            </table>
        </div>
        <div class="w3-panel">
            <input id="file-model" type="file" accept=".pbmm, .tflite"/>
            <button id="upload-model" class="w3-button" style="background-color: lightblue">Upload model</button>
        </div>
        <h3>Scorers</h3>
        <p id="responseScorer"></p>
        <div class="w3-panel">
            <table class="w3-table-all">
                <thead>
                    <th>Scorer</th>
                    <th>Size</th>
                    <th>Active</th>
                    <th style="width: 10%"></th>
                    <th style="width: 5%"></th>
                </thead>
                <tbody>
                    ${scorers.map(scorer => rowTemplateModels(scorer, "scorer", click, d))}
                </tbody>
            </table>
        </div>
        <div class="w3-panel">
            <input id="file-scorer" type="file" accept=".scorer"/>
            <button id="upload-scorer" class="w3-button" style="background-color: lightblue">Upload scorer</button>
        </div>
    </div>
`
const successTemplate = (text) => html`
<link href="style.css" rel="stylesheet"/>
<div class="w3-container w3-green" style="color: white">
    <h2>
        <b>Success</b>
    </h2>
    <p>${text}</p>
</div>
`

const failTemplate = (response) => html`
<link href="style.css" rel="stylesheet"/>
<div class="w3-container w3-red" style="color: white">
    <h2>
        <b>Something went wrong :(</b>
    </h2>
    <p>${response}</p>
</div>
`

const uploadingTemplate = (text) => html`
<link href="style.css" rel="stylesheet"/>
<div class="w3-container w3-grey" style="color: white">
    <h2>File upload in progress. Do not close this window or reload the page</h2>
    <p>${text}</p>
</div>
`

export class AppModels extends HTMLElement {
    
    constructor() {
        super()
    }

    async connectedCallback() {
        this.attachShadow({mode: 'open'})
        this.reload()
    }

    async reload() {
        const modelsJson = await services.models.getModels()
        const models = modelsJson.models 
        const scorersJson = await services.models.getScorers()
        const scorers = scorersJson.scorers

        models.forEach(m => {
            m.size = this.bytesToMb(m.size)
        })
        scorers.forEach(s => {
            s.size = this.bytesToMb(s.size)
        })

        render(modelsTemplate(models, scorers, async (type, name) => {
            const response = await services.config.setConfigValue(type, name)
            const responseContainer = type == 'model' ? this.responseModel : this.responseScorer
            const json = await response.json()
            if(response.status == 200) {
                this.reload()
                render(successTemplate('The changes will be applied after restart'), responseContainer);
            } else {
                this.reload()
                render(failTemplate(json.message), responseContainer);
            }
        }, async (type, name) => {
            const responseContainer = type == 'model' ? this.responseModel : this.responseScorer
            let response = null;
            if(type == "model") {
                response = await services.models.deleteModel(name)
            } else if(type == "scorer") {
                response = await services.models.deleteScorer(name)
            }
            const json = await response.json()
            if(response.status == 200) {
                this.reload()
                render(successTemplate('The model was deleted successfully!'), responseContainer)
            } else {
                render(failTemplate(json.message), responseContainer)
            }
        }), this.shadowRoot)

        const speech = await services.config.getConfigValue('speech_server')
        this.responseModel = this.shadowRoot.querySelector('#responseModel')
        this.responseScorer = this.shadowRoot.querySelector('#responseScorer')
        this.uploadModel = this.shadowRoot.querySelector('#upload-model')
        this.uploadScorer = this.shadowRoot.querySelector('#upload-scorer')
        this.modelInput = this.shadowRoot.querySelector('#file-model')
        this.scorerInput = this.shadowRoot.querySelector('#file-scorer')
        this.responseGeneral = this.shadowRoot.querySelector('#responseGeneral')
        this.speechServer = this.shadowRoot.querySelector('#speechServer')
        this.save = this.shadowRoot.querySelector('#save')
        this.speechServer.value = speech.speech_server
        this.save.addEventListener('click', async () => {
            let response = await services.config.setConfigValue('speech_server', this.speechServer.value);
            this.openConfigDialog(response.status, 'The changes have been successfully applied!');
        });

        if(modelsJson.invalid_model) {
            render(failTemplate(html`An invalid model file has been loaded! Try selecting another model! <b>The voice recognition is currently not active.</b>`), this.responseGeneral)
        } else if(scorersJson.invalid_scorer) {
            render(failTemplate(html`An invalid scorer file has been loaded! Try selecting another scorer! <b>The voice recognition is currently not active.</b>`), this.responseGeneral)
        }

        this.uploadModel.addEventListener('click', async c => {
            this.uploadModelScorer(this.modelInput.files[0], false)
        })
        this.uploadScorer.addEventListener('click', async c => {
            this.uploadModelScorer(this.scorerInput.files[0], true)
        })
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

    async uploadModelScorer (file, isScorer) {
        const responseDiv = !isScorer ? this.responseModel : this.responseScorer
        render(uploadingTemplate('Uploading model ' + file.name + "..."), responseDiv)
            window.onbeforeunload = function() {
                return "Upload in progress!";
            }
            const response = !isScorer ? await services.models.uploadModel(file) : await services.models.uploadScorer(file)
            if(response.status == 200) {
                render(successTemplate('Uploading model ' + file.name + " was successful!"), responseDiv)
                if(!isScorer) {
                    this.uploadModel.value = ""
                } else {
                    this.uploadScorer.value = ""
                }
                this.reload()
            } else {
                const json = await response.json()
                render(failTemplate(json.message), responseDiv)
            }
            window.onbeforeunload = null
    }

    bytesToMb (bytes) {
        const size = bytes / 1000000
        return Math.round(size * 100) / 100
    }
}

customElements.define('app-models', AppModels)