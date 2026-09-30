// RTK Query API slice for the work items backend: list, detail, analyse, retry, and complete.
import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react'

export type WorkItemStatus =
  | 'RECEIVED'
  | 'ANALYSING'
  | 'READY_FOR_REVIEW'
  | 'COMPLETED'
  | 'FAILED'

export type AllowedAction = 'analyse' | 'retry' | 'complete'

export interface Analysis {
  category: string
  priority: string
  summary: string
  recommendedAction: string
}

export interface AnalysisAttempt {
  attempt_number: number
  status: 'SUCCESS' | 'FAILED'
  error: string | null
  latency_ms: number | null
  created_at: string
}

export interface WorkItem {
  id: string
  externalId: string
  title: string
  description: string
  status: WorkItemStatus
  analysis: Analysis | null
  failureReason: string | null
  allowedActions: AllowedAction[]
  attempts: AnalysisAttempt[]
  createdAt: string
  updatedAt: string
}

export interface WorkItemListResponse {
  count: number
  next: string | null
  previous: string | null
  results: WorkItem[]
}

export interface GetWorkItemsArgs {
  status?: string
  page?: number
}

export interface CreateWorkItemArgs {
  externalId: string
  title: string
  description: string
}

export interface CreateWorkItemResult extends WorkItem {
  httpStatus: number
}

export const workItemsApi = createApi({
  reducerPath: 'workItemsApi',
  baseQuery: fetchBaseQuery({ baseUrl: import.meta.env.VITE_API_BASE_URL }),
  tagTypes: ['WorkItem'],
  endpoints: (builder) => ({
    getWorkItems: builder.query<WorkItemListResponse, GetWorkItemsArgs | void>({
      query: (args) => {
        const params = new URLSearchParams()
        if (args?.status && args.status !== 'ALL') params.set('status', args.status)
        if (args?.page) params.set('page', String(args.page))
        const qs = params.toString()
        return `work-items/${qs ? `?${qs}` : ''}`
      },
      providesTags: (result) =>
        result
          ? [
              ...result.results.map(({ id }) => ({ type: 'WorkItem' as const, id })),
              { type: 'WorkItem' as const, id: 'LIST' },
            ]
          : [{ type: 'WorkItem' as const, id: 'LIST' }],
    }),
    getWorkItem: builder.query<WorkItem, string>({
      query: (id) => `work-items/${id}/`,
      providesTags: (_result, _error, id) => [{ type: 'WorkItem', id }],
    }),
    analyseWorkItem: builder.mutation<WorkItem, string>({
      query: (id) => ({ url: `work-items/${id}/analyse/`, method: 'POST' }),
      invalidatesTags: (_result, _error, id) => [
        { type: 'WorkItem', id },
        { type: 'WorkItem', id: 'LIST' },
      ],
    }),
    retryWorkItem: builder.mutation<WorkItem, string>({
      query: (id) => ({ url: `work-items/${id}/retry/`, method: 'POST' }),
      invalidatesTags: (_result, _error, id) => [
        { type: 'WorkItem', id },
        { type: 'WorkItem', id: 'LIST' },
      ],
    }),
    createWorkItem: builder.mutation<CreateWorkItemResult, CreateWorkItemArgs>({
      query: (body) => ({ url: 'work-items/', method: 'POST', body }),
      transformResponse: (response: WorkItem, meta) => ({
        ...response,
        httpStatus: meta?.response?.status ?? 0,
      }),
      invalidatesTags: [{ type: 'WorkItem', id: 'LIST' }],
    }),
    completeWorkItem: builder.mutation<WorkItem, string>({
      query: (id) => ({
        url: `work-items/${id}/status/`,
        method: 'PATCH',
        body: { status: 'COMPLETED' },
      }),
      invalidatesTags: (_result, _error, id) => [
        { type: 'WorkItem', id },
        { type: 'WorkItem', id: 'LIST' },
      ],
    }),
  }),
})

export const {
  useGetWorkItemsQuery,
  useGetWorkItemQuery,
  useCreateWorkItemMutation,
  useAnalyseWorkItemMutation,
  useRetryWorkItemMutation,
  useCompleteWorkItemMutation,
} = workItemsApi
