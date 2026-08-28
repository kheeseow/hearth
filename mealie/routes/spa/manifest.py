import json
from typing import Any
from urllib.parse import urlparse

from fastapi import Depends, Response
from sqlalchemy.orm import Session

from mealie.core.config import get_app_settings
from mealie.db.db_setup import generate_session
from mealie.services.app_capabilities_service import AppCapabilitiesService


def serve_manifest(session: Session = Depends(generate_session)):
    settings = get_app_settings()
    sub_path = urlparse(settings.BASE_URL).path or "/"
    capabilities = AppCapabilitiesService(session, settings.HEARTH_LEGACY_FEATURES).get()

    manifest: dict[str, Any] = {
        "name": settings.brand.name,
        "short_name": settings.brand.short_name,
        "id": "/",
        "start_url": sub_path,
        "scope": sub_path,
        "display": "standalone",
        "background_color": "#1E1E1E",
        "theme_color": settings.theme.light_primary,
        "description": settings.brand.description,
        "lang": "en",
        "display_override": ["standalone", "minimal-ui", "browser", "window-controls-overlay"],
        "categories": ["lifestyle", "productivity", "utilities"],
        "prefer_related_applications": False,
        "handle_links": "preferred",
        "launch_handler": {"client_mode": ["focus-existing", "auto"]},
        "edge_side_panel": {"preferred_width": 400},
        "icons": [
            {
                "src": "/icons/hearth-mark.svg",
                "sizes": "any",
                "type": "image/svg+xml",
                "purpose": "any maskable",
            },
        ],
        "shortcuts": [
            {
                "name": "Guides",
                "short_name": "Guides",
                "description": "Open your guides",
                "url": sub_path,
                "icons": [{"src": "/icons/hearth-mark.svg", "sizes": "any", "type": "image/svg+xml"}],
            }
        ],
    }

    if capabilities.legacy_recipes:
        manifest["share_target"] = {
            "action": "/r/create/url",
            "method": "GET",
            "enctype": "application/x-www-form-urlencoded",
            "params": {
                "url": "recipe_import_url",
                "text": "recipe_import_text",
            },
        }

    if capabilities.shopping_lists:
        manifest["shortcuts"].append(
            {
                "name": "Shopping Lists",
                "short_name": "Shopping Lists",
                "description": "Open the shopping lists",
                "url": "/shopping-lists",
                "icons": [
                    {"src": "/icons/mdiFormatListChecks-192x192.png", "sizes": "192x192"},
                    {"src": "/icons/mdiFormatListChecks-96x96.png", "sizes": "96x96"},
                ],
            }
        )

    if capabilities.meal_planning:
        manifest["shortcuts"].append(
            {
                "name": "Meal Planner",
                "short_name": "Meal Planner",
                "description": "Open the meal planner",
                "url": "/household/mealplan/planner/view",
                "icons": [
                    {"src": "/icons/mdiCalendarMultiselect-192x192.png", "sizes": "192x192"},
                    {"src": "/icons/mdiCalendarMultiselect-96x96.png", "sizes": "96x96"},
                ],
            }
        )

    return Response(
        content=json.dumps(manifest),
        media_type="application/manifest+json",
        headers={"Cache-Control": "no-cache"},
    )
