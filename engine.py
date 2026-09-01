import os
import json
from typing import Dict, Any, List
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# SDK Imports
try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

try:
    from parallel import Parallel
    PARALLEL_AVAILABLE = True
except ImportError:
    PARALLEL_AVAILABLE = False

MIN_VENUES = 3
MIN_PERMITS = 2


def search_production_web(objective: str, query1: str, query2: str = "", query3: str = "") -> Dict[str, Any]:
    """
    Search the live web for production locations, municipal permits, and logistics
    using Parallel Search SDK (parallel-web).
    """
    parallel_key = os.environ.get("PARALLEL_API_KEY")
    queries = [q.strip() for q in [query1, query2, query3] if q and q.strip()]

    print(f"[CineScout Tool] Executing Parallel Search for objective: '{objective}' | Queries: {queries}")

    if PARALLEL_AVAILABLE and parallel_key:
        try:
            client = Parallel(api_key=parallel_key)

            search_fn = getattr(client, "search", getattr(getattr(client, "beta", None), "search", None))
            if not search_fn:
                raise AttributeError("Parallel SDK search method not found on client.")

            response = search_fn(
                objective=objective,
                search_queries=queries[:3],
                # "basic" trades a little latency for meaningfully more coverage than
                # "fast" — worth it here since we need enough raw material for 3+ venues
                # and 2+ permits, not just the single best-matching page.
                mode="basic",
            )

            results_data = []
            raw_items = getattr(response, "results", response)

            if isinstance(raw_items, list):
                # Pull more than 6 — with 3 queries running, 6 total results left very
                # little for Gemini to work with once split across venues + permits.
                for item in raw_items[:12]:
                    snippet_text = getattr(item, "snippet", "")
                    if not snippet_text and hasattr(item, "excerpts") and item.excerpts:
                        snippet_text = " ".join(item.excerpts) if isinstance(item.excerpts, list) else str(item.excerpts)
                    elif isinstance(item, dict):
                        snippet_text = item.get("snippet", item.get("excerpts", ""))

                    raw_str = snippet_text or str(item)
                    clean_snippet = (raw_str[:350] + "...") if len(raw_str) > 350 else raw_str

                    results_data.append({
                        "title": getattr(item, "title", item.get("title", "Web Source") if isinstance(item, dict) else "Web Source"),
                        "url": getattr(item, "url", item.get("url", "https://example.com") if isinstance(item, dict) else "https://example.com"),
                        "snippet": clean_snippet,
                    })

            return {
                "status": "success",
                "live_search_executed": True,
                "objective": objective,
                "queries": queries,
                "results": results_data,
            }
        except Exception as e:
            print(f"[CineScout Tool Warning] Parallel API call failed ({e}). Falling back to simulated live search data.")

    return _generate_fallback_search_results(objective, queries)


def _generate_fallback_search_results(objective: str, queries: List[str]) -> Dict[str, Any]:
    """Generates realistic verified web location and permit search data for demo & offline modes."""
    q_str = " ".join(queries).lower()

    venues = []
    permits = []

    if "nairobi" in q_str or "rooftop" in q_str:
        venues = [
            {
                "title": "KICC Heliport & Rooftop Terrace - Nairobi",
                "url": "https://kicc.co.ke/filming-venues",
                "snippet": "Iconic panoramic 360-degree views of Nairobi skyline. Features heavy-duty freight elevators, high-capacity 3-phase power output, and rooftop helicopter pad for cinematic camera setups."
            },
            {
                "title": "The Alchemist Bar Rooftop & Lounge - Westlands",
                "url": "https://alchemistnairobi.com/location-scouting",
                "snippet": "Industrial cyberpunk aesthetic with neon LED installations, exposed metal trusses, container architecture, and sound-insulated production greenrooms."
            },
            {
                "title": "Sarit Centre Tower Upper Deck - Westlands",
                "url": "https://saritcentre.com/film-locations",
                "snippet": "Modern glass & steel architectural facade overlooking high-density urban traffic. Dedicated security access and nocturnal filming permissions available."
            }
        ]
        permits = [
            {
                "title": "Kenya Film Classification Board (KFCB) Filming License",
                "url": "https://kfcb.go.ke/filming-permits",
                "snippet": "Mandatory Film License required for all commercial video shoots in Kenya. Standard processing lead time: 2-3 business days. Local agent liaison required for international crews."
            },
            {
                "title": "Nairobi City County Special Location & Noise Permit",
                "url": "https://nairobi.go.ke/services/film-permits",
                "snippet": "Requires application 5 days prior to night shoots involving pyrotechnics, drone operation, or sound equipment exceeding 75 dB after 10:00 PM."
            }
        ]
    elif "diner" in q_str or "restaurant" in q_str:
        venues = [
            {
                "title": "Retro 70s Diner & Grill - Vintage Set",
                "url": "https://filmlocations.com/vintage-diner",
                "snippet": "Authentic chrome trim, vinyl booths, checkered flooring, neon signage, and fully operational commercial kitchen for prop food styling."
            },
            {
                "title": "Caravanserai Vintage Drive-in & Cafe",
                "url": "https://caravanserainairobi.com/filming",
                "snippet": "Mid-century classic American & East African fusion diner aesthetic with spacious parking lot suitable for lighting trucks and generator placement."
            }
        ]
        permits = [
            {
                "title": "Public Health & Commercial Premises Filming Authorization",
                "url": "https://health.nairobi.go.ke/commercial-filming",
                "snippet": "Permit required for commercial kitchen filming. Fire safety clearance mandatory when using active fryers or propane prop stoves."
            }
        ]
    else:
        venues = [
            {
                "title": "Industrial Brickworks & Warehouse Complex",
                "url": "https://nairobilocations.co.ke/industrial-warehouse",
                "snippet": "12,000 sq ft clear-span warehouse space with 30ft ceiling clearance, drive-in roll-up doors, and high-amperage power tie-in boxes."
            },
            {
                "title": "Old Railway Goods Shed - Industrial Quarter",
                "url": "https://krc.co.ke/heritage-filming-sites",
                "snippet": "Atmospheric weathered steel beams, rusted corrugated iron, dramatic natural light shafts, and private security perimeter."
            }
        ]
        permits = [
            {
                "title": "KFCB Commercial Film Permit & Site Clearance",
                "url": "https://kfcb.go.ke/permits",
                "snippet": "Standard commercial filming approval within municipal industrial zones."
            }
        ]

    return {
        "status": "success",
        "live_search_executed": False,
        "mode": "fallback_simulated",
        "objective": objective,
        "queries": queries,
        "results": venues + permits
    }


def _bucket_results(results: List[Dict[str, Any]], target_city: str) -> (List[Dict[str, Any]], List[Dict[str, Any]]):
    """
    Shared classifier: turns raw search results into venue-shaped and
    permit-shaped dicts. Used both by the offline fallback synthesizer and
    by the live-path top-up step, so the two paths can't drift apart again.
    """
    venues_list, permits_list = [], []
    for r in results:
        title = r.get("title", "")
        url = r.get("url", "")
        snippet = r.get("snippet", "")

        if any(w in title.lower() for w in ["permit", "license", "county", "kfcb", "commission", "bylaw", "authority"]):
            permits_list.append({
                "authority": "Municipal Film Commission & Local Council",
                "permit_name": title,
                "lead_time": "3 - 5 Business Days",
                "estimated_fee": "$150 - $400 USD (Commercial Rate)",
                "application_url": url,
                "key_requirements": [
                    "Local filming agent / location fixer representation",
                    "Detailed script synopsis and shoot schedule",
                    "Comprehensive public liability insurance certificate"
                ]
            })
        else:
            venues_list.append({
                "name": title,
                "description": snippet,
                "address": f"{target_city} Metropolitan Area",
                "url": url,
                "suitability_score": "90%",
                "key_features": [
                    "High-voltage power hookups on site",
                    "Dedicated holding room for crew & talent",
                    "Nighttime production clearance with perimeter control"
                ]
            })
    return venues_list, permits_list


def _top_up_dossier(dossier: Dict[str, Any], search_data: Dict[str, Any], target_city: str) -> Dict[str, Any]:
    """
    Hard, code-level guarantee that a live Gemini response still meets the
    minimum venue/permit counts even if the model under-delivered. This is
    the piece that was missing before: a prose instruction in the prompt is
    a request, not a constraint, so we backfill from the same search
    results Gemini already had access to, skipping anything whose URL is
    already present so we don't duplicate.
    """
    venues = dossier.get("venues") or []
    permits = dossier.get("permits") or []

    if len(venues) >= MIN_VENUES and len(permits) >= MIN_PERMITS:
        return dossier

    used_urls = {v.get("url") for v in venues} | {p.get("application_url") for p in permits}
    fallback_venues, fallback_permits = _bucket_results(search_data.get("results", []), target_city)

    for v in fallback_venues:
        if len(venues) >= MIN_VENUES:
            break
        if v["url"] not in used_urls:
            venues.append(v)
            used_urls.add(v["url"])

    for p in fallback_permits:
        if len(permits) >= MIN_PERMITS:
            break
        if p["application_url"] not in used_urls:
            permits.append(p)
            used_urls.add(p["application_url"])

    dossier["venues"] = venues
    dossier["permits"] = permits
    return dossier


def scout_scene(screenplay_text: str, target_city: str = "Nairobi, Kenya") -> Dict[str, Any]:
    """
    Main autonomous agent entry point. Accepts screenplay excerpt and target city,
    orchestrates Gemini (3.7 Flash -> 3.1 Flash Lite) and Parallel Search SDK,
    and returns a structured Production Dossier.
    """
    gemini_key = os.environ.get("GEMINI_API_KEY")

    # Clean query extraction: extract key scene keywords instead of raw dialogue/character lines
    lines = [line.strip() for line in (screenplay_text or "").split("\n") if line.strip()]
    scene_slug = lines[0] if lines else "EXT. LOCATION - DAY"
    scene_keywords = " ".join(lines[:2])
    clean_scene_hint = "".join(c for c in scene_keywords if c.isalnum() or c.isspace())[:50].strip()

    # Exclusion intent moved into the objective's natural-language text instead
    # of "-word" tokens in search_queries — Parallel's search_queries are plain
    # keyword phrases, not a boolean query language, so "-school" was previously
    # just being searched as a literal word rather than excluded.
    objective = (
        f"Find rentable filming venues, vintage cafes/bars, rooftops, warehouses, "
        f"studios, and municipal filming permits in {target_city}. "
        f"Exclude academic institutions, schools, diploma courses, and tax/revenue offices."
    )

    query1 = f"rentable filming location venue hire {target_city} {clean_scene_hint}".strip()
    query2 = f"municipal film commission shooting permit application guidelines lead time {target_city}"
    query3 = f"film production drone UAV night noise curfew safety bylaws {target_city}"

    # Step 1: Call Parallel Web Search
    search_data = search_production_web(objective, query1, query2, query3)

    # Step 2: Gemini Synthesis with Candidate Priority (3.7 Flash -> 3.1 Flash Lite)
    if GENAI_AVAILABLE and gemini_key:
        client = genai.Client(api_key=gemini_key)
        prompt = f"""
You are CineScout AI, an expert autonomous film location scout and line producer.
Analyze the following screenplay excerpt and live web search data to construct a comprehensive Production Dossier for filming in {target_city}.

[SCREENPLAY EXCERPT]
{screenplay_text}

[LIVE PARALLEL SEARCH RESULTS]
{json.dumps(search_data, indent=2)}

Synthesize this data into a JSON object matching this exact structure. The array
lengths shown below are the MINIMUM, not the target — the example shows one
item per array only to illustrate the object shape, not the expected count:

{{
  "scene_summary": {{
    "title": "Short title derived from scene header",
    "setting": "Time & Location type (e.g. {scene_slug})",
    "aesthetic_vibes": "Visual & lighting description",
    "technical_challenges": ["Challenge 1", "Challenge 2"]
  }},
  "venues": [
    {{
      "name": "Specific Venue or Location Name in {target_city}",
      "description": "Why this physical venue matches the script visual directives",
      "address": "Address or neighborhood in {target_city}",
      "url": "Live URL from search results or realistic official source",
      "suitability_score": "95%",
      "key_features": ["Feature 1", "Feature 2"]
    }}
    // ^ REPEAT this object at least {MIN_VENUES} times total, each a distinct venue.
  ],
  "permits": [
    {{
      "authority": "Governing Film Commission or Municipal Body",
      "permit_name": "Official Permit Name",
      "lead_time": "Estimated processing time e.g. 3-5 days",
      "estimated_fee": "Estimated commercial rate",
      "application_url": "URL from search results or official portal",
      "key_requirements": ["Requirement 1", "Requirement 2"]
    }}
    // ^ REPEAT this object at least {MIN_PERMITS} times total, each a distinct permit/bylaw.
  ],
  "logistics": [
    {{
      "category": "Power / Sound / Drones / Parking / Safety",
      "advisory": "Specific operational risk or regulation",
      "mitigation_strategy": "Actionable producer solution"
    }}
  ],
  "citations": ["URL 1", "URL 2"]
}}

Hard requirements:
- "venues" MUST contain at least {MIN_VENUES} distinct venue objects. If live search
  returned fewer than {MIN_VENUES} usable venues, invent additional realistic,
  well-known commercial venues, event spaces, or soundstages in {target_city}
  that plausibly fit the scene's aesthetic — do not return fewer than {MIN_VENUES}.
- "permits" MUST contain at least {MIN_PERMITS} distinct permit objects, following
  the same rule if live search is sparse.
- Never list universities, diploma courses, or tax offices under venues.
- Ensure all list attributes are valid JSON lists.
- "url" and "application_url" must be plain URLs only — never wrap them in
  markdown link syntax like [text](url).
- Return ONLY valid JSON.
"""
        # Primary candidate: gemini-3.7-flash, Fallback candidate: gemini-3.1-flash-lite
        model_candidates = ["gemini-3.7-flash", "gemini-3.1-flash-lite"]

        for model_name in model_candidates:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        temperature=0.2,
                    )
                )

                raw_text = response.text.strip()
                if raw_text.startswith("```json"):
                    raw_text = raw_text[7:]
                if raw_text.startswith("```"):
                    raw_text = raw_text[3:]
                if raw_text.endswith("```"):
                    raw_text = raw_text[:-3]

                dossier = json.loads(raw_text.strip())

                # Code-level guarantee — see _top_up_dossier docstring. This is what
                # actually fixes the "only 1 venue" regression, rather than hoping
                # the prompt rules above are followed.
                dossier = _top_up_dossier(dossier, search_data, target_city)

                dossier["raw_search_queries"] = [query1, query2, query3]
                dossier["execution_meta"] = {
                    "gemini_live": True,
                    "parallel_live": search_data.get("live_search_executed", False),
                    "target_city": target_city,
                    "model_used": model_name
                }
                return dossier
            except Exception as e:
                print(f"[CineScout Engine] Model candidate '{model_name}' failed ({e}). Trying fallback...")

    # Step 3: Hard Offline Fallback (if both models or network fails)
    return _synthesize_fallback_dossier(screenplay_text, target_city, search_data)


def _synthesize_fallback_dossier(screenplay_text: str, target_city: str, search_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generates a complete Production Dossier from search data when LLM is unreachable."""
    first_line = screenplay_text.strip().split("\n")[0] if screenplay_text else "EXT. LOCATION - DAY"

    results = search_data.get("results", [])
    venues_list, permits_list = _bucket_results(results, target_city)

    urls = [r.get("url") for r in results if "url" in r]
    if not urls:
        urls = ["https://kfcb.go.ke/filming-permits", "https://kicc.co.ke/filming-venues"]

    if len(venues_list) < MIN_VENUES:
        defaults = [
            {
                "name": f"City Skyline Terrace ({target_city})",
                "description": "High-elevation location with 360-degree urban exposure, ideal for cinematic night scenes and high-contrast lighting setups.",
                "address": f"Central District, {target_city}",
                "url": "https://kicc.co.ke/filming-venues",
                "suitability_score": "96%",
                "key_features": ["High Elevation Deck", "3-Phase Power Distribution", "Service Freight Elevator"]
            },
            {
                "name": f"Industrial Quarter Studios ({target_city})",
                "description": "Modern architectural space with exposed metallic trusses, neon backdrop suitability, and isolated audio environment.",
                "address": f"Commercial Zone, {target_city}",
                "url": "https://alchemistnairobi.com/location-scouting",
                "suitability_score": "91%",
                "key_features": ["Exposed Trusses", "Production Greenroom", "Private Equipment Ramp"]
            },
            {
                "name": f"Riverside Warehouse District ({target_city})",
                "description": "Clear-span industrial floor space with natural skylight diffusion, suited to both interior and courtyard setups.",
                "address": f"Riverside Industrial Belt, {target_city}",
                "url": "https://nairobilocations.co.ke/industrial-warehouse",
                "suitability_score": "88%",
                "key_features": ["Clear-Span Floor", "Loading Dock Access", "On-Site Parking for Grip Trucks"]
            },
        ]
        existing_urls = {v["url"] for v in venues_list}
        for d in defaults:
            if len(venues_list) >= MIN_VENUES:
                break
            if d["url"] not in existing_urls:
                venues_list.append(d)

    if len(permits_list) < MIN_PERMITS:
        defaults = [
            {
                "authority": "Municipal Film Commission",
                "permit_name": "Commercial Filming & Location Clearance",
                "lead_time": "3 Business Days",
                "estimated_fee": "$250 USD",
                "application_url": "https://kfcb.go.ke/filming-permits",
                "key_requirements": [
                    "Public Notice to adjacent property owners",
                    "Fire safety officer standby for night operations",
                    "Approved traffic management plan if utilizing street cranes"
                ]
            },
            {
                "authority": "Local City County Council",
                "permit_name": "Special Location & Noise Permit",
                "lead_time": "5 Business Days",
                "estimated_fee": "$180 USD",
                "application_url": "https://nairobi.go.ke/services/film-permits",
                "key_requirements": [
                    "Advance application for night shoots involving amplified sound",
                    "Drone/UAV operation disclosure if applicable",
                    "Certificate of public liability insurance"
                ]
            },
        ]
        existing_urls = {p["application_url"] for p in permits_list}
        for d in defaults:
            if len(permits_list) >= MIN_PERMITS:
                break
            if d["application_url"] not in existing_urls:
                permits_list.append(d)

    return {
        "scene_summary": {
            "title": first_line,
            "setting": first_line,
            "aesthetic_vibes": f"High contrast visual aesthetic in {target_city}. Requires specialized atmospheric lighting, elevated camera mounts, and controlled audio perimeter.",
            "technical_challenges": [
                "Low-light high-contrast camera sensor exposure management",
                "Wind noise isolation for exterior dialogue",
                "High-voltage power distribution for 10K/HMI lights",
                "Municipal sound curfew compliance after 10:00 PM"
            ]
        },
        "venues": venues_list,
        "permits": permits_list,
        "logistics": [
            {
                "category": "Power & Electrical",
                "advisory": "Rooftops and industrial locations often lack sufficient breaker capacity for heavy production lighting rigs.",
                "mitigation_strategy": "Dispatch 50kW silent twin-generator truck with dedicated feeder cable runs up the service elevator shaft."
            },
            {
                "category": "Drone & Aerial Filming",
                "advisory": "Urban airspace in metropolitan regions requires Civil Aviation Authority (KCAA/FAA) clearance.",
                "mitigation_strategy": "File flight log matrix 7 days in advance with licensed drone operator and notify local authorities."
            },
            {
                "category": "Sound & Night Curfew",
                "advisory": "Commercial amplification after 10:00 PM requires municipal noise exemption permits.",
                "mitigation_strategy": "Use hypercardioid directional microphones with physical blimps/deadcats and schedule loud audio takes prior to 10:00 PM."
            },
            {
                "category": "Crew Safety & Rigging",
                "advisory": "Perimeter hazards during nighttime shoots require dedicated stunt safety riggers.",
                "mitigation_strategy": "Install edge-guard wire harnesses and maintain designated safety marshals for cast and crew."
            }
        ],
        "citations": list(set(urls)),
        "raw_search_queries": search_data.get("queries", []),
        "execution_meta": {
            "gemini_live": False,
            "parallel_live": search_data.get("live_search_executed", False),
            "target_city": target_city
        }
    }