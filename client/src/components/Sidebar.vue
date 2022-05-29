<template>
    <div class="sidebar">
        <el-menu class="sidebar-el-menu" :default-active="onRoutes" :collapse="collapse" background-color="#324157"
                 text-color="#bfcbd9" active-text-color="#20a0ff" unique-opened router>
            <template v-for="item in items">
                <template v-if="item.subs">
                    <el-submenu :index="item.index" :key="item.index">
                        <template #title>
                            <i :class="item.icon"></i>
                            <span>{{ item.title }}</span>
                        </template>
                        <template v-for="subItem in item.subs">
                            <el-submenu v-if="subItem.subs" :index="subItem.index" :key="subItem.index">
                                <template #title>{{ subItem.title }}</template>
                                <el-menu-item v-for="(threeItem, i) in subItem.subs" :key="i" :index="threeItem.index">
                                    {{ threeItem.title }}
                                </el-menu-item>
                            </el-submenu>
                            <el-menu-item v-else :index="subItem.index" :key="subItem.index">{{ subItem.title }}
                            </el-menu-item>
                        </template>
                    </el-submenu>
                </template>
                <template v-else>
                    <el-menu-item :index="item.index" :key="item.index">
                        <i :class="item.icon"></i>
                        <template #title>{{ item.title }}</template>
                    </el-menu-item>
                </template>
            </template>
        </el-menu>
    </div>
</template>

<script>
    import {computed, watch} from "vue";
    import {useStore} from "vuex";
    import {useRoute} from "vue-router";

    export default {
        setup() {
            const items = [
                {
                    icon: "el-icon-lx-home",
                    index: "/dashboard",
                    title: "首页",
                },
                {
                    icon: "el-icon-document",
                    index: "1",
                    title: "内容管理",
                    subs: [
                        {
                            index: "/wechatminiprogram_content_management",
                            title: "微信小程序",
                        }
                    ]
                },
                {
                    icon: "el-icon-s-grid",
                    index: "/product_management",
                    title: "商品管理",
                },
                {
                    icon: "el-icon-files",
                    index: "2",
                    title: "订单管理",
                    subs: [
                        {
                            index: "/order_unpaid",
                            title: "待支付"
                        },
                        {
                            index: "/order_paid",
                            title: "待发货"
                        },
                        {
                            index: "/order_sent",
                            title: "已发货"
                        },
                        {
                            index: "/order_completed",
                            title: "已完成"
                        },
                        {
                            index: "/order_closed",
                            title: "已关闭"
                        },
                        {
                            index: "/order_management",
                            title: "订单查询"
                        }
                    ]
                }
            ];

            const route = useRoute();

            const onRoutes = computed(() => {
                return route.path;
            });

            const store = useStore();
            const collapse = computed(() => store.state.collapse);

            return {
                items,
                onRoutes,
                collapse,
            };
        },
    };
</script>

<style scoped>
    .sidebar {
        display: block;
        position: absolute;
        left: 0;
        top: 70px;
        bottom: 0;
        overflow-y: scroll;
    }

    .sidebar::-webkit-scrollbar {
        width: 0;
    }

    .sidebar-el-menu:not(.el-menu--collapse) {
        width: 250px;
    }

    .sidebar > ul {
        height: 100%;
    }
</style>
