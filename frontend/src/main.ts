import { createApp } from 'vue'
import { createPinia } from 'pinia'
import {
  create,
  NButton,
  NCard,
  NConfigProvider,
  NDataTable,
  NDatePicker,
  NDrawer,
  NDrawerContent,
  NEmpty,
  NForm,
  NFormItem,
  NGrid,
  NGridItem,
  NInput,
  NInputNumber,
  NLayout,
  NLayoutContent,
  NLayoutHeader,
  NLayoutSider,
  NMenu,
  NMessageProvider,
  NModal,
  NPopconfirm,
  NProgress,
  NSelect,
  NSpace,
  NSpin,
  NStatistic,
  NTag,
  darkTheme
} from 'naive-ui'
import App from './App.vue'
import { router } from './router'
import './style.css'

const naive = create({
  components: [
    NButton,
    NCard,
    NConfigProvider,
    NDataTable,
    NDatePicker,
    NDrawer,
    NDrawerContent,
    NEmpty,
    NForm,
    NFormItem,
    NGrid,
    NGridItem,
    NInput,
    NInputNumber,
    NLayout,
    NLayoutContent,
    NLayoutHeader,
    NLayoutSider,
    NMenu,
    NMessageProvider,
    NModal,
    NPopconfirm,
    NProgress,
    NSelect,
    NSpace,
    NSpin,
    NStatistic,
    NTag
  ]
})

createApp(App)
  .use(createPinia())
  .use(router)
  .use(naive)
  .provide('naiveDarkTheme', darkTheme)
  .mount('#app')
