import { render, html } from 'lit-html';

const dialogTemplate = (dialog) => html`
    <link href="style.css" rel="stylesheet"/>
    <div id="dialog" class="w3-modal w3-show">
        <div class="w3-modal-content">
            <span class="w3-button w3-display-topright" style="background-color: rgb(0,0,0,0)" @click=${e => {
                dialog.close();
            }}>&times;</span>
            <div id="content">
                
            </div>
        </div>
    </div>
`;

export class AppModalDialog extends HTMLElement {

    constructor(content) {
        super();
        this.content = content;
    }

    async connectedCallback() {
        this.attachShadow({mode: 'open'});
        render(dialogTemplate(this), this.shadowRoot)
        this.contentElement = this.shadowRoot.querySelector('#content');
        if (this.content) {
            this.contentElement.appendChild(this.content);
        }
    }

    close() {
        this.remove();
    }

    open() {
        console.log('Open')
        document.body.appendChild(this);
    }

}

customElements.define('app-dialog', AppModalDialog)