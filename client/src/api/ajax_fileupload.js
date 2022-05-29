// ajax file upload module

import axios from "axios"

export default function ajax_fileupload(url = "", params = {}) {
    let promise;
    let config = {
        headers: {
            "Content-Type": "multipart/form-data",
            "token": localStorage.getItem("token")
        }
    }
    return new Promise((resolve, reject) => {
        promise = axios.post(url, params, config);
        promise.then((res) => {
            resolve(res.data);
        }).catch((err) => {
            reject(err);
        })
    })
}
