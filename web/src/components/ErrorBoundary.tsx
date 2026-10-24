import { Component, type ErrorInfo, type ReactNode } from "react";

interface Props {
  children: ReactNode;
}

interface State {
  error: Error | null;
}

export default class ErrorBoundary extends Component<Props, State> {
  state: State = { error: null };

  static getDerivedStateFromError(error: Error): State {
    return { error };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    try {
      fetch("/api/client-error", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          page: window.location.href,
          message: error.message,
          stack: error.stack,
          component: info.componentStack,
        }),
        keepalive: true,
      });
    } catch {
      /* best effort */
    }
  }

  render() {
    if (this.state.error) {
      return (
        <div className="page">
          <header className="topbar">
            <h1>DocAssay</h1>
          </header>
          <section className="panel">
            <div className="error">Render error: {this.state.error.message}</div>
            <pre className="muted small">{this.state.error.stack}</pre>
          </section>
        </div>
      );
    }
    return this.props.children;
  }
}