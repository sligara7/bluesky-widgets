import React from 'react';

interface RunViewerProps {
  uid: string;
  documents: any[];
}

const RunViewer: React.FC<RunViewerProps> = ({ uid, documents }) => {
  return (
    <div className="run-viewer">
      <h3>Run: {uid}</h3>
      <div className="run-docs">
        {documents.map((doc, i) => (
          <details key={i}>
            <summary>{doc.name || doc.type || doc["uid"]}</summary>
            <pre style={{ maxHeight: '240px', overflow: 'auto' }}>{JSON.stringify(doc, null, 2)}</pre>
          </details>
        ))}
      </div>
      <div>
        <a
          href={`data:application/json;charset=utf-8,${encodeURIComponent(JSON.stringify({ uid, documents }, null, 2))}`}
          download={`run-${uid}.json`}
        >
          Download JSON
        </a>
      </div>
    </div>
  );
};

export default RunViewer;
