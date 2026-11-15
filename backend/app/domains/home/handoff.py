from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit


WEEKLY_REMINDER_SOURCE = "weekly_reminder"
UPLOAD_FIRST_SURFACE_STATE = "progress_proof"
WEEKLY_SCAN_SURFACE_STATE = "weekly_scan"


def append_query_params_to_path(path: str, params: dict[str, str | None]) -> str:
    parts = urlsplit(path)
    query = dict(parse_qsl(parts.query, keep_blank_values=True))
    for key, value in params.items():
        if value is None:
            continue
        query[key] = value
    return urlunsplit((
        "",
        "",
        parts.path,
        urlencode(query),
        parts.fragment,
    ))


def extract_query_param(path: str | None, key: str) -> str | None:
    if not path:
        return None
    parts = urlsplit(path)
    for query_key, query_value in parse_qsl(parts.query, keep_blank_values=True):
        if query_key == key:
            return query_value or None
    return None


def should_use_upload_first_handoff(
    *,
    source: str | None,
    reentry_state: str,
    proof_photo_count: int,
    enabled: bool,
) -> bool:
    return (
        enabled
        and source == WEEKLY_REMINDER_SOURCE
        and reentry_state == WEEKLY_SCAN_SURFACE_STATE
        and proof_photo_count < 2
    )


def resolve_surface_state(
    *,
    source: str | None,
    reentry_state: str,
    proof_photo_count: int,
    enabled: bool,
) -> str:
    if should_use_upload_first_handoff(
        source=source,
        reentry_state=reentry_state,
        proof_photo_count=proof_photo_count,
        enabled=enabled,
    ):
        return UPLOAD_FIRST_SURFACE_STATE
    return reentry_state


def build_progress_upload_handoff_path(
    *,
    source: str,
    reentry_state: str,
    surface_state: str = UPLOAD_FIRST_SURFACE_STATE,
) -> str:
    return append_query_params_to_path(
        "/progress",
        {
            "tab": "photos",
            "focus": "upload",
            "from": source,
            "reentry_state": reentry_state,
            "surface_state": surface_state,
        },
    )


def build_weekly_scan_journey_handoff_path(
    *,
    source: str,
    reentry_state: str = WEEKLY_SCAN_SURFACE_STATE,
    surface_state: str = WEEKLY_SCAN_SURFACE_STATE,
) -> str:
    return append_query_params_to_path(
        "/body-scan#transformation",
        {
            "tab": "journey",
            "from": source,
            "reentry_state": reentry_state,
            "surface_state": surface_state,
        },
    )
