
# Everyday Wants pin maker. Usage in Composio workbench:
#   import requests; exec(requests.get("https://raw.githubusercontent.com/computeragent7/everyday-wants-pins/main/make_pin.py").text)
#   setup(); photo = pixabay_photo("cozy fall living room", KEY, skip_ids=set())
#   make_pin(photo["path"], "COZY HOME DECOR", "Fall Living Room Ideas on a Budget", "out.jpg", style="A")
import os, requests
from PIL import Image, ImageDraw, ImageFont, ImageOps
RAW = "https://raw.githubusercontent.com/computeragent7/everyday-wants-pins/main/"
W, H = 1000, 1500
CREAM=(247,242,234); INK=(33,37,34); GREEN=(46,74,58); MUTED=(110,112,104)
WORK = "/tmp/pinwork"
def setup():
    os.makedirs(WORK, exist_ok=True)
    for f in ("serif.ttf","sans.ttf"):
        p = os.path.join(WORK, f)
        if not os.path.exists(p):
            r = requests.get(RAW+"fonts/"+f, timeout=60); r.raise_for_status()
            open(p,"wb").write(r.content)
def _font(name, size, wt=None):
    f = ImageFont.truetype(os.path.join(WORK, name), size)
    if wt:
        try: f.set_variation_by_axes([wt])
        except Exception: pass
    return f
def _wrap(d, text, f, maxw):
    lines, cur = [], ""
    for w in text.split():
        t = (cur+" "+w).strip()
        if d.textlength(t, font=f) <= maxw: cur = t
        else:
            if cur: lines.append(cur)
            cur = w
    lines.append(cur); return lines
def _fit_head(d, text, maxw, start, minsize, maxlines=3):
    size = start
    while True:
        f = _font("serif.ttf", size); lines = _wrap(d, text, f, maxw)
        if (len(lines) <= maxlines and all(d.textlength(l,font=f)<=maxw for l in lines)) or size <= minsize:
            return f, lines, size
        size -= 4
def pixabay_photo(query, key, skip_ids=(), orientation="vertical"):
    r = requests.get("https://pixabay.com/api/", params={"key":key,"q":query,"image_type":"photo",
        "orientation":orientation,"safesearch":"true","per_page":20,"order":"popular"}, timeout=60)
    r.raise_for_status()
    for h in r.json().get("hits", []):
        if h["id"] in skip_ids or h.get("imageHeight",0) < 1200: continue
        img = requests.get(h["largeImageURL"], timeout=60); img.raise_for_status()
        p = os.path.join(WORK, f"px_{h['id']}.jpg"); open(p,"wb").write(img.content)
        return {"id": h["id"], "path": p, "page": h.get("pageURL"), "user": h.get("user")}
    return None
def make_pin(photo, label, head, out, style="A"):
    setup()
    src = Image.open(photo).convert("RGB")
    lab = _font("sans.ttf", 24, 600); foot = _font("sans.ttf", 26, 450)
    spaced = " ".join(label.upper())
    if style == "A":
        img = ImageOps.fit(src, (W, H), centering=(0.5, 0.45)); d = ImageDraw.Draw(img)
        cx0, cx1 = 60, W-60; inner = cx1-cx0-80
        hf, lines, size = _fit_head(d, head, inner, 78, 54)
        lh = int(size*1.12)
        card_h = 60 + 30 + 34 + lh*len(lines) + 30 + 4 + 34 + 26 + 50
        y0 = H - 60 - card_h
        d.rounded_rectangle([cx0, y0, cx1, H-60], 36, fill=CREAM)
        y = y0 + 60
        d.text((W/2, y), spaced, font=lab, fill=GREEN, anchor="mt"); y += 64
        for l in lines: d.text((W/2, y), l, font=hf, fill=INK, anchor="mt"); y += lh
        y += 30; d.line([(W/2-50, y), (W/2+50, y)], fill=GREEN, width=4); y += 34
        d.text((W/2, y), "everyday wants  ·  shop the look", font=foot, fill=MUTED, anchor="mt")
    else:
        img = Image.new("RGB", (W, H), CREAM); d = ImageDraw.Draw(img); x = 70; y = 72
        d.text((x, y), spaced, font=lab, fill=GREEN); y += 60
        hf, lines, size = _fit_head(d, head, W-2*x, 96, 64)
        lh = int(size*1.08)
        for l in lines: d.text((x, y), l, font=hf, fill=INK); y += lh
        y += 24; d.text((x, y), "everyday wants  ·  shop the look →", font=foot, fill=MUTED)
        top = y + 60; ph = H - top - 60
        p = ImageOps.fit(src, (W-120, ph), centering=(0.5, 0.5))
        m = Image.new("L", p.size, 0); ImageDraw.Draw(m).rounded_rectangle([0,0,*p.size], 28, fill=255)
        img.paste(p, (60, top), m)
    img.save(out, "JPEG", quality=88, optimize=True)
    return out
