// Tests for WorkItemList's loading, empty, and populated states — pure props, no network calls.
import { render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import WorkItemList from './WorkItemList'
import type { WorkItem } from '../../api/workItemsApi'

function makeItem(overrides: Partial<WorkItem> = {}): WorkItem {
  return {
    id: '1',
    externalId: 'EXT-1',
    title: 'Missing payslip',
    description: 'Description',
    status: 'RECEIVED',
    analysis: null,
    failureReason: null,
    allowedActions: ['analyse'],
    attempts: [],
    createdAt: '2024-01-01T00:00:00Z',
    updatedAt: '2024-01-01T00:00:00Z',
    ...overrides,
  }
}

describe('WorkItemList', () => {
  it('renders a loading state', () => {
    const { container } = render(
      <WorkItemList items={[]} isLoading selectedId={null} onSelect={vi.fn()} />,
    )
    expect(container.querySelector('[aria-busy="true"]')).toBeInTheDocument()
  })

  it('renders an empty state when results are empty', () => {
    render(<WorkItemList items={[]} isLoading={false} selectedId={null} onSelect={vi.fn()} />)
    expect(screen.getByText(/no work items found/i)).toBeInTheDocument()
  })

  it('renders item rows when results exist', () => {
    render(
      <WorkItemList items={[makeItem()]} isLoading={false} selectedId={null} onSelect={vi.fn()} />,
    )
    expect(screen.getByText('EXT-1')).toBeInTheDocument()
    expect(screen.getByText('Missing payslip')).toBeInTheDocument()
  })
})
