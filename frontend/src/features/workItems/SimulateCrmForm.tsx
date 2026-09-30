// Demo-only form that mimics an external CRM POSTing a new work item straight to the intake API.
import { useState, type FormEvent } from 'react'
import { useCreateWorkItemMutation } from '../../api/workItemsApi'
import { extractErrorMessage } from '../../api/errors'

export default function SimulateCrmForm() {
  const [externalId, setExternalId] = useState('')
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [resultMessage, setResultMessage] = useState<string | null>(null)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const [createWorkItem, { isLoading }] = useCreateWorkItemMutation()

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault()
    setResultMessage(null)
    setErrorMessage(null)

    try {
      const result = await createWorkItem({ externalId, title, description }).unwrap()
      setResultMessage(
        result.httpStatus === 201
          ? `Created (201) — ${result.externalId}`
          : `Already existed (200) — ${result.externalId}`,
      )
      setExternalId('')
      setTitle('')
      setDescription('')
      setTimeout(() => setResultMessage(null), 4000)
    } catch (error) {
      setErrorMessage(extractErrorMessage(error))
    }
  }

  return (
    <details className="crm-simulator">
      <summary>Simulate CRM Submission (for demo purposes)</summary>
      <div className="crm-simulator-body">
        <p className="crm-simulator-note">
          This mimics an external CRM calling the intake API directly — not part of the normal
          operations workflow.
        </p>
        <form onSubmit={handleSubmit} className="crm-simulator-form">
          <label>
            External ID
            <input
              type="text"
              value={externalId}
              onChange={(event) => setExternalId(event.target.value)}
              required
            />
          </label>
          <label>
            Title
            <input
              type="text"
              value={title}
              onChange={(event) => setTitle(event.target.value)}
              required
            />
          </label>
          <label>
            Description
            <textarea
              value={description}
              onChange={(event) => setDescription(event.target.value)}
              required
            />
          </label>
          <button type="submit" className="btn btn-crm" disabled={isLoading}>
            {isLoading && <span className="spinner" aria-hidden="true" />}
            Submit
          </button>
        </form>
        {resultMessage && <div className="crm-simulator-result">{resultMessage}</div>}
        {errorMessage && (
          <div className="error-banner" role="alert">
            {errorMessage}
          </div>
        )}
      </div>
    </details>
  )
}
