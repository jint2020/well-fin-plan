import type { DecimalValue } from '../types/finance'

export function numberValue(value: DecimalValue | null | undefined): number {
  if (value === null || value === undefined || value === '') return 0
  const parsed = Number(value)
  return Number.isFinite(parsed) ? parsed : 0
}

export function money(value: DecimalValue | null | undefined): string {
  return new Intl.NumberFormat('zh-CN', {
    style: 'currency',
    currency: 'CNY',
    maximumFractionDigits: 0
  }).format(numberValue(value))
}

export function percent(value: DecimalValue | null | undefined, digits = 1): string {
  return `${(numberValue(value) * 100).toFixed(digits)}%`
}

export function currentMonth(): string {
  const now = new Date()
  return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`
}

export function monthDate(month: string): string {
  return `${month}-01`
}

export function compactPayload<T extends Record<string, unknown>>(payload: T): Partial<T> {
  return Object.fromEntries(
    Object.entries(payload).filter(([, value]) => value !== '' && value !== undefined)
  ) as Partial<T>
}
