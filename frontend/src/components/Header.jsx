export default function Header({ fileName, onUpload }) {
  return (
    <header className="app-header">
      <div className="brand">
        <span className="brand-mark">§</span>
        <span className="brand-name">Docket</span>
      </div>
      <div className="doc-name">{fileName || 'No document loaded'}</div>
      <label className="upload-btn">
        Upload contract
        <input
          type="file"
          accept=".txt,.pdf,.docx"
          onChange={onUpload}
          hidden
        />
      </label>
    </header>
  );
}
