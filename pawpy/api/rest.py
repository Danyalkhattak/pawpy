"""FastAPI REST endpoints for Pawpy."""

import logging
import os
import tempfile
import uuid
from typing import Annotated, Any, Dict

logger = logging.getLogger("pawpy.api")

_app = None


def get_app():
    """Lazily create and return the FastAPI app."""
    global _app
    if _app is not None:
        return _app

    try:
        from fastapi import FastAPI, File, Form, UploadFile
        from fastapi.responses import FileResponse, JSONResponse
    except ImportError:
        raise ImportError(
            "FastAPI is required for API mode. "
            "Install it with: pip install fastapi uvicorn"
        )

    app = FastAPI(
        title="Pawpy API",
        description="Educational Wordlist Generator – REST API",
        version="1.0.0",
        # ⚠️ optional safety switch if OpenAPI keeps crashing on Python 3.14
        # openapi_url=None,
    )

    _jobs: Dict[str, Dict[str, Any]] = {}

    @app.get("/")
    async def root():
        return {"name": "Pawpy API", "version": "1.0.0", "status": "running"}

    @app.post("/generate")
    async def generate_wordlist(
        profile: Annotated[UploadFile, File(...)],
        output: Annotated[str | None, Form()] = None,
        lite: Annotated[bool, Form()] = False,
        extreme: Annotated[bool, Form()] = False,
        min_length: Annotated[int | None, Form()] = None,
        min_strength: Annotated[int | None, Form()] = None,
        markov: Annotated[bool, Form()] = False,
    ):
        """Generate a wordlist from an uploaded profile JSON file."""

        job_id = str(uuid.uuid4())[:8]
        out_file = output or f"pawpy_{job_id}.txt"

        tmp_profile = tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, prefix="pawpy_profile_"
        )

        content = await profile.read()
        tmp_profile.write(content.decode("utf-8", errors="ignore"))
        tmp_profile.close()

        try:
            from pawpy.config import PawpyConfig
            from pawpy.generator.core import PipelineOrchestrator
            from pawpy.profile.base import ProfileCollector

            config = PawpyConfig(
                output_file=out_file,
                profile_json=tmp_profile.name,
                lite=lite,
                extreme=extreme,
                min_length=min_length,
                min_strength=min_strength,
                markov=markov,
            )

            collector = ProfileCollector()
            prof = collector.run(config)

            orchestrator = PipelineOrchestrator(config, prof)
            result_path = orchestrator.run()

            _jobs[job_id] = {
                "status": "completed",
                "output": result_path,
                "size": os.path.getsize(result_path),
            }

            return JSONResponse(
                content={
                    "job_id": job_id,
                    "status": "completed",
                    "download_url": f"/download/{job_id}",
                }
            )

        except Exception as e:
            logger.exception("Generation failed")
            return JSONResponse(
                status_code=500,
                content={"job_id": job_id, "status": "error", "message": str(e)},
            )

        finally:
            try:
                os.unlink(tmp_profile.name)
            except Exception:
                pass

    @app.get("/download/{job_id}")
    async def download_wordlist(job_id: str):
        job = _jobs.get(job_id)

        if not job or job["status"] != "completed":
            return JSONResponse(
                status_code=404,
                content={"error": "Job not found or not completed"},
            )

        return FileResponse(
            job["output"],
            media_type="text/plain",
            filename=os.path.basename(job["output"]),
        )

    @app.get("/jobs")
    async def list_jobs():
        return {"jobs": _jobs}

    _app = app
    return app


def run_api(host: str = "127.0.0.1", port: int = 8000):
    """Start API server."""
    app = get_app()

    import uvicorn

    logger.info("Starting Pawpy API on %s:%d", host, port)
    uvicorn.run(app, host=host, port=port)
