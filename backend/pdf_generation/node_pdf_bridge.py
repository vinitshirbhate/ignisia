from __future__ import annotations

import os
import subprocess
import uuid
from pathlib import Path
from contextlib import suppress

from schemas import ProposalRequest
from pdf_generator import build_proposal_pdf


BACKEND_DIR = Path(__file__).resolve().parent
REPO_ROOT = BACKEND_DIR.parent.parent
FRONTEND_DIR = REPO_ROOT / "frontend"
RENDER_SCRIPT = "scripts/render-quotation.cjs"


def _renderer_command() -> list[str]:
    return ["node"]


def render_pdf_via_node(payload: ProposalRequest) -> bytes:
    render_script_path = FRONTEND_DIR / RENDER_SCRIPT
    if not render_script_path.exists():
        return build_proposal_pdf(payload)

    render_dir = BACKEND_DIR / ".render_tmp"
    render_dir.mkdir(exist_ok=True)

    token = uuid.uuid4().hex
    input_path = render_dir / f"{token}.json"
    output_path = render_dir / f"{token}.pdf"

    try:
        input_path.write_text(payload.model_dump_json(indent=2), encoding="utf-8")

        command = [
            *_renderer_command(),
            RENDER_SCRIPT,
            str(input_path),
            str(output_path),
        ]

        completed = subprocess.run(
            command,
            cwd=FRONTEND_DIR,
            capture_output=True,
            text=True,
            check=False,
        )

        if completed.returncode != 0:
            stderr = completed.stderr.strip()
            stdout = completed.stdout.strip()
            message = stderr or stdout or "Unknown Node PDF renderer error"
            if "Cannot find module" in message and RENDER_SCRIPT in message:
                return build_proposal_pdf(payload)
            raise RuntimeError(message)

        return output_path.read_bytes()
    finally:
        with suppress(OSError):
            if input_path.exists():
                input_path.unlink()
        with suppress(OSError):
            if output_path.exists():
                output_path.unlink()
