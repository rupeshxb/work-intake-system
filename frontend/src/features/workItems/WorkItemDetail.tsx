// Detail panel for the selected work item: metadata, analysis, failure reason, and attempt history.
import { useGetWorkItemQuery } from '../../api/workItemsApi'
import ActionBar from './ActionBar'
import StatusBadge from './StatusBadge'
import PriorityBadge from './PriorityBadge'

function formatDate(iso: string) {
  return new Date(iso).toLocaleString()
}

export default function WorkItemDetail({ id }: { id: string }) {
  const { data: item, isLoading, isError } = useGetWorkItemQuery(id)

  if (isLoading) {
    return (
      <div className="detail-panel">
        <div className="detail-skeleton" />
      </div>
    )
  }

  if (isError || !item) {
    return <div className="detail-panel error-banner">Could not load this work item.</div>
  }

  return (
    <div className={`detail-panel status-accent-${item.status.toLowerCase()}`}>
      <ActionBar workItem={item} />

      <div className="detail-header">
        <div>
          <p className="detail-external-id">{item.externalId}</p>
          <h2>{item.title}</h2>
        </div>
        <StatusBadge status={item.status} />
      </div>
      <p className="detail-description">{item.description}</p>

      <div className="detail-meta">
        <span>Created {formatDate(item.createdAt)}</span>
        <span>Updated {formatDate(item.updatedAt)}</span>
      </div>

      {item.analysis && (
        <div className="analysis-card">
          <div className="analysis-card-header">
            <h3>Analysis</h3>
            <PriorityBadge priority={item.analysis.priority} />
          </div>
          <p className="analysis-category">{item.analysis.category.replaceAll('_', ' ')}</p>
          <p className="analysis-summary">{item.analysis.summary}</p>
          <div className="analysis-recommendation">
            <span className="analysis-recommendation-label">Recommended action</span>
            <p>{item.analysis.recommendedAction}</p>
          </div>
        </div>
      )}

      {item.failureReason && (
        <div className="error-banner">
          <strong>Failure reason:</strong> {item.failureReason}
        </div>
      )}

      <div className="attempts-section">
        <h3>Attempts</h3>
        {item.attempts.length === 0 ? (
          <p className="empty-state empty-state-inline">No analysis attempts yet.</p>
        ) : (
          <table className="attempts-table">
            <thead>
              <tr>
                <th>#</th>
                <th>Status</th>
                <th>Error</th>
                <th>Latency</th>
                <th>Timestamp</th>
              </tr>
            </thead>
            <tbody>
              {item.attempts.map((attempt) => (
                <tr key={attempt.attempt_number}>
                  <td>{attempt.attempt_number}</td>
                  <td>
                    <span className={`attempt-status attempt-${attempt.status.toLowerCase()}`}>
                      {attempt.status}
                    </span>
                  </td>
                  <td className="attempt-error">{attempt.error ?? '—'}</td>
                  <td>{attempt.latency_ms !== null ? `${attempt.latency_ms} ms` : '—'}</td>
                  <td>{formatDate(attempt.created_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
