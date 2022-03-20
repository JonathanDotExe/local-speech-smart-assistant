import { render, html } from 'lit-html';
import { services } from './rest';
import { AppModalDialog } from 'www-util/util.js';

const rowTemplate = (client, rooms, onRowSelect, onDelete) => html`
    <tr style="cursor: pointer">
        <td @click=${e => onRowSelect(client)}>${client.id}</td>
        <td @click=${e => onRowSelect(client)}>${client.name}</td>
        <td @click=${e => onRowSelect(client)}>${client.room_id != null ? rooms.get(client.room_id) : "No room selected"}</td>
        <td @click=${e => onRowSelect(client)}>${client.is_online ? client.ip : "-"}</td>
        <td @click=${e => onRowSelect(client)}>${client.is_online ? html`<span class="material-icons-outlined" style="color: green">check_circle</span>` : html`<span class="material-icons-outlined" style="color: red">highlight_off</span>`}</td>
        <td>
            <a @click=${async e => onDelete(client)} class="material-icons-outlined" style="cursor: pointer;">delete</a>
        </td>
    </tr>
`

const clientsTemplate = (clients, rooms, onRowSelect, onDelete) => html`
    <link href="style.css" rel="stylesheet"/>
    <div class="w3-panel">
        <div id="response"></div>
        <h3>Clients</h3>
        <table class="w3-table-all">
            <thead>
                <th>ID</th>
                <th>Name</th>
                <th>Room</th>
                <th>IP-address</th>
                <th>Online status</th>
                <th></th>
            </thead>
            <tbody>
                ${clients.map(c => rowTemplate(c, rooms, onRowSelect, onDelete))}
            </tbody>
        </table>
    </div>
`

const confirmDeleteClientTemplate = (dialog, onConfirm) => html`<link href="style.css" rel="stylesheet"/>
<div class="w3-container" style="background-color: lightblue">
    <h2>Do you really want to remove this client?</h2>
</div>
<div class="w3-container">
    <p>
        This will remove all configurations such as the set client
    </p>
    <button class="w3-button" @click=${() => dialog.close()}>Cancel</button>
    <button class="w3-button w3-red" @click=${async () => onConfirm()}>Remove client</button>
</div>`

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

export class ClientsTable extends HTMLElement {

    constructor() {
        super();
    }

    async connectedCallback() {
        this.attachShadow({mode: 'open'})
        this.responseDiv = undefined
        this.load()
    }

    async load() {
        const clients = await services.clients.getAll()
        const rooms = await services.rooms.getAll()
        const roomMap = new Map()
        rooms.forEach(element => {
            roomMap.set(element.id, element.name)
        });
        render(clientsTemplate(clients, roomMap, (client) => {
            const dialog = new AppModalDialog(new AppClientDetails(this, client, c => {
                dialog.close()
                this.load()
            }))
            dialog.open()
            this.load()
        }, async (client) => {
            removeClient(this, client)
        }), this.shadowRoot)
        this.responseDiv = this.shadowRoot.querySelector('#response')
    }

}

customElements.define('app-clients', ClientsTable)

const clientDetails = (parent, onSave, client, rooms, onSelect) => html`
    <link href="style.css" rel="stylesheet"/>
    <div class="w3-container" style="background-color: lightblue">
        <h2>Client</h2>
    </div>
    <div class="w3-container" style="margin-top: 10px">
        ID: ${client.id}
        <form style="margin-top: 10px; margin-bottom: 10px">
            <label>Room:</label>
            <select id="room_select" class="w3-input" @change="${onSelect}">
                <option value="-1">No room</option>
                ${rooms.map(r => html`
                    <option value="${r.id}" ?selected=${client.room_id === r.id}>${r.name}</option> 
                `)}
            </select>
        </form>
        <button id="save" class="w3-button" style="background-color: lightblue; margin-top: 10px">Save</button>
        <button class="w3-button w3-red" style="margin-left: 10px; margin-top: 10px" @click="${c => {
            removeClient(parent, client, onSave)
        }}">Remove</button>
        <br>
    </div>
    <br>
`

export class AppClientDetails extends HTMLElement {

    constructor(parent, client, onSave) {
        super()
        this.parent = parent
        this.client = client
        this.onSave = onSave
    }

    async connectedCallback() {
        const rooms = await services.rooms.getAll()

        this.attachShadow({mode: 'open'})
        render(clientDetails(this.parent, this.onSave, this.client, rooms, s => {
        }), this.shadowRoot)

        this.roomSelect = this.shadowRoot.querySelector('#room_select')
        this.saveButton = this.shadowRoot.querySelector('#save')
        this.saveButton.addEventListener('click', async c => {
            await services.clients.setRoom(this.client.id, this.roomSelect.value)
            this.onSave()
        })
    }

}

customElements.define('app-client-details', AppClientDetails)

function removeClient(parent, client, onConfirm) {
    const dialog = new AppModalDialog(null);
        dialog.open();
        render(confirmDeleteClientTemplate(dialog, async c => {
            const response = await services.clients.remove(client.id)
            if(response.status == 200) {
                render(successTemplate(html`The client has been removed`), parent.responseDiv)
            } else {
                const json = await response.json()
                render(failTemplate(json.message), parent.responseDiv)
            }
            if(onConfirm)
                onConfirm()
            dialog.close()
            parent.load()
        }), dialog.contentElement)
}