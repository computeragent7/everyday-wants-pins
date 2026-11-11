
# Everyday Wants pin maker v3 (Nov 2026; v2 single-product pins + make_roundup): product name big + "See it on Amazon" button.
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
        tl = [t.strip() for t in tags.split(",")]
        # the item must be one of the photo's MAIN subjects (first 4 tags), not a side mention
        if req and not any(any(w in t for w in req) for t in tl[:4]): continue
        if any(b in tags for b in ("baby","child","children","kid","toddler","infant","boy","girl","newborn")): continue
        animals = ("horse","cow","sheep","goat","pig","cattle","deer","bird","wildlife")
        if any(a in tags for a in animals) and not any(a in " ".join(req) for a in animals): continue
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


# ---- pin maker v3 addition (Nov 11 2026): numbered ROUNDUP / gift-guide pins ----
def _shadow_text(d, xy, text, font, fill=(255,255,255)):
    x,y=xy
    for dx,dy in ((1,1),(2,2)): d.text((x+dx,y+dy), text, font=font, fill=(0,0,0))
    d.text((x,y), text, font=font, fill=fill)
def make_roundup(items, label, head, sub, out, cta=None):
    """items: list of 4 or 6 (photo_path, short caption). Numbered grid pin for roundups/gift guides."""
    from PIL import ImageFilter
    setup()
    n = len(items); assert n in (4,6), "use 4 or 6 items"
    img = Image.new("RGB", (W, H), CREAM); d = ImageDraw.Draw(img)
    lab = _font("sans.ttf", 24, 600); foot = _font("sans.ttf", 22, 450)
    y = 56
    d.text((W/2, y), " ".join(label.upper()), font=lab, fill=GREEN, anchor="mt"); y += 50
    hf, hl, hs = _fit(d, head, "serif.ttf", W-120, 84, 56, 2)
    for l in hl: d.text((W/2, y), l, font=hf, fill=INK, anchor="mt"); y += int(hs*1.06)
    if sub:
        sf, sl, ss = _fit(d, sub, "sans.ttf", W-140, 34, 26, 1, 500)
        y += 10; d.text((W/2, y), sl[0], font=sf, fill=MUTED, anchor="mt"); y += int(ss*1.3)
    top = y + 26; bottom = H - 190
    rows = n // 2; gap = 16; cw = (W - 2*50 - gap) // 2; ch = (bottom - top - gap*(rows-1)) // rows
    nf = _font("serif.ttf", 34); cf = _font("sans.ttf", 26, 650)
    for i,(p,cap) in enumerate(items):
        r_, c_ = divmod(i, 2); x0 = 50 + c_*(cw+gap); y0 = top + r_*(ch+gap)
        ph = ImageOps.fit(Image.open(p).convert("RGB"), (cw, ch), centering=(0.5,0.5))
        grad = Image.new("L", (1, ch), 0)
        for yy in range(ch): grad.putpixel((0,yy), int(max(0, (yy-ch*0.55)/(ch*0.45))*190))
        dark = Image.new("RGB", (cw, ch), (0,0,0)); ph = Image.composite(dark, ph, grad.resize((cw, ch)))
        m = Image.new("L", (cw, ch), 0); ImageDraw.Draw(m).rounded_rectangle([0,0,cw,ch], 22, fill=255)
        img.paste(ph, (x0, y0), m)
        d.ellipse([x0+14, y0+14, x0+66, y0+66], fill=CREAM)
        d.text((x0+40, y0+41), str(i+1), font=nf, fill=GREEN, anchor="mm")
        cfit, clines, cs = _fit(d, cap, "sans.ttf", cw-36, 28, 20, 2, 650)
        ty = y0 + ch - 18 - int(cs*1.2)*len(clines)
        for l in clines: _shadow_text(d, (x0+18, ty), l, cfit); ty += int(cs*1.2)
    y = bottom + 38
    _cta(d, W/2, y, cta or f"See all {n} picks →")
    d.text((W/2, H-46), "everyday wants", font=foot, fill=MUTED, anchor="mm")
    img.save(out, "JPEG", quality=88, optimize=True)
    return out
