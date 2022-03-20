import { render, html } from 'lit-html';

const headerTemplate = (selected) => html`
    <link href="style.css" rel="stylesheet"/>
    <div class="banner">
        <h1>Local Speech - Control Panel</h1>
    </div>
    <nav class="w3-bar">
        <a href="index.html" class="w3-bar-item ${selected == 'dashboard' ? 'nav-active' : ''}">Dashboard</a>
        <a href="plugins.html" class="w3-bar-item ${selected == 'plugins' ? 'nav-active' : ''}">Plugins</a>
        <a href="rooms.html" class="w3-bar-item ${selected == 'rooms' ? 'nav-active': ''}">Rooms</a>
        <a href="settings.html" class="w3-bar-item ${selected == 'settings' ? 'nav-active' : ''}">Settings</a>
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

customElements.define('master-app-header', AppHeader)