import axios from 'axios';

const backendURL = process.env.REACT_APP_API_URL || "http://localhost:8080/api"; 
const customAxios = axios.create({
  baseURL: backendURL
});

export default customAxios;

export const processResponse = (request) => {
    return new Promise((resolve, reject) => {
        request.then(response => {
            resolve(response.data);    
        }).catch(error => {
            reject(error)
        })
    })
}