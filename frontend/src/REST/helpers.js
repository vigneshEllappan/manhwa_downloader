import axios from 'axios';

const customAxios = axios.create({
  baseURL: 'http://127.0.0.1:5000', // fallback for dev
  timeout: 5000
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