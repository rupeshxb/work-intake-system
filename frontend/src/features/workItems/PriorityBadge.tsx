// Small colored badge representing an analysis result's priority.
const PRIORITY_CLASS: Record<string, string> = {
  LOW: 'priority-badge priority-low',
  MEDIUM: 'priority-badge priority-medium',
  HIGH: 'priority-badge priority-high',
  URGENT: 'priority-badge priority-urgent',
}

export default function PriorityBadge({ priority }: { priority: string }) {
  return (
    <span className={PRIORITY_CLASS[priority] ?? 'priority-badge'}>
      {priority.charAt(0) + priority.slice(1).toLowerCase()}
    </span>
  )
}
