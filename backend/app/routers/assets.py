from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import HTMLResponse, Response


router = APIRouter()

REPO_ROOT = Path(__file__).resolve().parents[3]
HUMAN_BODY_MODEL_CANDIDATES = [
    REPO_ROOT / "human-converted.glb",
    REPO_ROOT / "frontend" / "public" / "assets" / "human-converted.glb",
]


def _load_human_body_model() -> bytes | None:
    for candidate in HUMAN_BODY_MODEL_CANDIDATES:
        if candidate.exists():
            return candidate.read_bytes()
    return None


@router.get("/assets/human-body-model")
async def get_human_body_model() -> Response:
    buffer = _load_human_body_model()
    if buffer is None:
        searched = ", ".join(str(path) for path in HUMAN_BODY_MODEL_CANDIDATES)
        return Response(
            content=f"Missing required asset. Looked for: {searched}",
            status_code=404,
            media_type="text/plain; charset=utf-8",
            headers={"Cache-Control": "no-store"},
        )

    return Response(
        content=buffer,
        media_type="model/gltf-binary",
        headers={"Cache-Control": "public, max-age=3600"},
    )


@router.get("/assets/human-body-preview", response_class=HTMLResponse)
async def get_human_body_preview() -> HTMLResponse:
    return HTMLResponse(
        """
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta
      name="viewport"
      content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no"
    />
    <title>Devenira Body Preview</title>
    <script
      type="module"
      src="https://ajax.googleapis.com/ajax/libs/model-viewer/4.1.0/model-viewer.min.js"
    ></script>
    <style>
      :root {
        color-scheme: dark;
        --gold: #e7cc98;
        --mint: #79d7c2;
        --ink: #090705;
        --panel: rgba(13, 10, 8, 0.88);
      }

      * {
        box-sizing: border-box;
      }

      html,
      body {
        width: 100%;
        height: 100%;
        margin: 0;
        overflow: hidden;
        background:
          radial-gradient(circle at 50% 24%, rgba(121, 215, 194, 0.24), transparent 44%),
          radial-gradient(circle at 50% 80%, rgba(231, 204, 152, 0.16), transparent 42%),
          linear-gradient(180deg, #15100d 0%, #0b0806 100%);
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Segoe UI", sans-serif;
      }

      .shell {
        position: relative;
        width: 100%;
        height: 100%;
        padding: 18px 16px 14px;
      }

      .halo {
        position: absolute;
        inset: 14% 12% 18%;
        border-radius: 999px;
        background:
          radial-gradient(circle, rgba(121, 215, 194, 0.18) 0%, rgba(121, 215, 194, 0.08) 34%, transparent 72%);
        filter: blur(18px);
        pointer-events: none;
      }

      model-viewer {
        width: 100%;
        height: 100%;
        --poster-color: transparent;
        background: transparent;
      }

      .overlay {
        position: absolute;
        left: 18px;
        right: 18px;
        bottom: 10px;
        display: flex;
        justify-content: space-between;
        align-items: end;
        gap: 12px;
        pointer-events: none;
      }

      .meta {
        display: flex;
        flex-direction: column;
        gap: 4px;
      }

      .eyebrow {
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 0.22em;
        color: rgba(231, 204, 152, 0.78);
        text-transform: uppercase;
      }

      .label {
        font-size: 12px;
        line-height: 1.3;
        color: rgba(247, 240, 228, 0.86);
      }

      .rings {
        display: flex;
        gap: 8px;
        align-items: center;
      }

      .ring {
        width: 10px;
        height: 10px;
        border-radius: 999px;
        background: rgba(121, 215, 194, 0.58);
        box-shadow: 0 0 14px rgba(121, 215, 194, 0.52);
      }

      .ring:nth-child(2) {
        background: rgba(231, 204, 152, 0.74);
        box-shadow: 0 0 14px rgba(231, 204, 152, 0.58);
      }

      .error {
        position: absolute;
        inset: 0;
        display: none;
        align-items: center;
        justify-content: center;
        padding: 24px;
        text-align: center;
        background: rgba(9, 7, 5, 0.84);
        color: rgba(247, 240, 228, 0.88);
      }
    </style>
  </head>
  <body>
    <div class="shell">
      <div class="halo"></div>
      <model-viewer
        id="viewer"
        src="/api/assets/human-body-model"
        camera-controls
        disable-pan
        interaction-prompt="none"
        auto-rotate
        auto-rotate-delay="0"
        rotation-per-second="24deg"
        shadow-intensity="0"
        exposure="1.12"
        min-camera-orbit="auto auto 96%"
        max-camera-orbit="auto auto 132%"
        camera-orbit="0deg 83deg 116%"
        field-of-view="26deg"
      ></model-viewer>
      <div class="overlay">
        <div class="meta">
          <div class="eyebrow">Weekly Body View</div>
          <div class="label">Same human anatomy model as web.</div>
        </div>
        <div class="rings">
          <div class="ring"></div>
          <div class="ring"></div>
        </div>
      </div>
      <div id="error" class="error">The 3D model could not load right now.</div>
    </div>
    <script>
      const viewer = document.getElementById('viewer');
      const error = document.getElementById('error');

      function post(type, payload) {
        if (window.ReactNativeWebView) {
          window.ReactNativeWebView.postMessage(JSON.stringify({ type, payload }));
        }
      }

      viewer.addEventListener('load', () => {
        post('loaded');
      });

      viewer.addEventListener('error', (event) => {
        error.style.display = 'flex';
        post('error', String(event?.detail?.type || 'model-error'));
      });
    </script>
  </body>
</html>
        """.strip(),
        headers={"Cache-Control": "public, max-age=300"},
    )
