import axios, { processResponse } from './helpers';


export const GetChapters = (title) => {
    const request = axios.get('/chapters',{ 
        params: { title: title } })
    return processResponse(request);
}

export const GetCBZFile = (payload) => {
    const request = axios.post('/download', payload, {
        responseType: 'blob'
      })
    return processResponse(request)
}