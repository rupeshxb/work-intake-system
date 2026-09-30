import WorkItemsPage from './features/workItems/WorkItemsPage'
import './App.css'

function App() {
  return (
    <div className="app">
      <header className="app-header">
        <span className="app-logo">W</span>
        <div className="app-header-text">
          <h1>Work Intake</h1>
          <p>Triage and track incoming work items</p>
        </div>
      </header>
      <main className="app-main">
        <WorkItemsPage />
      </main>
    </div>
  )
}

export default App
