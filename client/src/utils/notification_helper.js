import {MessageBox,Loading} from "element-ui";
import time_helper from "@/common/js/utils/time_helper";

var loading;

function show_toast_success(content) {
    MessageBox({
        type: "success",
        message: content,
        showConfirmButton: false
    }).catch((err) => {
        console.log(err);
    })
}

function show_toast_info(content) {
    MessageBox({
        type: "info",
        message: content,
        showConfirmButton: false
    }).catch((err) => {
        console.log(err);
    })
}

function show_toast_warning(content) {
    MessageBox({
        type: "warning",
        message: content,
        showConfirmButton: false
    }).catch((err) => {
        console.log(err);
    })
}

function show_toast_error(content) {
    MessageBox({
        type: "error",
        message: content,
        showConfirmButton: false
    }).catch((err) => {
        console.log(err);
    })
}

function start_loading(content,target_id) {
    loading = Loading.service({
        lock: true,
        text: content,
        background: "rgba(0,0,0,0.7)",
        target: document.querySelector(`#${target_id}`)
    })
}

function stop_loading() {
    loading.close();
}

function user_greet(user_info) {
    // 0 for none, 1 for male, 2 for female
    let date = function () {
        let d = new Date();
        d = d.getHours();
        if (d > 21 || d <= 5) {
            return "晚安！熬夜有度，注意休息。";
        } else if (d > 5 && d <= 9) {
            return "早上好。";
        } else if (d > 9 && d <= 13) {
            return "中午好。"
        } else if (d > 13 && d <= 17) {
            return "下午好。"
        } else if (d > 17 && d <= 21) {
            return "晚上好。"
        }
    }
    let days_count = `这是您在"百川轩"的第${time_helper.days_user_created_till_now(user_info)}天。`;
    switch (user_info.gender) {
        case 0: {
            return  `${user_info.realname}同学，${date() + days_count}`;
        }
        case 1: {
            return `${user_info.realname[0]}先生，${date() + days_count}`;
        }
        case 2: {
            return `${user_info.realname[0]}女士，${date() + days_count}`;
        }
    }
}

export default {
    show_toast_success,
    show_toast_info,
    show_toast_warning,
    show_toast_error,
    start_loading,
    stop_loading,
    user_greet
}