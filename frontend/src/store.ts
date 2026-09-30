import { configureStore } from '@reduxjs/toolkit'
import { workItemsApi } from './api/workItemsApi'

export const store = configureStore({
  reducer: {
    [workItemsApi.reducerPath]: workItemsApi.reducer,
  },
  middleware: (getDefaultMiddleware) => getDefaultMiddleware().concat(workItemsApi.middleware),
})

export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch
