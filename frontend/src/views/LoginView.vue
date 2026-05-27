<script setup lang="ts">
import { Landmark } from 'lucide-vue-next'
import { reactive, ref } from 'vue'
import { useMessage } from 'naive-ui'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const message = useMessage()
const auth = useAuthStore()
const isRegister = ref(false)
const submitting = ref(false)
const form = reactive({
  email: 'alice@example.com',
  password: 'SecurePass123!',
  displayName: 'Alice'
})

async function submit() {
  submitting.value = true
  try {
    if (isRegister.value) {
      await auth.register(form.email, form.password, form.displayName)
    } else {
      await auth.login(form.email, form.password)
    }
    router.push('/')
  } catch (error) {
    message.error(error instanceof Error ? error.message : '认证失败')
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <main class="login-page">
    <section class="login-panel">
      <div class="login-brand">
        <span><Landmark :size="26" /></span>
        <div>
          <strong>Well Fin Plan</strong>
          <small>个人资金管理后台</small>
        </div>
      </div>
      <h1>{{ isRegister ? '创建账户' : '欢迎回来' }}</h1>
      <p>以现金流为起点，把应急金、债务、投资和资产配置放在同一个工作台。</p>

      <n-form label-placement="top" class="login-form" @submit.prevent="submit">
        <n-form-item label="邮箱">
          <n-input v-model:value="form.email" />
        </n-form-item>
        <n-form-item label="密码">
          <n-input v-model:value="form.password" type="password" show-password-on="click" />
        </n-form-item>
        <n-form-item v-if="isRegister" label="昵称">
          <n-input v-model:value="form.displayName" />
        </n-form-item>
        <n-space>
          <n-button type="primary" attr-type="submit" :loading="submitting">
            {{ isRegister ? '注册并进入' : '登录' }}
          </n-button>
          <n-button quaternary @click="isRegister = !isRegister">
            {{ isRegister ? '已有账户' : '创建账户' }}
          </n-button>
        </n-space>
      </n-form>
    </section>
  </main>
</template>
