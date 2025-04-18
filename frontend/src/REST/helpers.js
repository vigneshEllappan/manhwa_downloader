import axios from 'axios';

const backendURL = process.env.REACT_APP_API_URL || "http://localhost:8080"; 
const customAxios = axios.create({
  baseURL: backendURL
});

export default customAxios;

export const processResponse = (request) => {
    return new Promise((resolve, reject) => {
        request.then(response => {
            if(response.data.statusCode === 200){
                if(response.data.file){
                    const base64File = response.data.file;
          
                    // Convert the base64 string to a Blob
                    const byteCharacters = atob(base64File);
                    const byteArrays = [];

                    for (let offset = 0; offset < byteCharacters.length; offset += 1024) {
                        const slice = byteCharacters.slice(offset, offset + 1024);
                        const byteNumbers = new Array(slice.length);
                        for (let i = 0; i < slice.length; i++) {
                        byteNumbers[i] = slice.charCodeAt(i);
                        }
                        byteArrays.push(new Uint8Array(byteNumbers));
                    }

                    const blob = new Blob(byteArrays, { type: 'application/zip' });
                    resolve(blob);  // Returning the Blob (CBZ file)
                }else if(response.data.data){
                    resolve(response.data.data);
                }
        } else {
          reject(new Error('Failed with status code: ' + response.data));
        }       
        }).catch(error => {
            reject(error)
        })
    })
}