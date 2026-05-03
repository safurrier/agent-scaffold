from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit


def _write_script(path: Path, content: str) -> None:
    path.write_text(content)
    path.chmod(path.stat().st_mode | 0o111)


def test_canonical_scripts_contract_can_delegate_to_native_tools(
    tmp_path: Path,
) -> None:
    scripts = tmp_path / "scripts"
    log = tmp_path / "commands.log"
    scripts.mkdir()
    for name in ("lint", "typecheck", "test"):
        _write_script(
            scripts / name,
            f"#!/usr/bin/env bash\nset -euo pipefail\necho {name} >> {log}\n",
        )
    _write_script(
        scripts / "check",
        "#!/usr/bin/env bash\nset -euo pipefail\nscripts/lint\nscripts/typecheck\nscripts/test\n",
    )

    result = subprocess.run(
        ["scripts/check"],
        cwd=tmp_path,
        capture_output=True,
        check=False,
        text=True,
        env=os.environ.copy(),
    )

    assert result.returncode == 0, result.stderr
    assert log.read_text().splitlines() == ["lint", "typecheck", "test"]


def test_canonical_scripts_contract_fails_fast(tmp_path: Path) -> None:
    scripts = tmp_path / "scripts"
    log = tmp_path / "commands.log"
    scripts.mkdir()
    _write_script(
        scripts / "lint",
        f"#!/usr/bin/env bash\nset -euo pipefail\necho lint >> {log}\n",
    )
    _write_script(
        scripts / "typecheck", "#!/usr/bin/env bash\nset -euo pipefail\nexit 12\n"
    )
    _write_script(
        scripts / "test",
        f"#!/usr/bin/env bash\nset -euo pipefail\necho test >> {log}\n",
    )
    _write_script(
        scripts / "check",
        "#!/usr/bin/env bash\nset -euo pipefail\nscripts/lint\nscripts/typecheck\nscripts/test\n",
    )

    result = subprocess.run(
        ["scripts/check"],
        cwd=tmp_path,
        capture_output=True,
        check=False,
        text=True,
        env=os.environ.copy(),
    )

    assert result.returncode == 12
    assert log.read_text().splitlines() == ["lint"]
