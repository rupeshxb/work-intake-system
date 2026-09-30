// Tests for ActionBar's action buttons, driven purely by allowedActions — mocks the API hooks, no network calls.
import { render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import ActionBar from './ActionBar'
import type { WorkItem } from '../../api/workItemsApi'

const mockTrigger = vi.fn()

vi.mock('../../api/workItemsApi', () => ({
  useAnalyseWorkItemMutation: () => [mockTrigger, { isLoading: false }],
  useRetryWorkItemMutation: () => [mockTrigger, { isLoading: false }],
  useCompleteWorkItemMutation: () => [mockTrigger, { isLoading: false }],
}))

function makeWorkItem(allowedActions: WorkItem['allowedActions']): WorkItem {
  return {
    id: '1',
    externalId: 'EXT-1',
    title: 'Title',
    description: 'Description',
    status: 'RECEIVED',
    analysis: null,
    failureReason: null,
    allowedActions,
    attempts: [],
    createdAt: '2024-01-01T00:00:00Z',
    updatedAt: '2024-01-01T00:00:00Z',
  }
}

describe('ActionBar', () => {
  it('renders Analyse button when allowedActions contains "analyse"', () => {
    render(<ActionBar workItem={makeWorkItem(['analyse'])} />)
    expect(screen.getByRole('button', { name: /analyse/i })).toBeInTheDocument()
  })

  it('renders Complete button when allowedActions contains "complete"', () => {
    render(<ActionBar workItem={makeWorkItem(['complete'])} />)
    expect(screen.getByRole('button', { name: /complete/i })).toBeInTheDocument()
  })

  it('renders no buttons when allowedActions is empty', () => {
    render(<ActionBar workItem={makeWorkItem([])} />)
    expect(screen.queryByRole('button')).not.toBeInTheDocument()
  })
})
