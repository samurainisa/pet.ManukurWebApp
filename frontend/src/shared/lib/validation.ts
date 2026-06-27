const PHONE_REGEX = /^\+?[0-9()\-\s]{7,20}$/
const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

export function normalizeSpaces(value: string) {
  return value.trim().replace(/\s+/g, ' ')
}

export function toNullableText(value: string) {
  const normalized = value.trim()
  return normalized.length > 0 ? normalized : null
}

export function validateRequiredText(value: string, label: string, minLength = 1) {
  const normalized = normalizeSpaces(value)
  if (!normalized) {
    return `${label} обязательно для заполнения.`
  }
  if (normalized.length < minLength) {
    return `${label} должно содержать минимум ${minLength} символа.`
  }
  return null
}

export function validatePhone(value: string) {
  const normalized = normalizeSpaces(value)
  if (!normalized) {
    return 'Телефон обязателен для заполнения.'
  }
  if (!PHONE_REGEX.test(normalized)) {
    return 'Укажите корректный телефон.'
  }

  const digits = normalized.replace(/\D/g, '')
  if (digits.length < 7) {
    return 'Телефон должен содержать минимум 7 цифр.'
  }

  return null
}

export function validateOptionalEmail(value: string) {
  const normalized = value.trim()
  if (!normalized) {
    return null
  }
  if (!EMAIL_REGEX.test(normalized)) {
    return 'Укажите корректный email.'
  }
  return null
}

export function validateDateRange(dateFrom: string, dateTo: string) {
  if (!dateFrom || !dateTo) {
    return 'Укажите период: дату начала и дату окончания.'
  }

  const from = new Date(`${dateFrom}T00:00:00`)
  const to = new Date(`${dateTo}T00:00:00`)
  if (Number.isNaN(from.getTime()) || Number.isNaN(to.getTime())) {
    return 'Укажите корректные даты периода.'
  }

  if (from > to) {
    return 'Дата начала периода не может быть позже даты окончания.'
  }

  return null
}

export function validatePositiveNumber(value: number, label: string, min = 0) {
  if (!Number.isFinite(value)) {
    return `${label} должно быть числом.`
  }
  if (value < min) {
    return `${label} не может быть меньше ${min}.`
  }
  return null
}
