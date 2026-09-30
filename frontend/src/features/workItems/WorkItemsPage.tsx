// Main work items page: status overview tiles (persisted in the URL), list, and detail panel.
import { useSearchParams } from 'react-router-dom'
import { useGetWorkItemsQuery } from '../../api/workItemsApi'
import WorkItemList from './WorkItemList'
import WorkItemDetail from './WorkItemDetail'
import StatusSummary from './StatusSummary'
import SimulateCrmForm from './SimulateCrmForm'
import './workItems.css'

export default function WorkItemsPage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const status = searchParams.get('status') ?? 'ALL'
  const selectedId = searchParams.get('selected')

  const { data, isLoading } = useGetWorkItemsQuery({
    status: status === 'ALL' ? undefined : status,
  })

  const handleStatusChange = (nextStatus: string) => {
    const next = new URLSearchParams(searchParams)
    if (nextStatus === 'ALL') {
      next.delete('status')
    } else {
      next.set('status', nextStatus)
    }
    next.delete('selected')
    setSearchParams(next)
  }

  const handleSelect = (id: string) => {
    const next = new URLSearchParams(searchParams)
    next.set('selected', id)
    setSearchParams(next)
  }

  return (
    <div className="work-items-page">
      <SimulateCrmForm />

      <StatusSummary status={status} onChange={handleStatusChange} />

      <div className="list-header">
        <h2>Work items</h2>
        {!isLoading && data && (
          <span className="list-count">
            {data.count} {data.count === 1 ? 'item' : 'items'}
          </span>
        )}
      </div>

      <div className="work-items-layout">
        <WorkItemList
          items={data?.results ?? []}
          isLoading={isLoading}
          selectedId={selectedId}
          onSelect={handleSelect}
        />
        {selectedId && (
          <div className="detail-column">
            <WorkItemDetail id={selectedId} />
          </div>
        )}
      </div>
    </div>
  )
}
