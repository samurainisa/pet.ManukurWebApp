const FIELD_LABELS: Record<string, string> = {
  non_field_errors: 'Ошибка',
  detail: 'Ошибка',
  username: 'Логин',
  password: 'Пароль',
  password_confirm: 'Подтверждение пароля',
  first_name: 'Имя',
  last_name: 'Фамилия',
  full_name: 'ФИО',
  phone: 'Телефон',
  email: 'Email',
  notes: 'Заметка',
  client: 'Клиент',
  service: 'Услуга',
  name: 'Название',
  base_duration_min: 'Длительность',
  base_price: 'Цена',
  sort_order: 'Порядок',
  date: 'Дата',
  time: 'Время',
  start_datetime: 'Начало записи',
  end_datetime: 'Окончание записи',
  planned_duration_min: 'Плановая длительность',
  planned_price: 'Плановая цена',
  actual_duration_min: 'Фактическая длительность',
  payment_method: 'Способ оплаты',
  payment_status: 'Статус оплаты',
  amount: 'Сумма',
  reason: 'Причина',
  service_id: 'Услуга',
}

function prettifyFieldName(field: string): string {
  return FIELD_LABELS[field] ?? field.replaceAll('_', ' ')
}

function flattenErrors(value: unknown, prefix = ''): string[] {
  if (typeof value === 'string') {
    return [prefix ? `${prefix}: ${value}` : value]
  }

  if (Array.isArray(value)) {
    return value.flatMap((item) => flattenErrors(item, prefix))
  }

  if (value && typeof value === 'object') {
    const record = value as Record<string, unknown>
    if (typeof record.detail === 'string') {
      return [record.detail]
    }

    return Object.entries(record).flatMap(([key, nested]) => {
      const fieldName = prettifyFieldName(key)
      const nextPrefix =
        key === 'non_field_errors' || key === 'detail'
          ? prefix
          : prefix
            ? `${prefix}: ${fieldName}`
            : fieldName
      return flattenErrors(nested, nextPrefix)
    })
  }

  return []
}

export function getBackendErrorMessage(data: unknown, fallback = 'Ошибка запроса к API'): string {
  const messages = flattenErrors(data)
  return messages.length > 0 ? messages.join('\n') : fallback
}
