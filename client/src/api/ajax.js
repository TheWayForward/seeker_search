// ajax request module

import axios from "axios"

export default function ajax({url, headers = {
    "token": localStorage.getItem("token") === null ? "" : localStorage.getItem("token"),
}, params, method="GET"}) {
    let promise;
    return new Promise((resolve, reject) => {
        if (method === "GET") {
            // GET request
            // generate query string from params
            let query_string = "";
            Object.keys(params).forEach(key => {
                query_string += key + "=" + params[key] + "&";
            });
            // find out the last &
            if (query_string !== "") {
                query_string = query_string.substr(0, query_string.lastIndexOf("&"));
            }
            // generate full URL from query string and params
            url += "?" + query_string;
            console.log(url);
            promise = axios.get(url, {headers: headers});
        } else if (method === "POST") {
            promise = axios.post(url, params, {headers: headers});
        }
        promise.then((res) => {
            resolve(res.data);
        }).catch((err) => {
            reject(err);
        })
    })
}
