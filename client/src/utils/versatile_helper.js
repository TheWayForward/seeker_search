import Config from "./config";
import lodash from "lodash";

function get_array_element_by_id(array, id) {
    if (!array.length) {
        return {
            is_empty: true,
            element: {}
        }
    } else {
        for (let i = 0; i < array.length; i++) {
            if (array[i].id == id) {
                return {
                    is_empty: false,
                    found: true,
                    element: array[i]
                }
            }
        }
        return {
            is_empty: false,
            found: false
        }
    }
}

function delete_array_element_by_id(array, id) {
    if (!array.length) {
        return {
            is_empty: true,
            element: {}
        }
    } else {
        for (let i = 0; i < array.length; i++) {
            if (array[i].id == id) {
                return {
                    is_empty: false,
                    found: true,
                    element: array.splice(i, 1)
                }
            }
        }
        return {
            is_empty: false,
            found: false
        }
    }
}

function distribution_triple(array) {
    let array_1 = [], array_2 = [], array_3 = [];
    for (let i = 0; i < array.length; i++) {
        if (i % 3 == 0) array_1.push(array[i]);
        else if ((i - 1) % 3 == 0) array_2.push(array[i]);
        else array_3.push(array[i]);
    }
    return {
        array_1,
        array_2,
        array_3
    }
}

function parse_url(url) {
    if (url.substr(0, 7) === "http://" || url.substr(0, 8) === "https://") return url;
    return `${Config.BASE_URL}${url}`;
}

function redo_url(url) {
    if (url.substr(0, 7) === "http://" || url.substr(0, 8) === "https://") {
        return url.substr(Config.BASE_URL.length);
    }
    return url;
}

function generate_address_string(address) {
    let address_string = address.province;
    if (address.hasOwnProperty("region")) {
        address_string += ` ${address.region}`;
    }
    if (address.hasOwnProperty("district")) {
        address_string += ` ${address.district}`;
    }
    let address_detail_string = address_string + ` ${address.detail}`;
    return {
        address_string: address_string,
        address_detail_string: address_detail_string
    };
}

function copy_content(content) {
    let temp = document.createElement('input');
    temp.setAttribute('value', content);
    document.body.appendChild(temp);
    temp.select();
    let result = document.execCommand('copy');
    document.body.removeChild(temp);
    return result;
}

function byteToSize(byte) {
    return byte / (1024 * 1024);
}

function listToTree(list) {
    const map = {};
    const tree = [];
    list.forEach((item) => {
        item.label = item.name;
        map[item.id] = item;
    });
    list.forEach((item) => {
        const parent = map[item.parent_id];
        if (parent) {
            (parent.children || (parent.children = [])).push(item);
        } else {
            tree.push(item);
        }
    });
    return tree;
}

let clone_object = function (obj = {}) {
    // if (typeof obj !== "object" || obj == null) {
    //     return obj;
    // }
    // let result;
    // if (obj instanceof Array) {
    //     result = [];
    // } else {
    //     result = {};
    // }
    // for (let key in obj) {
    //     if (obj.hasOwnProperty(key)) {
    //         result[key] = clone_object(obj[key]);
    //     }
    // }
    // return result;
    return lodash.cloneDeep(obj);
}

let object_equal = (obj_1, obj_2) => lodash.isEqual(obj_1, obj_2);

export default {
    MB: 1048576,
    get_array_element_by_id,
    delete_array_element_by_id,
    distribution_triple,
    parse_url,
    redo_url,
    generate_address_string,
    copy_content,
    byteToSize,
    listToTree,
    clone_object,
    object_equal
}