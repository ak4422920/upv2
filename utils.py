import aiohttp

def readable_size(size):
    for unit in ['B','KB','MB','GB','TB']:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} TB"

def is_video_file(filename):
    return any(filename.lower().endswith(ext) for ext in ['.mp4', '.mkv', '.webm', '.mov'])

async def bypass_link(url):
    try:
        api = "https://bypass.pm/bypass2?url="
        async with aiohttp.ClientSession() as session:
            async with session.get(api + url) as resp:
                data = await resp.json()
                return data.get("destination") if data.get("success") else None
    except:
        return None