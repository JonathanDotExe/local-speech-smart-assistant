import { render, html } from 'lit-html';
import { services } from './rest';
import { AppModalDialog } from 'www-util/util.js';
import 'material-icons/iconfont/material-icons.css'

import JSONEditor from "jsoneditor";

const rowTemplate = (plugin, table) => html`
    <tr style=${plugin.name == "Invalid" ? "background-color: lightsalmon" : ""}>
        <td>${plugin.name}</td>
        <td>${plugin.filename}</td>
        <td>${plugin.description.replace("\n", "<br>")}</td>
        <td><input type="checkbox" class="w3-check" ?checked=${plugin.active} disabled/></td>
        <td><a @click=${e => {
                const dialog = new AppModalDialog(new AppPluginView(plugin, table))
                dialog.open();
            }} class="material-icons-outlined" style="cursor: pointer;">description</a>
            <a @click=${async e => {
                await services.plugins.delete(plugin.filename);
                await table.reload();
            }} class="material-icons-outlined" style="cursor: pointer;">delete</a>
        </td>
    </tr>
`;

const pluginsTemplate = (plugins, table) => html`
    <link href="style.css" rel="stylesheet"/>
    <table class="w3-table-all">
        <thead>
            <th>Name</th>
            <th>Filename</th>
            <th>Description</th>
            <th>Active</th>
            <th></th>
        </thead>
        <tbody>
            ${plugins.map(p => rowTemplate(p, table))}
        </tbody>
    </table>
    <div class="w3-panel">
        Upload Plugin: <input id="file" type="file" accept="application/zip"/><button id="upload" class="w3-button">Upload</button>
    </div>
`;

export class AppPluginsTable extends HTMLElement{

    constructor() {
        super();
    }

    async connectedCallback() {
        this.attachShadow({mode: 'open'});
        await this.reload();
        this.uploadElement.addEventListener('click', async e => {
            if (this.fileElement.files[0]) {
                if (await services.plugins.uploadPlugin(this.fileElement.files[0])) {
                    this.fileElement.value = "";
                    await this.reload();

                    const dialog = new AppModalDialog(null);
                    dialog.open();
                    render(html`
                        <link href="style.css" rel="stylesheet"/>
                        <div class="w3-container" style="background-color: lightblue">
                            <h2>Success</h2>
                            <p>Sucessfully uploaded plugin</p>
                        </div>
                        <div class="w3-container">
                            <p>
                                You can now use the commands of this plugin in your voice system!
                            </p>
                        </div>
                    `, dialog.contentElement);
                }
                else {
                    const dialog = new AppModalDialog(null);
                    dialog.open();
                    render(html`
                        <link href="style.css" rel="stylesheet"/>
                        <div class="w3-container w3-red">
                            <h2>Error</h2>
                            <p>Invalid plugin file</p>
                        </div>
                        <div class="w3-container">
                            <p>
                                Try uploading a valid plugin .zip - file!
                            </p>
                        </div>
                    `, dialog.contentElement);
                }
            }
        });
    }

    async reload() {
        const plugins = await services.plugins.getAll();
        console.log(plugins)
        render(pluginsTemplate(plugins, this), this.shadowRoot);
        this.uploadElement = this.shadowRoot.querySelector('#upload');
        this.fileElement = this.shadowRoot.querySelector('#file');
    }

}
customElements.define('app-plugins-table', AppPluginsTable)

const commandsTemplate = (plugin, language) => html`
    ${
        plugin.commands.map(cmd => html`
            <details class="accordion">
                <summary>
                    ${cmd.name}
                </summary>
                <div class="w3-panel">
                    <p>${cmd.description.replace("\n", "<br>")}</p>
                    <table class="w3-table-all">
                        <thead>
                            <th>Aliases</th>
                        </thead>
                        <tbody>
                            ${cmd.aliases[language].map(p => html`
                                <tr>
                                    <td>${p}</td>
                                </tr>
                            `)}
                        </tbody>
                    </table>
                    </div>
                </div>
            </details>
        `)
    }
`;

const pluginTemplate = (plugin) => html`
    <link href="style.css" rel="stylesheet"/>
    <div class="w3-container" style="background-color: lightblue">
        <h2>${plugin.name}</h2>
        <p>${plugin.filename}</p>
        <p>${plugin.description}</p>
    </div>
    <div class="w3-panel">
        <input id="active" type="checkbox" class="w3-check"/>
        <label>Active</label>
    </div>
    <div class="w3-panel" id="customHTML"></div>
    <div class="w3-container">
        <h3>Config</h3>
        <div id="jsoneditor"></div>
    </div>
    <div class="w3-panel">
        <button id="save" class="w3-button">Save</button>
    </div>
    <div class="w3-container">
        <h3>Commands</h3>
        <p>Language:
            <select id="language">
                
            </select>
        </p>
    </div>
    <div class="w3-container" id="commands">
        
    </div>
    <br>
`;


class AppPluginView extends HTMLElement {

    constructor(plugin, table) {
        super();
        this.table = table;
        this.plugin = plugin;
        this.languages = []
        for (let cmd of this.plugin.commands) {
            for (let lang in cmd.aliases) {
                if (!this.languages.includes(lang)) {
                    this.languages.push(lang)
                }
            }
        }
    }

    async connectedCallback() {
        this.attachShadow({mode: 'open'});
        render(pluginTemplate(this.plugin, 'de'), this.shadowRoot);
        this.commandsElement = this.shadowRoot.querySelector('#commands');
        this.configElement = this.shadowRoot.querySelector('#jsoneditor');
        this.saveButton = this.shadowRoot.querySelector('#save');
        this.activeCheckbox = this.shadowRoot.querySelector('#active');
        this.customHTMLContainer = this.shadowRoot.querySelector('#customHTML');
        this.editor = new JSONEditor(this.configElement, {
            mode: 'text'
        });
        this.activeCheckbox.checked = this.plugin.active;
        this.customHTMLContainer.innerHTML = this.plugin.html;
        //Config
        this.editor.set(this.plugin.config);
        this.saveButton.addEventListener('click', async e => {
            this.plugin.active = this.activeCheckbox.checked
            this.plugin.config = this.editor.get();
            await services.plugins.update(this.plugin);
            const dialog = new AppModalDialog(null);
            dialog.open();
            await this.table.reload();
            render(html`
                <link href="style.css" rel="stylesheet"/>
                <div class="w3-container" style="background-color: lightblue">
                    <h2>Success</h2>
                    <p>Sucessfully updated plugin config!</p>
                </div>
                <div class="w3-container">
                    <p>
                        The changes are active now!
                    </p>
                </div>
            `, dialog.contentElement);
        })
        //Languages
        this.languageElement = this.shadowRoot.querySelector('#language');
        for (let lang of this.languages) {
            const option = document.createElement('option')
            option.text = lang;
            option.value = lang;
            this.languageElement.add(option);
        }
        this.languageElement.addEventListener('change', e => {
            render(commandsTemplate(this.plugin, this.languageElement.value), this.commandsElement);
        })
        this.languageElement.value = 'de';
        render(commandsTemplate(this.plugin, this.languageElement.value), this.commandsElement);
    }

}

customElements.define('app-plugin-view', AppPluginView)