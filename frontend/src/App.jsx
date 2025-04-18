import { useState } from 'react';
import './App.css';

function App() {
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [msg, setMsg] = useState("");

  const download = async () => {
    setLoading(true);
    setMsg("");

    const cbz = `chapter_${Date.now()}.cbz`;
    const folder = `chapter_${Date.now()}`;

    const res = await fetch("/download", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url, cbz, folder })
    });

    const result = await res.json();
    setLoading(false);
    setMsg(result.status === "success" ? `✅ Downloaded: ${result.cbz}` : "❌ Failed");
  };

  return (
    <div className="App">
      <h1>Manhwa Downloader</h1>
      <input value={url} onChange={e => setUrl(e.target.value)} placeholder="Paste chapter URL" />
      <button onClick={download} disabled={loading}>
        {loading ? "Downloading..." : "Download"}
      </button>
      <p>{msg}</p>
    </div>
  );
}

export default App;
