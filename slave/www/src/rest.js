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

export class ConfigService {

    async getConfigValue(name) {
        const response = await fetch(API_URL + '/config/' + name, {
            method: 'GET',
            credentials: 'same-origin'
        })
        return await response.json()
    }

    async setConfigValue(name, value) {
        const response = await fetch(API_URL + '/config/' + name , {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'same-origin',
            body: JSON.stringify({value: value})
        })
        return await response
    }

}

export class ModelService {
    
    async getModels() {
        const response = await fetch(API_URL + '/models', {
            method: 'GET',
            credentials: 'same-origin'
        })
        return await response.json()
    }

    async uploadModel(file) {
        const form = new FormData();
        form.append('file', file, file.name);
        const response = await fetch(API_URL + '/model/upload', {
            method: 'POST',
            credentials: 'same-origin',
            body: form
        })
        return response;
    }

    async deleteModel(filename) {
        const response = await fetch(API_URL + '/model/' + filename, {
            method: 'DELETE',
            credentials: 'same-origin'
        })
        return response
    }

    async getScorers() {
        const response = await fetch(API_URL + '/scorers', {
            method: 'GET',
            credentials: 'same-origin'
        })
        return await response.json()
    }

    async uploadScorer(file) {
        const form = new FormData();
        form.append('file', file, file.name);
        const response = await fetch(API_URL + '/scorer/upload', {
            method: 'POST',
            credentials: 'same-origin',
            body: form
        })
        return response;
    }

    async deleteScorer(filename) {
        const response = await fetch(API_URL + '/scorer/' + filename, {
            method: 'DELETE',
            credentials: 'same-origin'
        })
        return response
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

    async connect(url, password) {
        const response = await fetch(API_URL + '/connect', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'same-origin',
            body: JSON.stringify({ password: password, api_url: url})
        })
        return await response.json();
    }

    async isConnected() {
        const response = await fetch(API_URL + '/is_connected', {
            method: 'GET',
            credentials: 'same-origin'
        })
        return await response.json();
    }

}




export const services = {
    login: new LoginService(),
    system: new SystemService(),
    config: new ConfigService(),
    models: new ModelService()
}
