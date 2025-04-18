import axios from 'axios';

const backendURL = process.env.REACT_APP_API_URL || "http://localhost:8080"; 
console.log(backendURL)
const customAxios = axios.create({
  baseURL: backendURL,
  timeout: 10000
});

export default customAxios;

export const processResponse = (request) => {
    return new Promise((resolve, reject) => {
        request.then(response => {
            if(response.data.statusCode === 200){
                resolve(response.data);
            }else{
                throw new Error(JSON.stringify(response.data))
            }
        }).catch(error => {
            reject(error)
        })
    })
}