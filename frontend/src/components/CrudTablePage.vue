<script setup lang="ts">
import type { DataTableColumns, FormInst } from 'naive-ui'
import { computed, ref } from 'vue'
import { h } from 'vue'
import { NPopconfirm, useMessage } from 'naive-ui'
import DataPanel from './DataPanel.vue'
import PageHeader from './PageHeader.vue'
import { compactPayload } from '../utils/format'

type Row = Record<string, unknown> & { id: string }
type Field = {
  key: string
  label: string
  type?: 'text' | 'number' | 'select' | 'date'
  options?: { label: string; value: string }[]
  placeholder?: string
}

const props = defineProps<{
  eyebrow?: string
  title: string
  description: string
  rows: Record<string, unknown>[]
  columns: DataTableColumns<Record<string, unknown>>
  fields: Field[]
  defaults: Record<string, unknown>
  loading?: boolean
  createText?: string
  onCreate: (payload: Record<string, unknown>) => Promise<unknown>
  onUpdate: (id: string, payload: Record<string, unknown>) => Promise<unknown>
  onDelete: (id: string) => Promise<void>
}>()

const emit = defineEmits<{ refresh: [] }>()
const message = useMessage()
const formRef = ref<FormInst | null>(null)
const drawerVisible = ref(false)
const editingId = ref<string | null>(null)
const submitting = ref(false)
const form = ref<Record<string, unknown>>({ ...props.defaults })

const modeTitle = computed(() => (editingId.value ? `编辑${props.title}` : props.createText || `新增${props.title}`))
const tableColumns = computed<DataTableColumns<Record<string, unknown>>>(() => [
  ...props.columns,
  {
    title: '操作',
    key: 'actions',
    width: 150,
    render(row) {
      return [
        hButton('编辑', () => openEdit(row as Row)),
        hDelete(row as Row)
      ]
    }
  }
])

function openCreate() {
  editingId.value = null
  form.value = { ...props.defaults }
  drawerVisible.value = true
}

function openEdit(row: Row) {
  editingId.value = row.id
  form.value = { ...props.defaults, ...row }
  drawerVisible.value = true
}

async function submit() {
  submitting.value = true
  try {
    const payload = compactPayload({ ...form.value })
    delete payload.id
    if (editingId.value) {
      await props.onUpdate(editingId.value, payload)
    } else {
      await props.onCreate(payload)
    }
    drawerVisible.value = false
    emit('refresh')
    message.success('已保存')
  } catch (error) {
    message.error(error instanceof Error ? error.message : '保存失败')
  } finally {
    submitting.value = false
  }
}

async function remove(row: Row) {
  try {
    await props.onDelete(row.id)
    emit('refresh')
    message.success('已删除')
  } catch (error) {
    message.error(error instanceof Error ? error.message : '删除失败')
  }
}

function hButton(label: string, onClick: () => void) {
  return h(
    'button',
    {
      class: 'link-button',
      onClick
    },
    label
  )
}

function hDelete(row: Row) {
  return h(
    NPopconfirm,
    {
      onPositiveClick: () => remove(row)
    },
    {
      trigger: () => h('button', { class: 'link-button link-button--danger' }, '删除'),
      default: () => `确认删除这条${props.title}记录？`
    }
  )
}
</script>

<template>
  <PageHeader :eyebrow="eyebrow" :title="title" :description="description">
    <template #actions>
      <slot name="filters" />
      <n-button type="primary" @click="openCreate">{{ createText || `新增${title}` }}</n-button>
    </template>
  </PageHeader>

  <DataPanel>
    <n-data-table
      :columns="tableColumns"
      :data="rows"
      :loading="loading"
      :bordered="false"
      :pagination="{ pageSize: 12 }"
      size="small"
    />
  </DataPanel>

  <n-drawer v-model:show="drawerVisible" :width="460" placement="right">
    <n-drawer-content :title="modeTitle">
      <n-form ref="formRef" label-placement="top">
        <n-form-item v-for="field in fields" :key="field.key" :label="field.label">
          <n-select v-if="field.type === 'select'" v-model:value="form[field.key]" :options="field.options || []" filterable />
          <n-input-number
            v-else-if="field.type === 'number'"
            v-model:value="form[field.key]"
            :show-button="false"
            class="full-control"
          />
          <n-date-picker
            v-else-if="field.type === 'date'"
            v-model:formatted-value="form[field.key]"
            value-format="yyyy-MM-dd"
            type="date"
            class="full-control"
          />
          <n-input v-else v-model:value="form[field.key]" :placeholder="field.placeholder" />
        </n-form-item>
      </n-form>
      <template #footer>
        <n-space justify="end">
          <n-button @click="drawerVisible = false">取消</n-button>
          <n-button type="primary" :loading="submitting" @click="submit">保存</n-button>
        </n-space>
      </template>
    </n-drawer-content>
  </n-drawer>
</template>
