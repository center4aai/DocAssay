import { useEffect, useState } from "react";
import Home from "./pages/Home";
import RepoView from "./pages/RepoView";

function parseHash(): string {
  const m = window.location.hash.match(/^#\/repo\/(.+)$/);
  return m ? decodeURIComponent(m[1]) : "";
}

export default function App() {
  const [repoId, setRepoId] = useState<string>(() => parseHash());

  useEffect(() => {
    const onChange = () => setRepoId(parseHash());
    window.addEventListener("hashchange", onChange);
    return () => window.removeEventListener("hashchange", onChange);
  }, []);

  if (repoId) {
    return (
      <RepoView
        repoId={repoId}
        onBack={() => {
          window.location.hash = "#/";
        }}
      />
    );
  }
  return <Home />;
}