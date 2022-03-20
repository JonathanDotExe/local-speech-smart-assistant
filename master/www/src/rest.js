const API_URL = 'api'

export class LoginService {

    constructor() {

    }

    async isLoggedIn() {
        const response = await fetch(API_URL + '/is_logged_in', { credentials: 'same-origin' })
        const loggedIn = await response.json();
        return loggedIn.logged_in;
    }

    async login(password) {
        const response = await fetch(API_URL + '/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'same-origin',
            body: JSON.stringify({ password: password, remember: false})
        })
        const loggedIn = await response.json();
        return loggedIn.logged_in;
    }

    async changePassword(password, newPassword) {
        const response = await fetch(API_URL + '/changePassword(', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'same-origin',
            body: JSON.stringify({ password: password, new_password: newPassword})
        })
        const loggedIn = await response.json();
        return loggedIn.success;
    }

}

export class PluginService {

    constructor() {

    }

    async getAll() {
        const response = await fetch(API_URL + '/plugins', { credentials: 'same-origin' })
        return await response.json();
    }

    async uploadPlugin(file) {
        const form = new FormData();
        form.append('file', file, file.name);
        const response = await fetch(API_URL + '/plugins/upload', {
            method: 'POST',
            credentials: 'same-origin',
            body: form
        })
        return await response.json();
    }

    async update(plugin) {
        const response = await fetch(API_URL + '/plugins', {
            method: 'POST',
            credentials: 'same-origin',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(plugin)
        })
        return await response.json();
    }

    async delete(filename) {
        const response = await fetch(API_URL + '/plugins/' + filename, {
            method: 'DELETE',
            credentials: 'same-origin'
        })
        return await response.json();
    }

}

export class SystemService {

    async reboot() {
        const response = await fetch(API_URL + '/reboot', {
            method: 'POST',
            credentials: 'same-origin'
        })
    }

    async shutdown() {
        const response = await fetch(API_URL + '/shutdown', {
            method: 'POST',
            credentials: 'same-origin'
        })
    }

}

export class ClientService {
    
    constructor() {

    }

    async getAll() {
        const response = await fetch(API_URL + '/clients', { credentials: 'same-origin' })
        if (!response.ok) {
            return [];
        }
        return await response.json();
    }

    async setRoom(id, room_id) {
        const response = await fetch(API_URL + '/clients/room/' + id + '/' + room_id)
        return await response.status
    }

    async remove(id) {
        const response = await fetch(API_URL + '/client/' + id, {
            method: 'DELETE',
            credentials: 'same-origin'
        })
        return await response
    }
}

export class RoomService {

    constructor() {

    }

    async getAll() {
        const response = await fetch(API_URL + '/rooms', { credentials: 'same-origin' })
        return await response.json();
    }

    async insert(name) {
        const response = await fetch(API_URL + '/rooms/' + name, { 
            method: 'POST',
            credentials: 'same-origin'
        })
        return await response.status;
    }

    async update(id, name) {
        const response = await fetch(API_URL + '/rooms/edit/' + id + '/' + name, { 
            method: 'POST',
            credentials: 'same-origin'
        })
        return await response.status;
    }

    async delete(id) {
        const response = await fetch(API_URL + '/rooms/' + id, { 
            method: 'DELETE',
            credentials: 'same-origin'
        })
        return await response.status
    }

}

export const services = {
    login: new LoginService(),
    plugins: new PluginService(),
    system: new SystemService(),
    clients: new ClientService(),
    rooms: new RoomService()
}
