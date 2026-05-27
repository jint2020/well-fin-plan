<script setup lang="ts">
import { reactive } from 'vue'
import { useRouter } from 'vue-router'
import { api, setToken } from '../api/client'

const router = useRouter()
const form = reactive({ email: 'alice@example.com', password: 'SecurePass123!', display_name: 'Alice' })

async function register() {
  const result = await api<{ access_token: string }>('/auth/register', {
    method: 'POST',
    body: JSON.stringify(form)
  })
  setToken(result.access_token)
  router.push('/')
}

async function login() {
  const result = await api<{ access_token: string }>('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email: form.email, password: form.password })
  })
  setToken(result.access_token)
  router.push('/')
}
</script>

<template>
  <section class="panel narrow">
    <h2>登录</h2>
    <el-form label-position="top">
      <el-form-item label="邮箱"><el-input v-model="form.email" /></el-form-item>
      <el-form-item label="密码"><el-input v-model="form.password" type="password" /></el-form-item>
      <el-form-item label="昵称"><el-input v-model="form.display_name" /></el-form-item>
      <div class="actions">
        <el-button type="primary" @click="login">登录</el-button>
        <el-button @click="register">注册</el-button>
      </div>
    </el-form>
  </section>
</template>
