
# Everyday Wants pin maker v2 (Nov 2026): product name big + "See it on Amazon" button.
#   import requests; ns={}; exec(requests.get(RAW+"make_pin.py").text, ns); ns["setup"]()
#   photo = ns["pixabay_photo"]("throw blanket sofa", KEY, skip_ids=set(), require=["blanket","throw"])
#   ns["make_pin"](photo["path"], "GIFTS FOR MOM", "Cozy Gift Ideas for Mom", "out.jpg", style="A", product="Caramel Throw Blanket")
import os, requests
from PIL import Image, ImageDraw, ImageFont, ImageOps
RAW = "https://raw.githubusercontent.com/computeragent7/everyday-wants-pins/main/"
W, H = 1000, 1500
CREAM=(247,242,234); INK=(33,37,34); GREEN=(46,74,58); MUTED=(96,98,90)
WORK = "/tmp/pinwork"
def setup():
    os.makedirs(WORK, exist_ok=True)
    for f in ("serif.ttf","sans.ttf"):
        p = os.path.join(WORK, f)
        if not os.path.exists(p):
            r = requests.get(RAW+"fonts/"+f, timeout=60); r.raise_for_status(); open(p,"wb").write(r.content)
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
def _fit(d, text, name, maxw, start, minsize, maxlines, wt=None):
    size = start
    while True:
        f = _font(name, size, wt); lines = _wrap(d, text, f, maxw)
        if (len(lines) <= maxlines and all(d.textlength(l,font=f)<=maxw for l in lines)) or size <= minsize:
            return f, lines, size
        size -= 4
def pixabay_photo(query, key, skip_ids=(), orientation="vertical", require=None):
    """require: list of words; only accept photos whose Pixabay tags contain at least one (so the photo shows the item type)."""
    r = requests.get("https://pixabay.com/api/", params={"key":key,"q":query,"image_type":"photo",
        "orientation":orientation,"safesearch":"true","per_page":40,"order":"popular"}, timeout=60)
    r.raise_for_status()
    req = [w.lower() for w in (require or [])]
    for h in r.json().get("hits", []):
        if h["id"] in skip_ids or h.get("imageHeight",0) < 1200: continue
        tags = h.get("tags","").lower()
        if req and not any(w in tags for w in req): continue
        img = requests.get(h["largeImageURL"], timeout=60); img.raise_for_status()
        p = os.path.join(WORK, f"px_{h['id']}.jpg"); open(p,"wb").write(img.content)
        return {"id": h["id"], "path": p, "page": h.get("pageURL"), "tags": h.get("tags","")}
    return None
def _cta(d, cx, y, text, left=None):
    f = _font("sans.ttf", 32, 650)
    tw = d.textlength(text, font=f); pw, ph = tw+76, 70
    x0 = (cx - pw/2) if left is None else left
    d.rounded_rectangle([x0, y, x0+pw, y+ph], 35, fill=GREEN)
    d.text((x0+pw/2, y+ph/2), text, font=f, fill=CREAM, anchor="mm")
    return y+ph
def make_pin(photo, label, head, out, style="A", product=None, cta="See it on Amazon →"):
    setup()
    src = Image.open(photo).convert("RGB")
    lab = _font("sans.ttf", 24, 600); foot = _font("sans.ttf", 22, 450)
    spaced = " ".join(label.upper())
    main = product or head
    sub = head if product else None
    if style == "A":
        img = ImageOps.fit(src, (W, H), centering=(0.5, 0.4)); d = ImageDraw.Draw(img)
        cx0, cx1 = 50, W-50; inner = cx1-cx0-80
        mf, mlines, ms = _fit(d, main, "serif.ttf", inner, 80, 54, 2)
        mlh = int(ms*1.1)
        if sub: sf, slines, ss = _fit(d, sub, "sans.ttf", inner, 34, 26, 2, 500); slh=int(ss*1.3)
        else: slines, slh = [], 0
        card_h = 52 + 30 + 30 + mlh*len(mlines) + (14 + slh*len(slines) if slines else 0) + 30 + 70 + 26 + 22 + 40
        y0 = H - 50 - card_h
        d.rounded_rectangle([cx0, y0, cx1, H-50], 36, fill=CREAM)
        y = y0 + 52
        d.text((W/2, y), spaced, font=lab, fill=GREEN, anchor="mt"); y += 60
        for l in mlines: d.text((W/2, y), l, font=mf, fill=INK, anchor="mt"); y += mlh
        if slines:
            y += 14
            for l in slines: d.text((W/2, y), l, font=sf, fill=MUTED, anchor="mt"); y += slh
        y += 30
        y = _cta(d, W/2, y, cta) + 26
        d.text((W/2, y), "everyday wants", font=foot, fill=MUTED, anchor="mt")
    else:
        img = Image.new("RGB", (W, H), CREAM); d = ImageDraw.Draw(img); x = 70; y = 70
        d.text((x, y), spaced, font=lab, fill=GREEN); y += 54
        mf, mlines, ms = _fit(d, main, "serif.ttf", W-2*x, 92, 60, 3)
        mlh = int(ms*1.06)
        for l in mlines: d.text((x, y), l, font=mf, fill=INK); y += mlh
        if sub:
            sf, slines, ss = _fit(d, sub, "sans.ttf", W-2*x, 36, 26, 2, 500)
            y += 22
            for l in slines: d.text((x, y), l, font=sf, fill=MUTED); y += int(ss*1.3)
        y += 26
        y = _cta(d, 0, y, cta, left=x) + 40
        top = y; ph = H - top - 90
        p = ImageOps.fit(src, (W-120, ph), centering=(0.5, 0.5))
        m = Image.new("L", p.size, 0); ImageDraw.Draw(m).rounded_rectangle([0,0,*p.size], 28, fill=255)
        img.paste(p, (60, top), m)
        d.text((W/2, H-50), "everyday wants", font=foot, fill=MUTED, anchor="mm")
    img.save(out, "JPEG", quality=88, optimize=True)
    return out
