import request from '../utils/request';

import ajax from "../api/ajax";
import ajax_fileupload from "../api/ajax_fileupload";
import Config from "../utils/config";

const BASE_URL = Config.BASE_URL + "api/v1";

export const login = (username, password) => ajax({
    url: `${BASE_URL}/login`,
    params: {
        username: username,
        password: password
    },
    method: "POST"
});

export const getSuggestion = (key_words) => ajax({
    url: `${BASE_URL}/zhihu_suggest`,
    params: {
        key_words: key_words
    },
    method: "GET"
});

export const getSearchResult = (key_words, page_index) => ajax({
    url: `${BASE_URL}/zhihu_search_result`,
    params: {
        key_words: key_words,
        page_index: page_index
    },
    method: "GET"
});