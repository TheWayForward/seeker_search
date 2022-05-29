let ONE_DAY = 86400000;

const format_number = function (n) {
    n = n.toString();
    return n[1] ? n : "0" + n;
}

export default {
    days_user_created_till_now: function (user_info) {
        let d = new Date(user_info.date_created);
        let d_now = new Date();
        return Math.floor((d_now - d) / ONE_DAY) + 1;
    },

    convert_date_to_date_string: function (date) {
        return `${date.getFullYear()}-${format_number(date.getMonth() + 1)}-${format_number(date.getDate())}`;
    },

    convert_date_to_short_date_string: function(date) {
        return `${format_number(date.getMonth() + 1)}-${format_number(date.getDate())}`;
    },

    convert_date_to_time_string: function (date) {
        return `${format_number(date.getHours())}:${format_number(date.getMinutes())}:${format_number(date.getSeconds())}`;
    },

    convert_date_to_date_time_string: function (date) {
        return `${this.convert_date_to_date_string(date)} ${this.convert_date_to_time_string(date)}`;
    },

    generate_week_string_array: function () {
        let now = new Date();
        let week_string_array = [];
        for (let i = 0; i < 7; i++) {
            week_string_array.unshift({
                timestamp: this.convert_date_to_short_date_string(new Date(now.getTime() - i * ONE_DAY)),
                value: 0,
                payment: 0
            });
        }
        return week_string_array;
    }
};
