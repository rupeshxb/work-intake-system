// Small colored badge representing a work item's status.
import type { WorkItemStatus } from '../../api/workItemsApi'

const STATUS_CLASS: Record<WorkItemStatus, string> = {
  RECEIVED: 'status-badge status-received',
  ANALYSING: 'status-badge status-analysing',
  READY_FOR_REVIEW: 'status-badge status-ready',
  COMPLETED: 'status-badge status-completed',
  FAILED: 'status-badge status-failed',
}

const STATUS_LABEL: Record<WorkItemStatus, string> = {
  RECEIVED: 'Received',
  ANALYSING: 'Analysing',
  READY_FOR_REVIEW: 'Ready for review',
  COMPLETED: 'Completed',
  FAILED: 'Failed',
}

export default function StatusBadge({ status }: { status: WorkItemStatus }) {
  return <span className={STATUS_CLASS[status]}>{STATUS_LABEL[status]}</span>
}
