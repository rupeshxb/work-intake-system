// Table of work items with a loading skeleton, empty state, and row selection.
import type { WorkItem } from '../../api/workItemsApi'
import StatusBadge from './StatusBadge'

interface WorkItemListProps {
  items: WorkItem[]
  isLoading: boolean
  selectedId: string | null
  onSelect: (id: string) => void
}

function formatDate(iso: string) {
  return new Date(iso).toLocaleString()
}

export default function WorkItemList({
  items,
  isLoading,
  selectedId,
  onSelect,
}: WorkItemListProps) {
  if (isLoading) {
    return (
      <div className="work-item-table" aria-busy="true">
        {Array.from({ length: 6 }).map((_, index) => (
          <div key={index} className="skeleton-row" />
        ))}
      </div>
    )
  }

  if (items.length === 0) {
    return <div className="empty-state">No work items found.</div>
  }

  return (
    <table className="work-item-table">
      <thead>
        <tr>
          <th>External ID</th>
          <th>Title</th>
          <th>Status</th>
          <th>Created</th>
        </tr>
      </thead>
      <tbody>
        {items.map((item) => (
          <tr
            key={item.id}
            className={item.id === selectedId ? 'selected' : ''}
            onClick={() => onSelect(item.id)}
          >
            <td>{item.externalId}</td>
            <td>{item.title}</td>
            <td>
              <StatusBadge status={item.status} />
            </td>
            <td>{formatDate(item.createdAt)}</td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}
