// user
function username_verification(username) {
    if (username.length < 4) {
        if (!username) {
            return {
                has_error: true,
                detail: "昵称不能为空"
            }
        }
        return {
            has_error: true,
            detail: "用户名过短"
        }
    } else if (username.length > 20) {
        return {
            has_error: true,
            detail: "用户名过长"
        }
    } else {
        if (/^[0-9a-zA-Z_]{1,}$/.test(username)) {
            return {
                has_error: false,
            }
        } else {
            return {
                has_error: true,
                detail: "用户名包含非法字符"
            }
        }
    }
}

function nickname_verification(nickname) {
    if (nickname.length < 6) {
        if (!nickname) {
            return {
                has_error: true,
                detail: "昵称不能为空"
            }
        }
        return {
            has_error: true,
            detail: "昵称过短"
        }
    } else if (nickname.length > 20) {
        return {
            has_error: true,
            detail: "昵称过长"
        }
    } else {
        // has proper length
        if (/^[0-9a-zA-Z_\u4E00-\u9FA5\\s]{1,}$/.test(nickname)) {
            return {
                has_error: false,
                detail: "昵称可用"
            }
        } else {
            return {
                has_error: true,
                detail: "昵称包含非法字符"
            }
        }
    }
}

function realname_verification(realname) {
    if (realname === "") {
        return {
            has_error: true,
            detail: "真实姓名不能为空"
        }
    }
    if (/^[\u4E00-\u9FA5]{2,10}(·[\u4E00-\u9FA5]{2,10}){0,2}$/.test(realname)) {
        return {
            has_error: false,
            detail: "真实姓名可用"
        }
    } else {
        return {
            has_error: true,
            detail: "真实姓名包含非法字符"
        }
    }
}

function password_verification(password) {
    if (!password) {
        return {
            has_error: true,
            detail: "密码不能为空"
        }
    }
    if (password.length < 4) {
        return {
            has_error: true,
            detail: "密码过短"
        }
    } else if (password.length > 20) {
        return {
            has_error: true,
            detail: "密码过长"
        }
    } else {
        if (/^[0-9a-zA-Z_]{1,}$/.test(password)) {
            return {
                has_error: false,
            }
        } else {
            return {
                has_error: true,
                detail: "密码包含非法字符"
            }
        }
    }
}

function password_strength_verification(password) {
    let s = Number(/\s+/g.test(password));
    // has number
    let n = Number(/\d+/g.test(password));
    // has letter
    let l = Number(/[a-zA-Z]+/g.test(password));
    // has dash
    let d = Number(/[_]+/g.test(password));
    return s ? 0 : n + l + d;
}

function QQ_verification(QQ) {
    if (!QQ) {
        return {
            has_error: true,
            detail: "QQ号码不能为空"
        }
    }
    if (QQ.length < 6 || QQ.length > 11) {
        return {
            has_error: true,
            detail: "QQ号码长度错误"
        }
    } else {
        if (/[1-9][0-9]{4,14}/.test(QQ)) {
            return {
                has_error: false
            }
        } else {
            return {
                has_error: true,
                detail: "QQ号码格式错误"
            }
        }
    }
}

function tel_verification(tel) {
    if (!tel) {
        return {
            has_error: true,
            detail: "手机号不能为空"
        }
    }
    if (/^[1][3,4,5,7,8][0-9]{9}$/.test(tel)) {
        return {
            has_error: false
        };
    } else {
        return {
            has_error: true,
            detail: "手机号格式错误"
        };
    }
}

function email_verification(email) {
    if (!email) {
        return {
            has_error: true,
            detail: "email不能为空"
        }
    }
    if (/[\w]+(\.[\w]+)*@[\w]+(\.[\w])+/.test(email)) {
        return {
            has_error: false
        }
    } else {
        return {
            has_error: true,
            detail: "email格式错误"
        }
    }
}

function user_order_serial_verification(serial) {
    if (!serial) {
        return {
            has_error: true,
            detail: "订单号不能为空！"
        };
    }
    if (/^[1][0-9]{18}$/.test(serial)) {
        return {
            has_error: false
        };
    } else {
        return {
            has_error: true,
            detail: "订单号格式错误"
        };
    }
}

function address_verification(address) {
    if (!address) {
        return {
            has_error: true,
            detail: "住址不能为空"
        }
    } else {
        return {
            has_error: false
        }
    }
}

function empty_verification(obj) {
    for (let obj_attribute in obj) {
        if (obj[obj_attribute]) return false;
    }
    return true;
}

function ute_judgement(ute) {
    let result = {type: "username"};
    let t_verification = tel_verification(ute);
    let e_verification = email_verification(ute);
    if (!t_verification.has_error) {
        result.type = "tel";
        return result;
    } else if (!e_verification.has_error) {
        result.type = "email";
        return result;
    } else {
        return result;
    }
}

// commodity
function commodity_name_verification(name) {
    if (!name) {
        return {
            has_error: true,
            detail: "物品名称不能为空"
        }
    } else {
        if (/^[0-9a-zA-Z_\u4E00-\u9FA5\\s]{1,}$/.test(name)) {
            return {
                has_error: false
            }
        } else {
            return {
                has_error: true,
                detail: "物品名称格式有误"
            }
        }

    }
}

function commodity_detail_verification(detail) {
    if (!detail) {
        return {
            has_error: true,
            detail: "物品详情不能为空"
        }
    } else {
        if (detail.length < 100) {
            return {
                has_error: true,
                detail: `物品详情须在100字以上（当前字数：${detail.length}）`
            }
        } else {
            return {
                has_error: false
            }
        }
    }
}

function commodity_state_verification(commodity) {
    let state = commodity.state;
    switch (state) {
        case 0: {
            // initial upload, pending censorship
            return {
                name: "审核中",
                value: 0,
                class: "badge-secondary",
                is_editable: false,
                is_tradable: false,
            }
        }
        case 1: {
            // has passed sensorship
            return {
                name: "审核通过",
                value: 1,
                class: "badge-success",
                is_editable: true,
                is_tradable: true
            }
        }
        case 2: {
            // has been asked by another user
            return {
                name: "交易中",
                value: 2,
                class: "badge-warning",
                is_editable: false,
                is_tradable: false
            }
        }
        case 5: {
            return {
                name: "审核不通过",
                value: 5,
                class: "badge-danger",
                is_editable: true,
                is_tradable: false
            }
        }
    }
}

// transaction

function transaction_state_verification(transaction) {
    let state = transaction.state;
    switch (state) {
        case 0: {
            return {
                name: "进行中",
                value: 0,
                class: "badge-warning",
            }
        }
        case 1: {
            return {
                name: "已成交",
                value: 1,
                class: "badge-success",
            }
        }
        case 2: {
            return {
                name: "已关闭",
                value: 2,
                class: "badge-secondary"
            }
        }
        case 3: {
            return {
                name: "进行中（需求）",
                value: 3,
                class: "badge-info"
            }
        }
    }
}

// censorship

function censorship_type_verification(censorship) {
    let type = censorship.type;
    switch (type) {
        case 1: {
            return {
                name: "通过",
                value: 1,
                class: "badge-success"
            }
        }
        case 0: {
            return {
                name: "驳回",
                value: 0,
                class: "badge-danger"
            }
        }
    }
}

// requirement

function requirement_state_verification(requirement) {
    let state = requirement.state;
    switch (state) {
        case 0: {
            return {
                name: "待解决",
                class: "badge-secondary",
                value: 0
            }
        }
        case 1: {
            return {
                name: "已解决",
                class: "badge-success",
                value: 1
            }
        }
    }
}

function requirement_detail_verification(detail) {
    if (!detail) {
        return {
            has_error: true,
            detail: "物品详情不能为空"
        }
    } else {
        if (detail.length < 20) {
            return {
                has_error: true,
                detail: `需求描述须在20字以上（当前字数：${detail.length}）`
            }
        } else {
            return {
                has_error: false
            }
        }
    }
}

// url
function url_verification(url) {
    if (!url) {
        return {
            has_error: true,
            detail: "url不能为空"
        }
    } else {
        if (/([hH][tT]{2}[pP]:\/\/|[hH][tT]{2}[pP][sS]:\/\/|[wW]{3}.|[wW][aA][pP].|[fF][tT][pP].|[fF][iI][lL][eE].)[-A-Za-z0-9+&@#/%?=~_|!:,.;]+[-A-Za-z0-9+&@#/%=~_|]/.test(url)) {
            return {
                has_error: false
            }
        } else {
            return {
                has_error: true,
                detail: "url格式有误"
            }
        }
    }
}

function contains_space(s) {
    return !/^[^\s]*$/.test(s);
}

function price_verification(price) {
    if (Number(price) === 0) return false;
    return /(^[1-9]\d*(\.\d{1,2})?$)|(^0(\.\d{1,2})?$)/.test(price);
}

function quantity_verification(quantity) {
    return /^[1-9]\d*$/.test(quantity);
}

export default {
    username_verification,
    nickname_verification,
    realname_verification,
    password_verification,
    password_strength_verification,
    QQ_verification,
    tel_verification,
    email_verification,
    address_verification,
    user_order_serial_verification,
    empty_verification,
    ute_judgement,
    commodity_name_verification,
    commodity_state_verification,
    commodity_detail_verification,
    transaction_state_verification,
    censorship_type_verification,
    requirement_state_verification,
    requirement_detail_verification,
    url_verification,
    contains_space,
    price_verification,
    quantity_verification
}
