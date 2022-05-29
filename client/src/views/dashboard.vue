<template>
    <div>
        <el-row :gutter="20">
            <el-col :span="8">

                <!-- search input card -->
                <el-card shadow="hover" class="mgb20">
                    <div>
                        <el-image :src="staticImage.logo_full"></el-image>
                    </div>
                    <el-row :gutter="20" style="margin-top: 20px;">
                        <el-col :span="18">
                            <el-autocomplete
                                    style="width: 100%;"
                                    v-model="searchInput"
                                    :fetch-suggestions="getSearchSuggestion"
                                    :debounce="500"
                                    clearable
                                    placeholder="请输入关键词"
                            />
                        </el-col>
                        <el-col :span="6">
                            <!-- search button -->
                            <el-button style="width: 100%;" type="primary" @click="search">搜索</el-button>
                        </el-col>
                    </el-row>
                </el-card>

                <!-- history card -->
                <el-card shadow="hover" style="height: 505px;" v-loading="seekerDataTabLoading">
                    <div class="card-header">
                        <span style="font-weight: bold;">Seeker Data</span>
                        <el-button class="button" type="text">
                            <i class="el-icon-lx-refresh hover-rotate" style="font-size: 20px;"/>
                        </el-button>
                    </div>
                    <el-tabs v-model="activeName" class="demo-tabs" @tab-click="handleSeekerDataTabClick">
                        <!-- sum data chart -->
                        <el-tab-pane label="搜索记录" name="first" lazy>
                            <el-scrollbar height="350px" style="margin-top: 20px; margin-bottom: 20px;">
                                <el-card v-for="item in searchHistory" shadow="hover" style="margin-bottom: 10px;">
                                    <p class="search-history" @click="searchFromHistory({key_words: item.key_words})">{{item.key_words}}</p>
                                    <el-tag style="margin-top: 20px;">{{item.time}}</el-tag>
                                </el-card>
                            </el-scrollbar>
                        </el-tab-pane>
                    </el-tabs>
                </el-card>
            </el-col>

            <el-col :span="16">

                <!-- search result card -->
                <el-card shadow="hover" style="height: 750px; position: relative;" v-loading="searchResultTabLoading">
                    <div class="card-header" v-if="searchResult.total_result">
                        <div>
                            <p style="font-weight: bold;">{{searchResult.key_words}}</p>
                            <div style="display: flex; margin-top: 20px;">
                                <el-tag>Seeker Search为您找到相关结果{{searchResult.total_result}}个</el-tag>
                                <el-tag type="info" style="margin-left: 20px;">用时{{searchResult.duration}}秒</el-tag>
                            </div>
                        </div>
                    </div>
                    <!-- display when no result presented -->
                    <el-empty v-if="!searchResult.total_result"
                              style="position: absolute; top: 0; bottom: 0; left: 0; right: 0; margin: auto;"
                              :image="staticImage.logo_full" :description="emptyHint"/>

                    <el-scrollbar height="540px" style="margin-top: 20px; margin-bottom: 20px;">
                        <el-card style="margin-bottom: 10px;" v-for="item in searchResult.search_data" shadow="hover">
                            <a :href="item.url" target="_blank" v-html="item.title"
                               style="font-size: 18px; line-height: 22px; text-decoration: underline;"></a>
                            <p v-html="item.content" style="font-size: 13px; line-height: 21px; margin-top: 10px;"></p>
                            <el-tag size="small" style="margin-top: 10px;">关联度：{{item.score.toFixed(2)}}</el-tag>
                        </el-card>
                    </el-scrollbar>
                    <div class="handle-row" v-if="searchResult.total_result">
                        <el-pagination
                                background
                                style="margin-top: 20px;"
                                :page-size="searchResult.page_size"
                                layout="total, prev, pager, next"
                                :total="searchResult.total_result"
                                @current-change="handleSearchResultPaginationCurrentClick"
                        />
                    </div>
                </el-card>
            </el-col>
        </el-row>
    </div>
</template>

<script>
    import Schart from "vue-schart";
    import {Line} from '@antv/g2plot';
    import {reactive, ref} from "vue";
    import {getSearchResult, getSuggestion} from "../api/index";
    import TimeHelper from "../utils/time_helper";
    import Config from "../utils/config";
    import VersatileHelper from "../utils/versatile_helper";
    import logo_full from "../../src/assets/img/logo_full.png";

    export default {
        name: "dashboard",
        data() {
            return {
                lineChartObject: null,
                activeName: ref("first"),
                message: ref("first"),
                seekerDataTabLoading: false,
                searchInput: "",
                emptyHint: "键入内容以搜索",
                searchResultTabLoading: false,
                searchHistory: [],
                searchResult: {
                    duration: 0,
                    key_words: "",
                    page_size: 0,
                    page_index: 1,
                    total_result: 0,
                    total_pages: 0,
                    search_data: {}
                },

                TimeHelper,
                staticImage: {
                    logo_full: logo_full
                }
            }
        },

        components: {Schart},

        watch: {
            searchResult() {
                if (this.searchResult.key_words === "" && this.searchInput === "") {
                    this.emptyHint = "键入以搜索";
                } else if (this.searchResult.key_words !== "" && !this.searchResult.total_result) {
                    this.emptyHint = "暂无数据"
                }
            }
        },

        methods: {
            async getSearchSuggestion(queryString, cb) {
                if (this.searchInput === "") return;
                let result = await getSuggestion(this.searchInput);
                if (result.code === 200) {
                    let data = result.info.suggest_data;
                    let searchSuggestion = [];
                    for (let i = 0; i < data.length; i++) {
                        searchSuggestion.push({value: data[i]});
                    }
                    cb(searchSuggestion);
                } else {
                    ElMessage.warning(result.message);
                }
            },

            async search() {
                if (this.searchInput === "") return;
                this.searchResultTabLoading = true;
                if (this.searchResult.page_index === 1) {
                    this.saveSearchToLocalStorage(this.searchInput);
                    this.searchHistory = this.getSearchHistoryFromLocalStorage();
                }
                let result = await getSearchResult(this.searchInput, this.searchResult.page_index);
                if (result.code === 200) {
                    let data = result.info;
                    this.searchResult.duration = data.duration;
                    this.searchResult.key_words = data.key_words;
                    this.searchResult.page_index = data.page_index;
                    this.searchResult.page_size = data.page_size;
                    this.searchResult.total_result = data.total_result;
                    this.searchResult.total_pages = data.total_pages;
                    this.searchResult.search_data = data.search_data;
                    console.log(this.searchResult.search_data);
                    this.searchResultTabLoading = false;
                    this.$forceUpdate();
                } else {
                    ElMessage.warning(result.message);
                }
            },

            handleSeekerDataTabClick() {

            },

            searchFromHistory(e) {
                this.searchInput = e.key_words;
                this.search();
            },

            initSearchHistory() {
                let searchHistory = this.getSearchHistoryFromLocalStorage();
                if (!searchHistory) {
                    localStorage.setItem("search_history", JSON.stringify([]));
                    this.searchHistory = [];
                    return;
                }
                this.searchHistory = searchHistory;
            },

            getSearchHistoryFromLocalStorage() {
                console.log(JSON.parse(localStorage.getItem("search_history")));
                return JSON.parse(localStorage.getItem("search_history"));
            },

            saveSearchToLocalStorage(key_words) {
                let searchHistory = this.getSearchHistoryFromLocalStorage();
                while (searchHistory.length > 100) {
                    searchHistory.shift();
                }
                searchHistory.push({
                    key_words: key_words,
                    time: TimeHelper.convert_date_to_date_time_string(new Date())
                });
                searchHistory.sort(function(a, b) { return b.time > a.time ? 1 : -1; });
                localStorage.setItem("search_history", JSON.stringify(searchHistory));
            },

            async handleSearchResultPaginationCurrentClick(current) {
                this.searchResult.page_index = parseInt(current);
                await this.search();
            }
        },

        created() {
            this.initSearchHistory();
            this.getSearchHistoryFromLocalStorage();
        },

        mounted() {
            history.pushState(null, null, document.URL);
            window.addEventListener("popstate", function (e) {
                history.pushState(null, null, document.URL);
            }, false);
        }
    };
</script>

<style scoped>


    .el-row {
        margin-bottom: 20px;
    }

    .grid-content {
        display: flex;
        align-items: center;
        height: 100px;
    }

    .grid-cont-right {
        flex: 1;
        text-align: center;
        font-size: 14px;
        color: #999;
    }

    .grid-num {
        font-size: 30px;
        font-weight: bold;
    }

    .grid-con-icon {
        font-size: 50px;
        width: 100px;
        height: 100px;
        text-align: center;
        line-height: 100px;
        color: #fff;
    }

    .grid-con-1 .grid-con-icon {
        background: rgb(45, 140, 240);
    }

    .grid-con-1 .grid-num {
        color: rgb(45, 140, 240);
    }

    .grid-con-2 .grid-con-icon {
        background: rgb(100, 213, 114);
    }

    .grid-con-2 .grid-num {
        color: rgb(45, 140, 240);
    }

    .grid-con-3 .grid-con-icon {
        background: rgb(242, 94, 67);
    }

    .grid-con-3 .grid-num {
        color: rgb(242, 94, 67);
    }

    .user-info {
        display: flex;
        align-items: center;
    }

    .user-avatar {
        width: 120px;
        height: 120px;
        border-radius: 50%;
    }

    .user-info-cont {
        padding-left: 50px;
        flex: 1;
        font-size: 14px;
        color: #999;
    }

    .user-info-cont div:first-child {
        font-size: 30px;
        color: #222;
    }

    .user-info-list {
        font-size: 14px;
        color: #999;
        line-height: 25px;
    }

    .user-info-list span {
        margin-left: 70px;
    }

    .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .mgb20 {
        margin-bottom: 20px;
    }

    .scrollbar-demo-item {
        display: flex;
        align-items: center;
        justify-content: center;
        height: 50px;
        margin: 10px;
        text-align: center;
        border-radius: 4px;
        background: gainsboro;
        color: gray;
    }

    .search-history:hover {
        cursor: pointer;
    }
</style>
