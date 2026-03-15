# GitHub Actions CI/CD Configuration

This project includes automated GitHub Actions workflows to build Windows executables and validate code quality.

## Workflows

### 1. **build-release.yml** - Release Build
**Triggers**:
- On GitHub release (published)
- Manual trigger via `workflow_dispatch`

**What it does**:
- Checks out code
- Sets up Python 3.11
- Installs all build dependencies
- Runs linting and formatting checks
- Builds Windows executable using PyInstaller
- Uploads executable to release assets (if triggered by release)
- Keeps artifact for 30 days

**How to use**:
1. Create a GitHub release on your repository
2. The workflow automatically builds and attaches the executable to the release
3. Or manually trigger via GitHub Actions UI: `Actions → Build Windows Executable → Run workflow`

**Output**:
- `CAN_Pro_Decoder.exe` attached to release
- Artifact available in Actions tab

---

### 2. **validate.yml** - Pull Request & Main Branch Validation
**Triggers**:
- On pull requests to `main` or `develop` branches
- On pushes to `main` or `develop` branches

**What it does**:
- Runs on Python 3.11 and 3.12
- Installs dependencies
- Runs ruff linting
- Runs mypy type checking
- Runs pytest tests
- Builds executable (validation only, not released)
- Uploads test reports as artifacts

**How to use**:
- Automatic on every PR and push to main/develop
- Check workflow status in PR comments and Actions tab
- Review any failed checks before merging

---

## Local Development Equivalent Commands

### Build locally:
```bash
source venv/bin/activate  # or .\venv\Scripts\activate on Windows
python build_exe.py
```

### Run quality checks locally:
```bash
make quality        # All checks: ruff, mypy, black
make lint           # Ruff linting
make type-check     # Mypy type checking
```

### Run tests locally:
```bash
make test            # With coverage report
make test-quick      # Quick test run
pytest -v            # Verbose pytest output
```

---

## Setup Instructions for First-Time Use

1. **Ensure `requirements-build.txt` exists** in repo root
   - Already created in this configuration

2. **Ensure `build_exe.py` is present** with correct settings
   - Already configured for single-file Windows executable

3. **Create your first release**:
   ```bash
   git tag -a v0.3.0 -m "Release version 0.3.0"
   git push origin v0.3.0
   ```
   GitHub will automatically create a release and the workflow will build the executable

4. **Monitor build progress**:
   - Go to your GitHub repository
   - Click "Actions" tab
   - Watch the "Build Windows Executable" workflow run
   - Check for any errors in the build logs

---

## Customization

### Change Python version:
Edit `.github/workflows/build-release.yml` and `.github/workflows/validate.yml`:
```yaml
python-version: ["3.12"]  # Change to desired version
```

### Change executable name:
Edit `build_exe.py`:
```python
"--name=YourAppName",
```

### Add/remove validation checks:
Edit `.github/workflows/validate.yml` and add/remove steps as needed

### Run on different branch:
Edit workflow trigger in yaml files:
```yaml
on:
  push:
    branches: [main, develop, staging]  # Add branches here
```

---

## Troubleshooting

### Build fails with "No such file or directory: 'cantools'"
- Ensure `requirements-build.txt` has all dependencies
- Check PyInstaller `--hidden-import` options in `build_exe.py`

### Build fails with Windows-specific errors
- GitHub Actions runs on latest Windows, may have subtle differences
- Test locally with `python build_exe.py`
- Check file paths use backslashes or raw strings on Windows

### Artifact not appearing in release
- Verify the release was created as "published" not "draft"
- Check workflow logs for build errors
- Ensure `--onefile` flag is set in PyInstaller config

### Tests failing in CI but passing locally
- Different Python versions may behave differently
- GitHub runs with Python 3.11 and 3.12
- Try running locally with `python3.11` or `python3.12`

---

## Release Checklist

Before creating a release:
- [ ] Run `make quality` locally and verify all checks pass
- [ ] Run `make test` locally and verify tests pass
- [ ] Update version in `pyproject.toml`
- [ ] Update `CHANGELOG.md` (if using)
- [ ] Commit changes and push to main
- [ ] Create release tag: `git tag -a vX.Y.Z -m "Description"`
- [ ] Push tag: `git push origin vX.Y.Z`
- [ ] Monitor GitHub Actions workflow
- [ ] Verify executable builds successfully
- [ ] Test downloaded executable on Windows

---

## Additional Resources

- [PyInstaller Documentation](https://pyinstaller.org/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [secrets in GitHub Actions](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
