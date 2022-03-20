import { render, html } from 'lit-html';
import { services } from './rest';
import { AppModalDialog } from 'www-util/util.js';

const rowTemplate = (room, table) => html`
    <link href="style.css" rel="stylesheet"/>
    <tr>
        <td>${room.name}</td>
        <td>
            <a @click=${async e => {
                const dialog = new AppModalDialog(new AppEditRoom(room, c => {
                    table.load()
                    dialog.close()
                }))
                dialog.open()
            }} class="material-icons-outlined" style="cursor: pointer">edit</a>
            <a @click=${async e => {
                await services.rooms.delete(room.id)
                table.load()
            }} class="material-icons-outlined" style="cursor: pointer; right: 40%">delete</a>
        </td>
    </tr>
`

const roomsTemplate = (rooms, table) => html`
    <link href="style.css" rel="stylesheet"/>
    <div class="w3-panel">
        <button class="w3-button" style="background-color: lightblue; margin-bottom: 10px" @click=${e => {
            const dialog = new AppModalDialog(new AppCreateRoom(c => {
                table.load()
                dialog.close()
            }))
            dialog.open();
        }}>Create room</button>
        <table class="w3-table-all">
            <thead>
                <th>Room</th>
                <th></th>
            </thead>
            <tbody>
                ${rooms.map(r => rowTemplate(r, table))}
            </tbody>
        </table>
    </div>
`

export class AppRooms extends HTMLElement {

    constructor() {
        super()
    }

    async connectedCallback() {
        this.attachShadow({mode: 'open'});
        this.load()
    }

    async load() {
        const rooms = await services.rooms.getAll()
        render(roomsTemplate(rooms, this), this.shadowRoot)
    }

}

customElements.define('app-rooms', AppRooms)

const createRoom = () => html `
    <link href="style.css" rel="stylesheet"/>
    <div class="w3-container" style="background-color: lightblue">
        <h2>Create room</h2>
    </div>
    <div class="w3-container" style="margin: 10px">
        <h3>Room name:</h3>
        <div>
            <input id="nameInput" class="w3-input" type="text" style="margin-bottom:10px"/>
            <button class="w3-button" style="background-color: lightblue" id="save">Save</button>
        </div>
    </div>
    <br>
`

class AppCreateRoom extends HTMLElement {

    constructor(clickListener) {
        super()
        this.saveListener = clickListener
    }

    async connectedCallback() {
        this.attachShadow({mode: 'open'});
        render(createRoom(), this.shadowRoot)

        this.nameInput = this.shadowRoot.querySelector('#nameInput');
        this.saveButton = this.shadowRoot.querySelector('#save');
        this.saveButton.addEventListener('click', async c => {
            await services.rooms.insert(this.nameInput.value)
            this.saveListener()
        })
    }

}

customElements.define('app-create-room', AppCreateRoom)

const editRoom = () => html`
    <link href="style.css" rel="stylesheet"/>
    <div class="w3-container" style="background-color: lightblue">
        <h2>Edit room</h2>
    </div>
    <div class="w3-container" style="margin: 10px">
        <h3>Room name:</h3>
        <div>
            <input id="nameInput" type="text"/>
            <button class="w3-button" style="background-color: lightblue" id="save">Save</button>
        </div>
    </div>
    <br>
`

class AppEditRoom extends HTMLElement {

    constructor(room, clickListener) {
        super()
        this.room = room
        this.saveListener = clickListener
    }

    async connectedCallback() {
        this.attachShadow({mode: 'open'});
        render(editRoom(), this.shadowRoot)

        this.nameInput = this.shadowRoot.querySelector('#nameInput');
        this.nameInput.value = this.room.name
        this.saveButton = this.shadowRoot.querySelector('#save');
        this.saveButton.addEventListener('click', async c => {
            await services.rooms.update(this.room.id, this.nameInput.value)
            this.saveListener()
        })
    }
}

customElements.define('app-edit-room', AppEditRoom)