import { render, html } from 'lit-html';

const headerTemplate = (selected) => html`
    <link href="style.css" rel="stylesheet"/>
    <div class="banner">
        <h1>Local Speech - Slave</h1>
    </div>
    <nav class="w3-bar">
        <a href="index.html" class="w3-bar-item ${selected == 'assistant' ? 'nav-active' : ''}">Assistant</a>
        <a href="models.html" class="w3-bar-item ${selected == 'models' ? 'nav-active' : ''}">Speech model</a>
        <a href="system.html" class="w3-bar-item ${selected == 'system' ? 'nav-active' : ''}">System</a>
    </nav>
`

export class AppHeader extends HTMLElement{

    constructor() {
        super();
    }

    async connectedCallback() {
        let selected = this.getAttribute("selected");
        this.attachShadow({mode: 'open'});
        render(headerTemplate(selected), this.shadowRoot);
    }

}

customElements.define('slave-app-header', AppHeader)