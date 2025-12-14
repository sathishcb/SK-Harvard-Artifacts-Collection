import aiohttp
import asyncio

async def fetch_page(session, url, params):
    async with session.get(url, params=params) as resp:
        return await resp.json()

async def fetch_harvard(API_KEY, classification):
    base = "https://api.harvardartmuseums.org/object"
    tasks = []

    async with aiohttp.ClientSession() as session:
        for page in range(1, 40):
            params = {
                "apikey": API_KEY,
                "classification": classification,
                "size": 100,
                "page": page
            }
            tasks.append(fetch_page(session, base, params))

        results = await asyncio.gather(*tasks)

    metadata, media, colors = [], [], []

    for res in results:
        for r in res.get("records", []):
            oid = r.get("id")
            if not oid:
                continue

            metadata.append({
                "id": oid, "title": r.get("title"), "culture": r.get("culture"),
                "period": r.get("period"), "century": r.get("century"),
                "medium": r.get("medium"), "dimensions": r.get("dimensions"),
                "description": r.get("description"), "department": r.get("department"),
                "classification": r.get("classification"),
                "accessionyear": r.get("accessionyear"),
                "accessionmethod": r.get("accessionmethod")
            })

            media.append({
                "objectid": oid, "imagecount": r.get("imagecount"),
                "mediacount": r.get("mediacount"), "colorcount": r.get("colorcount"),
                "rank": r.get("rank"), "datebegin": r.get("datebegin"),
                "dateend": r.get("dateend")
            })

            for c in r.get("colors") or []:
                colors.append({
                    "objectid": oid, "color": c.get("color"), "spectrum": c.get("spectrum"),
                    "hue": c.get("hue"), "percent": c.get("percent"), "css3": c.get("css3")
                })

    return metadata[:2500], media[:2500], colors
