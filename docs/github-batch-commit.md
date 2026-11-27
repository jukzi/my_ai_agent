# Mehrere Textdateien gemeinsam committen

`GitHub_CommitFiles` nutzt die vorhandene GitHub-Verbindung der App. Der Token bleibt in den Einstellungen und benötigt Schreibzugriff auf das Zielrepository.

```json
{
  "repo": "owner/repo",
  "branch": "feature/docs",
  "expected_head": "0123456789abcdef0123456789abcdef01234567",
  "message": "Dokumentation aktualisieren",
  "files": [
    {"path": "docs/guide.md", "workspace_path": "guide.md"},
    {"path": "docs/notes.md", "content": "# Notizen\n"}
  ]
}
```

`expected_head` ist die vollständige SHA des geprüften Branchstands, nicht der Name des Branches. Pro Datei ist entweder `content` oder `workspace_path` anzugeben. Ein Aufruf umfasst bis zu 100 Textdateien; Löschungen und Binärdateien sind nicht vorgesehen.

Das Werkzeug prüft den Branch vor und nach der Vorbereitung und aktualisiert ihn ohne Force. Hat sich der Branch bewegt, den neuen Stand und die Änderungen prüfen, statt den Auftrag blind mit einer anderen SHA zu wiederholen. Falls GitHub die Branch-Aktualisierung ablehnt, können der vorbereitete Baum und Commit bereits existieren, ohne dass der Zielbranch auf sie zeigt.
