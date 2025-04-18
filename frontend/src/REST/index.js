import axios, { processResponse } from './helpers';


export const GetChapters = (title) => {
    const request = axios.get('/chapters',{ 
        params: { title: title } })
    return processResponse(request);
}