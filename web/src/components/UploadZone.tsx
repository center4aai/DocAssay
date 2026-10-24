import { useRef, useState } from "react";
import { IconUpload } from "./icons";

interface Props {
  onUpload: (file: File) => void;
  disabled: boolean;
}

export default function UploadZone({ onUpload, disabled }: Props) {
  const [drag, setDrag] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handle = (file: File | undefined) => {
    if (file && !disabled) onUpload(file);
  };

  return (
    <div
      className={`upload-zone${drag ? " dragging" : ""}`}
      onClick={() => inputRef.current?.click()}
      onDragOver={(e) => {
        e.preventDefault();
        setDrag(true);
      }}
      onDragLeave={() => setDrag(false)}
      onDrop={(e) => {
        e.preventDefault();
        setDrag(false);
        handle(e.dataTransfer.files?.[0]);
      }}
    >
      <input
        ref={inputRef}
        type="file"
        accept=".zip"
        hidden
        onChange={(e) => handle(e.target.files?.[0])}
      />
      <span className="upload-icon">
        <IconUpload size={20} />
      </span>
      <strong>Drop a repository zip here</strong>
      <span className="muted small">or click to choose · analyzed with the full pipeline</span>
    </div>
  );
}