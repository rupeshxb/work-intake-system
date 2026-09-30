// Action buttons (analyse/retry/complete) for the selected work item, driven by allowedActions.
import { useState } from 'react'
import {
  useAnalyseWorkItemMutation,
  useRetryWorkItemMutation,
  useCompleteWorkItemMutation,
  type WorkItem,
} from '../../api/workItemsApi'
import { extractErrorMessage } from '../../api/errors'

interface ActionBarProps {
  workItem: WorkItem
}

export default function ActionBar({ workItem }: ActionBarProps) {
  const [analyse, analyseState] = useAnalyseWorkItemMutation()
  const [retry, retryState] = useRetryWorkItemMutation()
  const [complete, completeState] = useCompleteWorkItemMutation()
  const [errorMessage, setErrorMessage] = useState<string | null>(null)

  const runAction = async (trigger: (id: string) => { unwrap: () => Promise<WorkItem> }) => {
    setErrorMessage(null)
    try {
      await trigger(workItem.id).unwrap()
    } catch (error) {
      setErrorMessage(extractErrorMessage(error))
    }
  }

  const anyLoading = analyseState.isLoading || retryState.isLoading || completeState.isLoading

  return (
    <div className="action-bar">
      <div className="action-bar-buttons">
        {workItem.allowedActions.includes('analyse') && (
          <button
            type="button"
            className="btn btn-analyse"
            disabled={anyLoading}
            onClick={() => runAction(analyse)}
          >
            {analyseState.isLoading && <span className="spinner" aria-hidden="true" />}
            Analyse
          </button>
        )}
        {workItem.allowedActions.includes('retry') && (
          <button
            type="button"
            className="btn btn-retry"
            disabled={anyLoading}
            onClick={() => runAction(retry)}
          >
            {retryState.isLoading && <span className="spinner" aria-hidden="true" />}
            Retry
          </button>
        )}
        {workItem.allowedActions.includes('complete') && (
          <button
            type="button"
            className="btn btn-complete"
            disabled={anyLoading}
            onClick={() => runAction(complete)}
          >
            {completeState.isLoading && <span className="spinner" aria-hidden="true" />}
            Complete
          </button>
        )}
      </div>
      {errorMessage && (
        <div className="error-banner" role="alert">
          {errorMessage}
        </div>
      )}
    </div>
  )
}
