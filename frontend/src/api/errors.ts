// Extracts a human-readable message from an RTK Query error, reading the API's {error, detail} body shape.
interface ApiErrorBody {
  detail?: string
  error?: string
}

export function extractErrorMessage(error: unknown): string {
  if (error && typeof error === 'object' && 'data' in error) {
    const data = (error as { data?: ApiErrorBody }).data
    if (data?.detail) return data.detail
    if (data?.error) return data.error
  }
  if (error && typeof error === 'object' && 'error' in error) {
    const message = (error as { error?: unknown }).error
    if (typeof message === 'string') return message
  }
  return 'Something went wrong. Please try again.'
}
