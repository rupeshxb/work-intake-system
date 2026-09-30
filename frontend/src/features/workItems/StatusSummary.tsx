// Clickable status overview tiles: one query per status, each tile filters the list and shows its count.
import { useGetWorkItemsQuery } from '../../api/workItemsApi'

const STATUS_TILES = [
  { value: 'RECEIVED', label: 'Received', className: 'tile-received' },
  { value: 'ANALYSING', label: 'Analysing', className: 'tile-analysing' },
  { value: 'READY_FOR_REVIEW', label: 'Ready for review', className: 'tile-ready' },
  { value: 'FAILED', label: 'Failed', className: 'tile-failed' },
  { value: 'COMPLETED', label: 'Completed', className: 'tile-completed' },
] as const

interface StatusSummaryProps {
  status: string
  onChange: (status: string) => void
}

function StatusCount({ status }: { status?: string }) {
  const { data } = useGetWorkItemsQuery({ status })
  return <span className="tile-count">{data ? data.count : '···'}</span>
}

export default function StatusSummary({ status, onChange }: StatusSummaryProps) {
  return (
    <div className="status-summary" role="tablist" aria-label="Filter by status">
      <button
        type="button"
        role="tab"
        aria-selected={status === 'ALL'}
        className={`status-tile tile-all ${status === 'ALL' ? 'active' : ''}`}
        onClick={() => onChange('ALL')}
      >
        <span className="tile-label">All items</span>
        <StatusCount />
      </button>

      {STATUS_TILES.map((tile) => (
        <button
          key={tile.value}
          type="button"
          role="tab"
          aria-selected={status === tile.value}
          className={`status-tile ${tile.className} ${status === tile.value ? 'active' : ''}`}
          onClick={() => onChange(tile.value)}
        >
          <span className="tile-label">{tile.label}</span>
          <StatusCount status={tile.value} />
        </button>
      ))}
    </div>
  )
}
