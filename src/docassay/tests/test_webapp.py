"""Tests for the web API (skipped when the ``[web]`` extra is not installed)."""

from __future__ import annotations

import io
import json
import os
import zipfile
from pathlib import Path

import pytest

fastapi = pytest.importorskip("fastapi")

from fastapi.testclient import TestClient  # noqa: E402

from docassay.webapp.server import RepoStore, create_app  # noqa: E402

_english = "# Demo project\nThis is the demo project that many teams use every day.\n"


def _client(tmp_path: Path, **app_kwargs) -> TestClient:
    app = create_app(
        workdir=tmp_path / "work",
        corpus_dir=tmp_path / "nonexistent-corpus",
        **app_kwargs,
    )
    # Every API request needs the session token; the test client sends it by
    # default (mirrors the injected frontend token).
    return TestClient(app, headers={"X-Session-Token": app.state.session_token})


def _mini_repo(root: Path) -> None:
    (root / "requirements.txt").write_text("requests==2.31.0\n")
    (root / "README.md").write_text(_english + "The project uses requests for the http client.\n")


def test_health(tmp_path: Path) -> None:
    client = _client(tmp_path)
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_health_probe_is_public(tmp_path: Path) -> None:
    # Container/orchestrator liveness probe: no session token required.
    app = create_app(workdir=tmp_path / "work", corpus_dir=tmp_path / "nonexistent-corpus")
    client = TestClient(app)
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}


def test_list_repos_empty(tmp_path: Path) -> None:
    client = _client(tmp_path)
    res = client.get("/api/repos")
    assert res.status_code == 200
    assert res.json()["repos"] == []


def test_analyze_path_and_bundle(tmp_path: Path) -> None:
    repo = tmp_path / "demo"
    repo.mkdir()
    _mini_repo(repo)
    client = _client(tmp_path)

    res = client.post("/api/repos/analyze", json={"path": str(repo)})
    assert res.status_code == 200
    repo_id = res.json()["id"]
    assert res.json()["meta"]["claims"] == 1

    bundle = client.get(f"/api/repos/{repo_id}/bundle").json()
    assert bundle["meta"]["repo"] == "demo"
    assert bundle["meta"]["verdicts"] == {"SUPPORTED": 1}
    claim = bundle["referents"][0]["assertions"][0]["claims"][0]
    assert claim["source"] == "README.md"
    assert claim["line_start"] == 3
    ev = bundle["evidence"]["requests:requirements.txt:==2.31.0"]
    assert ev["source_file"] == "requirements.txt"
    assert ev["line_start"] == 1

    repos = client.get("/api/repos").json()["repos"]
    assert [r["id"] for r in repos] == [repo_id]
    assert repos[0]["analyzed"] is True


def _sse_events(text: str) -> list[dict]:
    return [json.loads(line[6:]) for line in text.splitlines() if line.startswith("data: ")]


def test_analyze_stream_reports_progress(tmp_path: Path) -> None:
    repo = tmp_path / "demo"
    repo.mkdir()
    _mini_repo(repo)
    client = _client(tmp_path)

    res = client.post("/api/repos/analyze", json={"path": str(repo)}, params={"stream": "true"})
    assert res.status_code == 200
    events = _sse_events(res.text)
    progress = [e for e in events if e.get("kind")]
    done = [e for e in events if e.get("event") == "done"]
    assert progress, "expected pipeline progress frames"
    assert any("SYMBOL_EXISTS" in e["message"] for e in progress)
    assert any("adjudicat" in e["message"] for e in progress)
    timing = [e for e in progress if e["kind"] == "timing"]
    assert any(
        e["message"] == "analyze" and isinstance(e.get("duration_ms"), int) for e in timing
    ), "expected an analyze timing frame with an integer duration_ms"
    assert len(done) == 1
    assert done[0]["repo"]["meta"]["claims"] == 1


def test_bundle_stream_cache_hit_is_instant(tmp_path: Path) -> None:
    repo = tmp_path / "demo"
    repo.mkdir()
    _mini_repo(repo)
    client = _client(tmp_path)
    repo_id = client.post("/api/repos/analyze", json={"path": str(repo)}).json()["id"]

    res = client.get(f"/api/repos/{repo_id}/bundle/stream")
    assert res.status_code == 200
    events = _sse_events(res.text)
    assert all(e.get("event") == "done" for e in events)
    assert events[0]["bundle"]["meta"]["repo"] == "demo"


def test_log_persists_across_cache_hit(tmp_path: Path) -> None:
    repo = tmp_path / "demo"
    repo.mkdir()
    _mini_repo(repo)
    client = _client(tmp_path)
    repo_id = client.post("/api/repos/analyze", json={"path": str(repo)}).json()["id"]

    # A cached bundle streams no progress frames, but the completed run's log is
    # persisted and must still be retrievable (the "View logs" button).
    lines = client.get(f"/api/repos/{repo_id}/log").json()["lines"]
    assert lines, "expected a persisted analysis log"
    assert any("adjudicat" in line["message"] for line in lines)
    assert all("kind" in line and "message" in line for line in lines)
    assert any(line["kind"] == "step" for line in lines)
    assert any(
        line["kind"] == "timing"
        and line["message"] == "analyze"
        and isinstance(line.get("duration_ms"), int)
        for line in lines
    ), "expected the analyze timing frame to persist with the run log"


def test_file_endpoint_and_traversal(tmp_path: Path) -> None:
    repo = tmp_path / "demo"
    repo.mkdir()
    _mini_repo(repo)
    client = _client(tmp_path)
    repo_id = client.post("/api/repos/analyze", json={"path": str(repo)}).json()["id"]

    res = client.get(
        f"/api/repos/{repo_id}/file",
        params={"path": "README.md", "start": 3, "end": 3},
    )
    assert res.status_code == 200
    body = res.json()
    assert body["path"] == "README.md"
    assert [line["n"] for line in body["lines"]] == [3]
    assert "requests" in body["lines"][0]["text"]

    res = client.get(f"/api/repos/{repo_id}/file", params={"path": "../README.md"})
    assert res.status_code == 400

    res = client.get(f"/api/repos/{repo_id}/file", params={"path": "no/such/file.py"})
    assert res.status_code == 404


def test_export_markdown(tmp_path: Path) -> None:
    repo = tmp_path / "demo"
    repo.mkdir()
    _mini_repo(repo)
    client = _client(tmp_path)
    repo_id = client.post("/api/repos/analyze", json={"path": str(repo)}).json()["id"]
    res = client.get(f"/api/repos/{repo_id}/export.md")
    assert res.status_code == 200
    assert "## Assertions" in res.text


def test_upload_zip(tmp_path: Path) -> None:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("src/demo/", "")
        zf.writestr("demo/requirements.txt", "requests==2.31.0\n")
        zf.writestr(
            "demo/README.md",
            _english + "The project uses requests for the http client.\n",
        )
    buf.seek(0)
    client = _client(tmp_path)
    res = client.post("/api/repos/upload", files={"file": ("demo.zip", buf.getvalue())})
    assert res.status_code == 200
    body = res.json()
    assert body["kind"] == "upload"
    assert body["meta"]["claims"] == 1
    assert client.get(f"/api/repos/{body['id']}/bundle").status_code == 200


def test_upload_rejects_zip_slip(tmp_path: Path) -> None:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("../evil.txt", "boom")
    buf.seek(0)
    client = _client(tmp_path)
    res = client.post("/api/repos/upload", files={"file": ("evil.zip", buf.getvalue())})
    assert res.status_code == 400


def test_upload_rejects_invalid_zip(tmp_path: Path) -> None:
    client = _client(tmp_path)
    res = client.post("/api/repos/upload", files={"file": ("bad.zip", b"not a zip")})
    assert res.status_code == 400


def test_upload_skips_symlinks_and_macos_metadata(tmp_path: Path) -> None:
    # A zip of a macOS checkout that contains a virtualenv used to fail with
    # "symlinks are not allowed". Symlinks must be skipped, not materialized,
    # and Finder sidecars must not pollute the extracted tree.
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("README.md", _english + "The project uses requests for the http client.\n")
        zf.writestr("requirements.txt", "requests==2.31.0\n")
        link = zipfile.ZipInfo("python-link")
        link.external_attr = 0o120777 << 16
        zf.writestr(link, "/usr/bin/python3")
        zf.writestr("__MACOSX/._README.md", "junk")
        zf.writestr("._README.md", "junk")
        zf.writestr(".DS_Store", "junk")
    buf.seek(0)

    client = _client(tmp_path)
    res = client.post("/api/repos/upload", files={"file": ("demo.zip", buf.getvalue())})
    assert res.status_code == 200
    root = tmp_path / "work" / "uploads" / res.json()["id"]
    assert (root / "README.md").is_file()
    assert (root / "requirements.txt").is_file()
    assert not (root / "python-link").exists()
    assert not (root / "python-link").is_symlink()
    assert not (root / "__MACOSX").exists()
    assert not (root / "._README.md").exists()
    assert not (root / ".DS_Store").exists()


def test_clone_repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    import docassay.webapp.server as server

    def fake_clone(url: str, dest: Path, on_progress: object = None) -> None:
        dest.mkdir(parents=True, exist_ok=True)
        _mini_repo(dest)

    monkeypatch.setattr(server, "_clone_repository", fake_clone)
    client = _client(tmp_path)

    res = client.post("/api/repos/clone", json={"url": "https://github.com/org/demo.git"})
    assert res.status_code == 200
    body = res.json()
    assert body["kind"] == "clone"
    assert body["url"] == "https://github.com/org/demo.git"
    assert body["meta"]["claims"] == 1
    assert client.get(f"/api/repos/{body['id']}/bundle").status_code == 200

    repos = client.get("/api/repos").json()["repos"]
    assert repos[0]["url"] == "https://github.com/org/demo.git"

    clones = tmp_path / "work" / "repos" / "clones"
    assert any(clones.iterdir())

    assert client.delete(f"/api/repos/{body['id']}").status_code == 200
    assert list(clones.iterdir()) == []


@pytest.mark.parametrize(
    "bad",
    [
        "",
        "file:///etc/passwd",
        "/local/path",
        "./relative",
        "plain-name",
        "ssh://git@example.org/org/repo.git",
        "git://example.org/org/repo.git",
        "http://example.org/org/repo.git",
        "git@example.org:org/repo.git",
        "https:///nohost",
    ],
)
def test_clone_rejects_invalid_url(tmp_path: Path, bad: str) -> None:
    client = _client(tmp_path)
    res = client.post("/api/repos/clone", json={"url": bad})
    assert res.status_code == 400


def test_clone_failure_returns_400(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    import docassay.webapp.server as server

    def boom(url: str, dest: Path, on_progress: object = None) -> None:
        raise server.CloneError("could not clone 'x': boom")

    monkeypatch.setattr(server, "_clone_repository", boom)
    client = _client(tmp_path)
    res = client.post("/api/repos/clone", json={"url": "https://github.com/org/demo.git"})
    assert res.status_code == 400
    assert "boom" in res.text


def test_clone_progress_maps_phases() -> None:
    import docassay.webapp.server as server

    events: list[int | None] = []

    def on_progress(_kind: str, _message: str, percent: int | None = None) -> None:
        events.append(percent)

    state = {"percent": -1}
    for line in (
        "remote: Counting objects: 100% (10/10), done.",
        "Receiving objects:  50% (5/10)",
        "Receiving objects: 100% (10/10), done.",
        "Resolving deltas: 100% (3/3), done.",
    ):
        server._clone_progress(line, on_progress, state)

    # counting tops out at its band edge, receiving spans 10-90, deltas finish it
    assert events == [5, 50, 90, 100]


def test_clone_progress_drops_regressions() -> None:
    import docassay.webapp.server as server

    events: list[int | None] = []

    def on_progress(_kind: str, _message: str, percent: int | None = None) -> None:
        events.append(percent)

    state = {"percent": -1}
    server._clone_progress("Receiving objects:  30% (3/10)", on_progress, state)
    server._clone_progress("Receiving objects:  10% (1/10)", on_progress, state)
    assert events == [34]


def test_clone_stream_emits_percent(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    import docassay.webapp.server as server

    def fake_clone(url: str, dest: Path, on_progress: object = None) -> None:
        dest.mkdir(parents=True, exist_ok=True)
        _mini_repo(dest)
        assert callable(on_progress)
        on_progress("clone", "receiving objects 50%", percent=50)

    monkeypatch.setattr(server, "_clone_repository", fake_clone)
    client = _client(tmp_path)
    res = client.post(
        "/api/repos/clone?stream=true", json={"url": "https://github.com/org/demo.git"}
    )
    assert res.status_code == 200
    assert '"percent": 50' in res.text
    assert '"event": "done"' in res.text


def test_reclone_same_url_reuses_existing(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    import docassay.webapp.server as server

    def fake_clone(url: str, dest: Path, on_progress: object = None) -> None:
        dest.mkdir(parents=True, exist_ok=True)
        _mini_repo(dest)

    refreshed: list[Path] = []

    def fake_refresh(url: str, dest: Path, on_progress: object = None) -> None:
        refreshed.append(dest)

    monkeypatch.setattr(server, "_clone_repository", fake_clone)
    monkeypatch.setattr(server, "_refresh_clone_repository", fake_refresh)
    client = _client(tmp_path)

    first = client.post("/api/repos/clone", json={"url": "https://github.com/org/demo.git"}).json()
    # A second clone of the same remote (spelling differs only by `.git`) must
    # refresh the existing checkout, not add a second tree/manifest.
    second = client.post("/api/repos/clone", json={"url": "https://github.com/org/demo/"}).json()

    assert second["id"] == first["id"]
    assert refreshed, "expected the existing clone to be refreshed"
    assert len(client.get("/api/repos").json()["repos"]) == 1
    clones = tmp_path / "work" / "repos" / "clones"
    assert len(list(clones.iterdir())) == 1


def test_prune_sources_removes_orphans(tmp_path: Path) -> None:
    client = _client(tmp_path)
    clones = tmp_path / "work" / "repos" / "clones"
    bundles = tmp_path / "work" / "bundles"
    orphan = clones / "dead-cl00000000"
    orphan.mkdir(parents=True)
    (orphan / "file.txt").write_text("x" * 16)
    (bundles / "dead-cl00000000.json").write_text("{}")

    res = client.post("/api/repos/prune-sources")
    assert res.status_code == 200
    body = res.json()
    assert body["removed_dirs"] == 1
    assert body["removed_bundles"] == 1
    assert body["freed_bytes"] > 0
    assert not orphan.exists()
    assert not (bundles / "dead-cl00000000.json").exists()


def test_prune_duplicate_clones_keeps_newest(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import docassay.webapp.server as server

    def fake_clone(url: str, dest: Path, on_progress: object = None) -> None:
        dest.mkdir(parents=True, exist_ok=True)
        _mini_repo(dest)

    monkeypatch.setattr(server, "_clone_repository", fake_clone)
    client = _client(tmp_path)
    keep = client.post("/api/repos/clone", json={"url": "https://github.com/org/demo.git"}).json()

    # Forge an older duplicate of the same remote under a different id.
    work = tmp_path / "work"
    old_id = "demo-cl00000000"
    old_dir = work / "repos" / "clones" / old_id
    old_dir.mkdir(parents=True)
    (old_dir / "README.md").write_text(_english)
    old_manifest = work / "repos" / f"{old_id}.json"
    old_manifest.write_text(
        json.dumps(
            {
                "id": old_id,
                "name": "demo",
                "kind": "clone",
                "root": str(old_dir),
                "source_url": "https://github.com/org/demo",
            }
        )
    )
    (work / "bundles" / f"{old_id}.json").write_text("{}")
    os.utime(old_manifest, (1, 1))

    res = client.post("/api/repos/prune-duplicates")
    assert res.status_code == 200
    assert old_id in res.json()["removed"]
    assert not old_dir.exists()
    assert client.get(f"/api/repos/{keep['id']}/bundle").status_code == 200
    assert (work / "repos" / f"{keep['id']}.json").exists()


def test_store_roundtrip(tmp_path: Path) -> None:
    store = RepoStore(tmp_path / "work")
    manifest = {"id": "demo-0123456789", "name": "demo", "kind": "path", "root": "/tmp"}
    store.save_manifest(manifest)
    assert store.load_manifest("demo-0123456789") == manifest
    assert store.load_manifest("nope-0123456789") is None
    store.save_bundle("demo-0123456789", {"meta": {"repo": "demo"}})
    assert store.load_bundle("demo-0123456789")["meta"]["repo"] == "demo"
    assert store.load_bundle("nope-0123456789") is None


def test_corpus_repo_analyzed_on_open(tmp_path: Path) -> None:
    corpus = tmp_path / "corpus"
    repo = corpus / "demo"
    repo.mkdir(parents=True)
    _mini_repo(repo)
    app = create_app(workdir=tmp_path / "work", corpus_dir=corpus)
    client = TestClient(app, headers={"X-Session-Token": app.state.session_token})

    repos = client.get("/api/repos").json()["repos"]
    assert len(repos) == 1
    assert repos[0]["kind"] == "corpus"
    assert repos[0]["analyzed"] is False

    repo_id = repos[0]["id"]
    bundle = client.get(f"/api/repos/{repo_id}/bundle")
    assert bundle.status_code == 200
    assert bundle.json()["meta"]["repo"] == "demo"
    assert bundle.json()["meta"]["claims"] == 1

    repos = client.get("/api/repos").json()["repos"]
    assert repos[0]["analyzed"] is True


def test_delete_path_repo(tmp_path: Path) -> None:
    repo = tmp_path / "demo"
    repo.mkdir()
    _mini_repo(repo)
    client = _client(tmp_path)
    repo_id = client.post("/api/repos/analyze", json={"path": str(repo)}).json()["id"]

    assert client.get(f"/api/repos/{repo_id}/bundle").status_code == 200
    res = client.delete(f"/api/repos/{repo_id}")
    assert res.status_code == 200
    assert res.json() == {"ok": True}
    assert client.get(f"/api/repos/{repo_id}/bundle").status_code == 404
    assert client.get("/api/repos").json()["repos"] == []
    # The source tree is the caller's checkout and must survive deletion.
    assert repo.is_dir()


def test_delete_upload_repo_removes_source(tmp_path: Path) -> None:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("src/demo/", "")
        zf.writestr("demo/requirements.txt", "requests==2.31.0\n")
        zf.writestr(
            "demo/README.md",
            _english + "The project uses requests for the http client.\n",
        )
    buf.seek(0)
    client = _client(tmp_path)
    body = client.post("/api/repos/upload", files={"file": ("demo.zip", buf.getvalue())}).json()
    repo_id = body["id"]
    uploads = tmp_path / "work" / "uploads"
    assert any(uploads.iterdir())

    res = client.delete(f"/api/repos/{repo_id}")
    assert res.status_code == 200
    assert list(uploads.iterdir()) == []
    assert client.get("/api/repos").json()["repos"] == []


def test_clear_cache_reanalyzes_on_open(tmp_path: Path, monkeypatch) -> None:
    repo = tmp_path / "demo"
    repo.mkdir()
    (repo / "src").mkdir()
    (repo / "src" / "mod.py").write_text("class Klass:\n    pass\n")
    (repo / "requirements.txt").write_text("requests==2.31.0\n")
    (repo / "README.md").write_text(
        _english + "The project uses requests and provides the `Klass` symbol.\n"
    )
    # The symbol cache lives in the user cache (keyed by root hash), never inside
    # the analyzed tree.
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / "cache"))
    from docassay.evidence.symbols import cache_file

    client = _client(tmp_path)
    repo_id = client.post("/api/repos/analyze", json={"path": str(repo)}).json()["id"]
    cache_path = cache_file(repo)
    assert cache_path.is_file()
    assert not (repo / ".docassay_cache").exists()

    res = client.post("/api/repos/clear-cache")
    assert res.status_code == 200
    assert res.json()["cleared_bundles"] == 1
    assert res.json()["cleared_symbol_caches"] == 1
    assert not cache_path.exists()

    # The repo stays listed (manifest kept) but is un-analyzed again…
    repos = client.get("/api/repos").json()["repos"]
    assert [r["id"] for r in repos] == [repo_id]
    assert repos[0]["analyzed"] is False
    # …and re-analysis happens on the next open.
    assert client.get(f"/api/repos/{repo_id}/bundle").status_code == 200


def test_clear_cache_handles_multiple_repositories(tmp_path: Path, monkeypatch) -> None:
    # Regression: the loop used to rebind the imported `cache_file` function to
    # a Path on the first manifest, so clearing two or more repos crashed with
    # "'PosixPath' object is not callable".
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / "cache"))
    client = _client(tmp_path)

    ids: list[str] = []
    for name, symbol in (("alpha", "AlphaThing"), ("beta", "BetaThing")):
        repo = tmp_path / name
        repo.mkdir()
        (repo / "src").mkdir()
        (repo / "src" / "mod.py").write_text(f"class {symbol}:\n    pass\n")
        (repo / "requirements.txt").write_text("requests==2.31.0\n")
        (repo / "README.md").write_text(f"{_english}The project provides `{symbol}`.\n")
        ids.append(client.post("/api/repos/analyze", json={"path": str(repo)}).json()["id"])

    res = client.post("/api/repos/clear-cache")
    assert res.status_code == 200
    body = res.json()
    assert body["cleared_bundles"] == 2
    assert body["cleared_symbol_caches"] == 2
    assert sorted(r["id"] for r in client.get("/api/repos").json()["repos"]) == sorted(ids)


def test_delete_unknown_repo_404(tmp_path: Path) -> None:
    client = _client(tmp_path)
    assert client.delete("/api/repos/nope-0123456789").status_code == 404


@pytest.mark.parametrize(
    "bad_id",
    ["nope", "..%5C..%5Cx", "..%2F..%2Fx", "x-0123456789.json", "demo-UP01234567"],
)
def test_repo_routes_reject_foreign_ids(tmp_path: Path, bad_id: str) -> None:
    # Only the three id shapes the server mints may name a stored file.
    client = _client(tmp_path)
    assert client.delete(f"/api/repos/{bad_id}").status_code in (400, 404)
    assert client.get(f"/api/repos/{bad_id}/bundle").status_code in (400, 404)
    assert client.get(f"/api/repos/{bad_id}/log").status_code in (400, 404)


def test_repo_id_shapes() -> None:
    from docassay.webapp.server import is_valid_repo_id

    assert is_valid_repo_id("httpx-0123456789")
    assert is_valid_repo_id("demo_repo-upa1b2c3d4")
    assert is_valid_repo_id("demo.x-cla1b2c3d4")
    for bad in ("nope", "..\\..\\x-0123456789", "../x-0123456789", "a/b-0123456789", ""):
        assert not is_valid_repo_id(bad), bad


def test_prune_keeps_trees_of_running_analyses(tmp_path: Path) -> None:
    # A clone or upload has no manifest until its analysis finishes; prune
    # must not delete it in the meantime.
    store = RepoStore(tmp_path / "work")
    running = store.clone_dir("demo-cla1b2c3d4")
    running.mkdir(parents=True)
    orphan = store.clone_dir("old-clb1b2c3d4")
    orphan.mkdir(parents=True)
    store.mark_active("demo-cla1b2c3d4")
    report = store.prune_sources()
    assert running.is_dir()
    assert not orphan.exists()
    assert report["removed_dirs"] == 1
    store.release_active("demo-cla1b2c3d4")
    store.prune_sources()
    assert not running.exists()


def test_client_error_endpoint(tmp_path: Path) -> None:
    client = _client(tmp_path)
    res = client.post(
        "/api/client-error",
        json={"page": "http://localhost/#/repo/x", "message": "boom", "stack": "at f (a.js:1:2)"},
    )
    assert res.status_code == 200
    assert res.json() == {"ok": True}


# --- Phase 0: web security (B4) and runtime cache fixes (B19, B20) ----------


def test_api_requires_session_token(tmp_path: Path) -> None:
    app = create_app(workdir=tmp_path / "work", corpus_dir=tmp_path / "nonexistent-corpus")
    client = TestClient(app)  # no token header
    assert client.get("/api/health").status_code == 401
    assert client.get("/api/repos").status_code == 401
    assert client.post("/api/repos/analyze", json={"path": str(tmp_path)}).status_code == 401
    assert client.get("/api/repos/does-not-exist/bundle").status_code == 401


def test_api_accepts_any_session_token_from_the_app(tmp_path: Path) -> None:
    app = create_app(workdir=tmp_path / "work", corpus_dir=tmp_path / "nonexistent-corpus")
    client = TestClient(app, headers={"X-Session-Token": app.state.session_token})
    assert client.get("/api/repos").status_code == 200


def test_index_never_carries_the_session_token(tmp_path: Path) -> None:
    # The token reaches the browser only through the start address printed by
    # the server, never through a served page.
    static = tmp_path / "static"
    static.mkdir()
    (static / "index.html").write_text("<html><head><title>demo</title></head><body></body></html>")
    app = create_app(
        workdir=tmp_path / "work",
        corpus_dir=tmp_path / "nonexistent-corpus",
        static_dir=static,
    )
    client = TestClient(app)
    html = client.get("/").text
    assert app.state.session_token not in html
    assert json.dumps(app.state.session_token) not in html


def test_loopback_index_redirects_to_the_printed_address(tmp_path: Path) -> None:
    # Opening the bare http://127.0.0.1:8000/ (bookmark, new tab, reload) must
    # not render a UI whose every API call 401s.
    static = tmp_path / "static"
    static.mkdir()
    (static / "index.html").write_text("<html><body>demo</body></html>")
    app = create_app(
        workdir=tmp_path / "work",
        corpus_dir=tmp_path / "nonexistent-corpus",
        static_dir=static,
    )
    client = TestClient(app, client=("127.0.0.1", 50000), follow_redirects=False)

    res = client.get("/")
    assert res.status_code == 307
    assert res.headers["location"] == f"/?token={app.state.session_token}"
    assert res.headers["cache-control"] == "no-store"

    # The redirected address serves the page, which does not embed the token.
    page = client.get(res.headers["location"]).text
    assert "demo" in page
    assert app.state.session_token not in page
    # …and its token is the one the API accepts.
    assert (
        client.get("/api/repos", headers={"X-Session-Token": app.state.session_token}).status_code
        == 200
    )


def test_stale_token_in_the_address_bar_is_replaced(tmp_path: Path) -> None:
    # A tab restored from an earlier server run still has the old token.
    static = tmp_path / "static"
    static.mkdir()
    (static / "index.html").write_text("<html><body>demo</body></html>")
    app = create_app(
        workdir=tmp_path / "work",
        corpus_dir=tmp_path / "nonexistent-corpus",
        static_dir=static,
    )
    client = TestClient(app, client=("127.0.0.1", 50000), follow_redirects=False)
    res = client.get("/?token=token-from-an-earlier-run")
    assert res.status_code == 307
    assert res.headers["location"] == f"/?token={app.state.session_token}"


def test_remote_client_is_not_redirected_to_the_token(tmp_path: Path) -> None:
    # Over a non-loopback connection the printed URL stays mandatory.
    static = tmp_path / "static"
    static.mkdir()
    (static / "index.html").write_text("<html><body>demo</body></html>")
    app = create_app(
        workdir=tmp_path / "work",
        corpus_dir=tmp_path / "nonexistent-corpus",
        static_dir=static,
    )
    client = TestClient(app, client=("203.0.113.7", 50000), follow_redirects=False)
    res = client.get("/")
    assert res.status_code == 200
    assert app.state.session_token not in res.text
    assert client.get("/api/repos").status_code == 401


def test_container_bare_index_redirects_by_loopback_host(tmp_path: Path) -> None:
    # Docker publishes the UI on localhost:<host-port>, but the connection
    # arrives from the bridge gateway (not 127.0.0.1). With --allow-bare-index
    # the loopback Host header is enough to hand the browser the token.
    static = tmp_path / "static"
    static.mkdir()
    (static / "index.html").write_text("<html><body>demo</body></html>")
    app = create_app(
        workdir=tmp_path / "work",
        corpus_dir=tmp_path / "nonexistent-corpus",
        static_dir=static,
        allow_bare_index=True,
    )
    client = TestClient(
        app,
        base_url="http://localhost:8010",
        client=("192.168.65.1", 50000),
        follow_redirects=False,
    )

    res = client.get("/")
    assert res.status_code == 307
    assert res.headers["location"] == f"/?token={app.state.session_token}"
    assert client.get(res.headers["location"]).status_code == 200

    # A remote Host is still not redirected, even with the flag enabled.
    remote = TestClient(
        app,
        base_url="http://example.com:8010",
        client=("192.168.65.1", 50000),
        follow_redirects=False,
    )
    assert remote.get("/").status_code == 200


def test_container_bare_index_requires_the_flag(tmp_path: Path) -> None:
    static = tmp_path / "static"
    static.mkdir()
    (static / "index.html").write_text("<html><body>demo</body></html>")
    app = create_app(
        workdir=tmp_path / "work",
        corpus_dir=tmp_path / "nonexistent-corpus",
        static_dir=static,
    )
    client = TestClient(
        app,
        base_url="http://localhost:8010",
        client=("192.168.65.1", 50000),
        follow_redirects=False,
    )
    assert client.get("/").status_code == 200


@pytest.mark.parametrize(
    "host, expected",
    [
        ("localhost", True),
        ("localhost:8010", True),
        ("127.0.0.1:8010", True),
        ("[::1]:8010", True),
        ("example.com:8010", False),
        ("192.168.1.5:8010", False),
    ],
)
def test_loopback_host_header(host: str, expected: bool) -> None:
    from docassay.webapp.server import _is_loopback_host_header

    assert _is_loopback_host_header(host) is expected


def test_run_reads_port_and_public_url_from_env(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    import docassay.webapp.server as server

    seen: dict[str, object] = {}

    def fake_run(app: object, *, host: str, port: int) -> None:
        seen["host"] = host
        seen["port"] = port

    monkeypatch.setenv("DOCASSAY_PORT", "8123")
    monkeypatch.setenv("DOCASSAY_PUBLIC_URL", "http://localhost:9000")
    monkeypatch.setattr("uvicorn.run", fake_run)

    assert server.run(workdir=tmp_path / "work") == 0
    assert seen == {"host": "127.0.0.1", "port": 8123}
    out = capsys.readouterr().out
    assert "open: http://localhost:9000/?token=" in out


def test_foreign_host_header_is_refused(tmp_path: Path) -> None:
    from docassay.webapp.server import host_header_values

    static = tmp_path / "static"
    static.mkdir()
    (static / "index.html").write_text("<html><head></head><body></body></html>")
    app = create_app(
        workdir=tmp_path / "work",
        corpus_dir=tmp_path / "nonexistent-corpus",
        static_dir=static,
        allowed_hosts=host_header_values("127.0.0.1", 8000, []),
    )
    token = {"X-Session-Token": app.state.session_token}
    client = TestClient(app, base_url="http://127.0.0.1:8000")
    assert client.get("/").status_code == 200
    assert client.get("/api/health", headers=token).status_code == 200
    rebound = TestClient(app, base_url="http://attacker.example:8000")
    assert rebound.get("/").status_code == 400
    assert rebound.get("/api/health", headers=token).status_code == 400


def test_host_header_values() -> None:
    from docassay.webapp.server import host_header_values

    loop = host_header_values("127.0.0.1", 8000, [])
    assert {"127.0.0.1:8000", "localhost:8000", "[::1]:8000"} <= set(loop)
    assert "0.0.0.0:8000" not in host_header_values("0.0.0.0", 8000, [])
    assert "demo.local:8000" in host_header_values("0.0.0.0", 8000, ["demo.local"])
    assert "10.0.0.5:8000" in host_header_values("10.0.0.5", 8000, [])
    # ``*`` is the explicit opt-out used by the container image: a reviewer may
    # publish the container on any host port, so the Host header cannot be
    # predicted at launch time.
    assert host_header_values("0.0.0.0", 8000, ["*"]) == ["*"]


def test_wildcard_host_disables_the_check(tmp_path: Path) -> None:
    from docassay.webapp.server import host_header_values

    static = tmp_path / "static"
    static.mkdir()
    (static / "index.html").write_text("<html><head></head><body></body></html>")
    app = create_app(
        workdir=tmp_path / "work",
        corpus_dir=tmp_path / "nonexistent-corpus",
        static_dir=static,
        allowed_hosts=host_header_values("0.0.0.0", 8000, ["*"]),
    )
    token = {"X-Session-Token": app.state.session_token}
    client = TestClient(app, base_url="http://127.0.0.1:8123")
    assert client.get("/").status_code == 200
    assert client.get("/api/health", headers=token).status_code == 200


def test_no_cors_headers_emitted(tmp_path: Path) -> None:
    client = _client(tmp_path)
    res = client.get("/api/repos")
    assert "access-control-allow-origin" not in res.headers
    res = client.options("/api/repos")
    assert "access-control-allow-origin" not in res.headers


def test_local_path_analysis_disabled_off_loopback(tmp_path: Path) -> None:
    repo = tmp_path / "demo"
    repo.mkdir()
    _mini_repo(repo)
    client = _client(tmp_path, allow_local_paths=False)
    res = client.post("/api/repos/analyze", json={"path": str(repo)})
    assert res.status_code == 403
    assert "disabled" in res.text


def test_allow_root_restricts_path_analysis(tmp_path: Path) -> None:
    allowed = tmp_path / "allowed"
    denied = tmp_path / "denied"
    (allowed / "demo").mkdir(parents=True)
    (denied / "demo").mkdir(parents=True)
    _mini_repo(allowed / "demo")
    _mini_repo(denied / "demo")
    client = _client(tmp_path, allow_root=[allowed])

    ok = client.post("/api/repos/analyze", json={"path": str(allowed / "demo")})
    assert ok.status_code == 200
    assert ok.json()["meta"]["claims"] == 1

    bad = client.post("/api/repos/analyze", json={"path": str(denied / "demo")})
    assert bad.status_code == 403


def test_stored_path_repo_reanalysis_obeys_allow_root(tmp_path: Path) -> None:
    repo = tmp_path / "demo"
    repo.mkdir()
    _mini_repo(repo)
    client = _client(tmp_path)
    repo_id = client.post("/api/repos/analyze", json={"path": str(repo)}).json()["id"]
    assert client.post("/api/repos/clear-cache").status_code == 200

    # A server restarted with an --allow-root that no longer covers this root
    # must refuse to re-analyze and to serve the file.
    restricted = _client(tmp_path, allow_root=[tmp_path / "other"])
    assert restricted.get(f"/api/repos/{repo_id}/bundle").status_code == 403
    assert (
        restricted.get(f"/api/repos/{repo_id}/file", params={"path": "README.md"}).status_code
        == 403
    )


def test_clear_cache_preserves_upload_repo_id(tmp_path: Path) -> None:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("src/demo/", "")
        zf.writestr("demo/requirements.txt", "requests==2.31.0\n")
        zf.writestr(
            "demo/README.md",
            _english + "The project uses requests for the http client.\n",
        )
    buf.seek(0)
    client = _client(tmp_path)
    repo_id = client.post("/api/repos/upload", files={"file": ("demo.zip", buf.getvalue())}).json()[
        "id"
    ]

    assert client.post("/api/repos/clear-cache").status_code == 200
    assert client.get(f"/api/repos/{repo_id}/bundle").status_code == 200

    # Re-analysis after the cache clear must reuse the original id: no second
    # manifest, no orphaned upload directory.
    repos = client.get("/api/repos").json()["repos"]
    assert [r["id"] for r in repos] == [repo_id]
    uploads = tmp_path / "work" / "uploads"
    assert len(list(uploads.iterdir())) == 1

    assert client.delete(f"/api/repos/{repo_id}").status_code == 200
    assert list(uploads.iterdir()) == []


def test_symbol_inventory_refreshes_after_source_change(tmp_path: Path) -> None:
    from docassay.evidence.symbols import build_symbol_inventory

    src = tmp_path / "src"
    src.mkdir()
    (src / "mod.py").write_text("class Klass:\n    pass\n")
    first = {s.name for s in build_symbol_inventory(tmp_path)}
    assert "mod.klass" in first
    assert "mod.newone" not in first

    (src / "mod.py").write_text("class Klass:\n    pass\n\nclass NewOne:\n    pass\n")
    second = {s.name for s in build_symbol_inventory(tmp_path)}
    assert "mod.newone" in second
