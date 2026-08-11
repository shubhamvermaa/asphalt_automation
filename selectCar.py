"""Select Car OCR & Validation Module"""
import os, sys, time, ctypes
from typing import Tuple, Dict, Optional, Union
import cv2, numpy as np, pyautogui, winocr
from PIL import Image, ImageDraw, ImageFont, ImageGrab

try: ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    try: ctypes.windll.user32.SetProcessDPIAware()
    except Exception: pass


TOP_LEFT, BOTTOM_RIGHT = (1367, 209), (1720, 283)
CAR_TYPE_TOP_LEFT, CAR_TYPE_BOTTOM_RIGHT = (1724, 207), (1804, 286)
REFILL_COORD = (1811, 1029)
rank_bbox = (TOP_LEFT[0], TOP_LEFT[1], BOTTOM_RIGHT[0], BOTTOM_RIGHT[1])
type_bbox = (CAR_TYPE_TOP_LEFT[0], CAR_TYPE_TOP_LEFT[1], CAR_TYPE_BOTTOM_RIGHT[0], CAR_TYPE_BOTTOM_RIGHT[1])



SLANTED_TEMPLATES: Dict[str, np.ndarray] = {}
_font = None
for _fn in ['arialbd.ttf', 'arial.ttf', 'impact.ttf', 'calibrib.ttf']:
    try:
        _font = ImageFont.truetype(_fn, 65)
        break
    except Exception: pass

for _d in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '/']:
    _img = Image.new('L', (120, 120), 255)
    _draw = ImageDraw.Draw(_img)
    if _font: _draw.text((25, 10), _d, fill=0, font=_font)
    else: _draw.text((25, 10), _d, fill=0)
    _, _th = cv2.threshold(np.array(_img), 140, 255, cv2.THRESH_BINARY_INV)
    _sl = cv2.warpAffine(_th, np.float32([[1, -0.30, 25], [0, 1, 0]]), (120, 120), borderValue=0)
    _cnt, _ = cv2.findContours(_sl, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if _cnt:
        bx, by, bw, bh = cv2.boundingRect(_cnt[0])
        SLANTED_TEMPLATES[_d] = cv2.resize(_sl[by:by+bh, bx:bx+bw], (40, 60))

def move_left_car(delay: float = 0.15):
    pyautogui.press('a')
    if delay > 0: time.sleep(delay)

def move_right_car(delay: float = 0.15):
    pyautogui.press('d')
    if delay > 0: time.sleep(delay)


def get_dynamic_car_rois(wide_crop: Optional[Image.Image] = None) -> Tuple[Tuple[int, int, int, int], Tuple[int, int, int, int]]:
    def_type = (CAR_TYPE_TOP_LEFT[0], CAR_TYPE_TOP_LEFT[1], CAR_TYPE_BOTTOM_RIGHT[0], CAR_TYPE_BOTTOM_RIGHT[1])
    def_rank = (TOP_LEFT[0], TOP_LEFT[1], BOTTOM_RIGHT[0], BOTTOM_RIGHT[1])
    if wide_crop is None:
        try: wide_crop = ImageGrab.grab(bbox=(1200, 180, 1850, 320))
        except Exception as e: return def_type, def_rank
    gray = cv2.cvtColor(cv2.cvtColor(np.array(wide_crop.convert('RGB')), cv2.COLOR_RGB2BGR), cv2.COLOR_BGR2GRAY)
    _, th = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY)
    cnts, _ = cv2.findContours(th, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for c in cnts:
        bx, by, bw, bh = cv2.boundingRect(c)
        if 50 <= bw <= 100 and 50 <= bh <= 100 and bx > 300 and by < 80:
            x1, y1 = 1200 + bx, 180 + by
            return (x1, y1, x1 + bw, y1 + bh), (x1 - 360, y1, x1, y1 + bh)
    return def_type, def_rank

def run_ocr_on_pil_image(img: Image.Image, lang: str = "en") -> str:
    try:
        res = winocr.recognize_pil_sync(img, lang=lang)
        txt = res.get("text", "") if isinstance(res, dict) else getattr(res, "text", "")
        if txt: return txt.strip()
    except Exception: pass
    try:
        import pytesseract
        return pytesseract.image_to_string(img).strip()
    except Exception: return ""

def match_slanted_digit(char_mask: np.ndarray) -> str:
    cnts_l, hrc_l = cv2.findContours(char_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    if not cnts_l or hrc_l is None: return '?'
    l_max = np.argmax([cv2.contourArea(c) for c in cnts_l])
    cx, cy, cw, ch = cv2.boundingRect(cnts_l[l_max])
    aspect = cw / float(max(1, ch))
    holes = [cv2.moments(cnts_l[i])["m01"] / cv2.moments(cnts_l[i])["m00"] for i in range(len(cnts_l)) if hrc_l[0][i][3] == l_max and cv2.moments(cnts_l[i])["m00"] > 0]
    num_holes = len(holes)
    if num_holes == 0 and aspect < 0.32: return '1'
    if num_holes == 0 and aspect < 0.45 and (ch > 1.7 * cw):
        sub = char_mask[cy:cy+ch, cx:cx+cw]
        tr = np.mean(sub[:int(ch*0.4), int(cw*0.5):] > 0)
        bl = np.mean(sub[int(ch*0.6):, :int(cw*0.5)] > 0)
        if tr > 0.15 and bl > 0.15: return '/'
    hole_rel_y = (holes[0] - cy) / float(max(1, ch)) if num_holes == 1 else -1
    resized = cv2.resize(char_mask[cy:cy+ch, cx:cx+cw], (40, 60))
    best, max_c = '?', -1
    for d, tmpl in SLANTED_TEMPLATES.items():
        if (num_holes >= 2 and d != '8') or (num_holes < 2 and d == '8'): continue
        if num_holes == 1:
            if (hole_rel_y > 0.55 and d != '6') or (hole_rel_y < 0.38 and d not in ['9', '4']) or (0.38 <= hole_rel_y <= 0.55 and d in ['6', '9']): continue
        if num_holes == 0 and d in ['0', '6', '8', '9']: continue
        score = cv2.matchTemplate(resized, tmpl, cv2.TM_CCOEFF_NORMED)[0][0]
        if score > max_c: max_c, best = score, d
    return best if max_c >= 0.58 else '?'



def unslant_image(pil_img: Image.Image, shear_factor: float = 0.28) -> Image.Image:
    try:
        arr = np.array(pil_img.convert('RGB'))
        h, w, _ = arr.shape
        M = np.float32([[1, shear_factor, 0], [0, 1, 0]])
        unslanted = cv2.warpAffine(arr, M, (int(w + h * shear_factor), h), borderMode=cv2.BORDER_REPLICATE)
        return Image.fromarray(unslanted)
    except Exception: return pil_img

def extract_rank_from_ocr_res(ocr_str: str, require_slash: bool = False) -> str:
    if not ocr_str: return ""
    txt = str(ocr_str)
    for word in txt.replace("\n", " ").split():
        if "/" in word:
            f = filter_rank_text(word)
            if f and len(f) == 4 and 1000 <= int(f) <= 6000:
                return f
    if not require_slash:
        f_gen = filter_rank_text(txt)
        if f_gen and len(f_gen) == 4 and 1000 <= int(f_gen) <= 6000:
            return f_gen
    return ""

def get_rank_via_winocr(crop_img: Image.Image) -> str:
    w, h = crop_img.size
    left_crop = crop_img.crop((0, 0, int(w * 0.82), h))
    unslanted_left = unslant_image(left_crop, 0.28)
    up_left = unslanted_left.resize((unslanted_left.width * 3, unslanted_left.height * 3), Image.BICUBIC)
    raw_left = run_ocr_on_pil_image(up_left)
    r_left = extract_rank_from_ocr_res(raw_left)
    if r_left: return r_left

    unslanted = unslant_image(crop_img, 0.28)
    up_unslanted = unslanted.resize((unslanted.width * 3, unslanted.height * 3), Image.BICUBIC)
    raw1 = run_ocr_on_pil_image(up_unslanted)
    r1 = extract_rank_from_ocr_res(raw1, require_slash=True)
    if r1: return r1

    up_left2 = left_crop.resize((left_crop.width * 2, left_crop.height * 2), Image.BICUBIC)
    raw_left2 = run_ocr_on_pil_image(up_left2)
    r_left2 = extract_rank_from_ocr_res(raw_left2)
    if r_left2: return r_left2

    gray = cv2.cvtColor(cv2.cvtColor(np.array(unslanted_left.convert('RGB')), cv2.COLOR_RGB2BGR), cv2.COLOR_BGR2GRAY)
    th_mode = cv2.THRESH_BINARY_INV if gray.mean() > 128 else cv2.THRESH_BINARY
    _, thresh = cv2.threshold(gray, 160, 255, th_mode)
    raw4 = run_ocr_on_pil_image(Image.fromarray(thresh))
    r4 = extract_rank_from_ocr_res(raw4)
    if r4: return r4

    return ""




def get_selected_car_text(top_left: Optional[tuple] = None, bottom_right: Optional[tuple] = None) -> str:
    bbox = rank_bbox if (top_left is None or bottom_right is None) else (top_left[0], top_left[1], bottom_right[0], bottom_right[1])
    try:
        # Tier 1: Target Rank Box Crop (Isolates car rank 3909/3921)
        crop = ImageGrab.grab(bbox=bbox)
        r_crop = get_rank_via_winocr(crop)
        if r_crop: return r_crop

        # Tier 2: Template Matching on Target Rank Box
        gray = cv2.cvtColor(cv2.cvtColor(np.array(crop.convert('RGB')), cv2.COLOR_RGB2BGR), cv2.COLOR_BGR2GRAY)
        th_mode = cv2.THRESH_BINARY_INV if gray.mean() > 128 else cv2.THRESH_BINARY
        _, thresh = cv2.threshold(gray, 180, 255, th_mode)
        cnts, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        h, w = thresh.shape
        boxes = [cv2.boundingRect(c) for c in cnts if 10 <= cv2.boundingRect(c)[3] <= h and 2 <= cv2.boundingRect(c)[2] <= w * 0.35]
        
        clean = ""
        if boxes:
            y_centers = [b[1] + b[3]/2.0 for b in boxes]
            main_y = max(set(y_centers), key=lambda yc: sum(1 for y in y_centers if abs(y - yc) < 25))
            line_boxes = [b for b in boxes if abs((b[1] + b[3]/2.0) - main_y) < 25 and b[3] >= 10]
            line_boxes.sort(key=lambda b: b[0])
            chars = [match_slanted_digit(thresh[max(0, by-3):min(thresh.shape[0], by+bh+3), max(0, bx-3):min(thresh.shape[1], bx+bw+3)]) for bx, by, bw, bh in line_boxes]
            res = "".join(c for c in chars if c != '?')
            clean = filter_rank_text(res)
            if clean and len(clean) == 4 and 1000 <= int(clean) <= 6000:
                return clean

        # Tier 3: Wide Crop Fallback
        try:
            wide_crop = ImageGrab.grab(bbox=(1200, 180, 1850, 320))
            r_wide = get_rank_via_winocr(wide_crop)
            if r_wide: return r_wide
        except Exception: pass

        return clean if clean else ""
    except Exception: return ""








def classify_car_type_by_contours(crop: Image.Image) -> str:
    try:
        gray = cv2.cvtColor(cv2.cvtColor(np.array(crop.convert('RGB')), cv2.COLOR_RGB2BGR), cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 120, 255, cv2.THRESH_BINARY_INV)
        cnts, hrc = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        if not cnts or hrc is None: return ""
        l_max = np.argmax([cv2.contourArea(c) for c in cnts])
        by, bh = cv2.boundingRect(cnts[l_max])[1], cv2.boundingRect(cnts[l_max])[3]
        holes = [cv2.moments(cnts[i])["m01"] / cv2.moments(cnts[i])["m00"] for i in range(len(cnts)) if hrc[0][i][3] == l_max and cv2.moments(cnts[i])["m00"] > 0]
        if len(holes) >= 2: return "B"
        if len(holes) == 1: return "A" if (holes[0] - by) / float(max(1, bh)) < 0.52 else "D"
        bx, bw = cv2.boundingRect(cnts[l_max])[0], cv2.boundingRect(cnts[l_max])[2]
        return "S" if np.mean(thresh[by+int(bh*0.35):by+int(bh*0.65), bx+int(bw*0.5):bx+bw] > 0) > 0.15 else "C"
    except Exception: return ""

def get_car_type_ocr(top_left: Optional[tuple] = None, bottom_right: Optional[tuple] = None) -> str:
    bbox = type_bbox if (top_left is None or bottom_right is None) else (top_left[0], top_left[1], bottom_right[0], bottom_right[1])
    try:
        crop = ImageGrab.grab(bbox=bbox)
        let = classify_car_type_by_contours(crop)
        if let: return let
        raw = run_ocr_on_pil_image(crop)
        return next((c for c in raw.upper() if c in ["S", "A", "B", "C", "D"]), raw)
    except Exception: return ""

def get_refill_pixel_color(x: int = 1811, y: int = 1029) -> str:
    try:
        user32 = ctypes.windll.user32
        gdi32 = ctypes.windll.gdi32
        hdc = user32.GetDC(0)
        rgb_int = gdi32.GetPixel(hdc, x, y)
        user32.ReleaseDC(0, hdc)
        if rgb_int != -1 and rgb_int != 0xFFFFFFFF:
            r = rgb_int & 0xFF
            g = (rgb_int >> 8) & 0xFF
            b = (rgb_int >> 16) & 0xFF
            return f"#{r:02X}{g:02X}{b:02X}"
    except Exception: pass
    try:
        r, g, b = pyautogui.pixel(x, y)
        return f"#{r:02X}{g:02X}{b:02X}"
    except Exception: pass
def get_refill_text(*args, **kwargs) -> str:
    return get_refill_pixel_color(1811, 1029)

def is_gold_yellow_fuel_color(hex_col: str) -> bool:

    if not hex_col or not hex_col.startswith('#') or len(hex_col) != 7:
        return False
    try:
        r = int(hex_col[1:3], 16)
        g = int(hex_col[3:5], 16)
        b = int(hex_col[5:7], 16)
        return (r >= 170) and (g >= 140) and (b <= 140) and ((r - b) >= 40)
    except Exception: return False

def is_car_refilling(*args, **kwargs) -> bool:
    hex_col = get_refill_pixel_color(1811, 1029)
    has_fuel = is_gold_yellow_fuel_color(hex_col)
    return not has_fuel










def filter_rank_text(raw_ocr_str: str) -> str:
    if not raw_ocr_str: return ""
    txt = raw_ocr_str.upper().replace("RANK", "").replace("BANK", "").split("/")[0].replace(",", "").replace(".", "").strip()
    digits = "".join(c for c in txt if c.isdigit())
    if len(digits) > 4:
        if digits[0] in ['8', '9'] and len(digits) == 5:
            digits = digits[1:]
        else:
            digits = digits[:4]
    return digits


def parse_current_rank_number(rank_ocr_str: str) -> int:
    f = filter_rank_text(rank_ocr_str)
    return int(f) if f and f.isdigit() else 0

def get_stabilized_refill_status(samples_count: int = 10, sample_delay: float = 0.015, top_left: Optional[tuple] = None, bottom_right: Optional[tuple] = None) -> bool:
    from collections import Counter
    samples = []
    for _ in range(samples_count):
        samples.append(is_car_refilling(top_left=top_left, bottom_right=bottom_right))
        time.sleep(sample_delay)
    return Counter(samples).most_common(1)[0][0]

def is_car_valid(car_class: Optional[str] = None, rank_text_or_val: Union[str, int, float, None] = None, is_refilling_val: Optional[bool] = None, target_class: str = "B", minRank: int = 3300, allow_refilling: bool = False, verbose: bool = False, **kwargs) -> bool:
    target_class = kwargs.get("class", target_class)
    minRank = kwargs.get("min_rank", minRank)
    if car_class is None: car_class = get_car_type_ocr()
    if is_refilling_val is None: is_refilling_val = get_stabilized_refill_status()
    cur_rank = int(rank_text_or_val) if isinstance(rank_text_or_val, (int, float)) else parse_current_rank_number(get_stabilized_car_rank() if rank_text_or_val is None else str(rank_text_or_val))
    return car_class.upper() == target_class.upper() and cur_rank >= minRank and is_refilling_val == allow_refilling

def get_stabilized_car_rank(samples_count: int = 10, sample_delay: float = 0.015, top_left: Optional[tuple] = None, bottom_right: Optional[tuple] = None) -> str:
    from collections import Counter
    samples = []
    for _ in range(samples_count):
        txt = get_selected_car_text(top_left=top_left, bottom_right=bottom_right)
        if txt and len(txt) == 4 and txt.isdigit() and int(txt) >= 1000:
            samples.append(txt)
        time.sleep(sample_delay)
    
    if not samples:
        return get_selected_car_text(top_left=top_left, bottom_right=bottom_right)
    
    counts = Counter(samples)
    most_common = counts.most_common(1)[0][0]
    return most_common

def select_valid_car(target_class: str = "B", minRank: int = 3300, max_attempts: int = 100, allow_refilling: bool = False, **kwargs) -> bool:
    target_class = kwargs.get("class", target_class)
    minRank = kwargs.get("min_rank", minRank)
    allow_refilling = kwargs.get("allowRefilling", kwargs.get("allow_refill", allow_refilling))
    print(f"Searching for valid car (Class {target_class}, Rank >= {minRank})...")
    type_bbox, rank_bbox = get_dynamic_car_rois()
    for step in range(1, max_attempts + 1):
        type_ocr = get_car_type_ocr(top_left=(type_bbox[0], type_bbox[1]), bottom_right=(type_bbox[2], type_bbox[3]))
        if not type_ocr or type_ocr.upper() != target_class.upper():
            move_right_car(delay=0.15); time.sleep(0.10); continue
        
        # 10-sample Majority Voting for maximum OCR stability
        rank_str = get_stabilized_car_rank(samples_count=10, sample_delay=0.015, top_left=(rank_bbox[0], rank_bbox[1]), bottom_right=(rank_bbox[2], rank_bbox[3]))
        cur_rank = parse_current_rank_number(rank_str)
        
        if cur_rank < minRank:
            print(f"Car #{step}: Class {type_ocr}, Rank {cur_rank} (< {minRank}) -> Skipping...")
            move_right_car(delay=0.15); time.sleep(0.10); continue
        
        refilling = get_stabilized_refill_status(samples_count=10, sample_delay=0.015)
        ref_hex = get_refill_pixel_color()
        ref_fmt = format_color_for_terminal(ref_hex)
        if refilling and not allow_refilling:
            print(f"Car #{step}: Class {type_ocr}, Rank {cur_rank}, Color={ref_fmt}, Refilling=True -> Skipping...")
            move_right_car(delay=0.15); time.sleep(0.10); continue

        
        print(f"-> Selected Car #{step}: Class {type_ocr}, Rank {cur_rank}, Color={ref_fmt}, Refilling={refilling} -> VALID!")
        return True


    
    print(f"No valid car found after {max_attempts} attempts.")
    return False


def inspect_wide_ocr(top_left=(1200, 180), bottom_right=(1850, 320)):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    try:
        t_box, r_box = get_dynamic_car_rois()
        ImageGrab.grab(bbox=r_box).save(os.path.join(script_dir, "debug_crop_rank.png"))
        ImageGrab.grab(bbox=t_box).save(os.path.join(script_dir, "debug_crop_car_type.png"))
        wide = ImageGrab.grab(bbox=(top_left[0], top_left[1], bottom_right[0], bottom_right[1]))
        wide.save(os.path.join(script_dir, "debug_crop_wide.png"))
        res = winocr.recognize_pil_sync(wide, lang="en")
        lines = res.get("lines", []) if isinstance(res, dict) else getattr(res, "lines", [])
        print("\n--- Wide Region Text Search ---")
        for line in lines:
            for w in (line.get("words", []) if isinstance(line, dict) else getattr(line, "words", [])):
                wt = w.get("text", "") if isinstance(w, dict) else getattr(w, "text", "")
                r = w.get("bounding_rect", {}) if isinstance(w, dict) else getattr(w, "bounding_rect", {})
                rx = r.get("x", 0) if isinstance(r, dict) else getattr(r, "x", 0)
                ry = r.get("y", 0) if isinstance(r, dict) else getattr(r, "y", 0)
                print(f"Found '{wt}' at Screen (X={top_left[0] + rx}, Y={top_left[1] + ry})")
        print("-------------------------------\n")
    except Exception as e: print(f"Wide inspection error: {e}")

def format_color_for_terminal(hex_code: str) -> str:
    if not hex_code or not hex_code.startswith('#') or len(hex_code) != 7:
        return hex_code
    try:
        r = int(hex_code[1:3], 16)
        g = int(hex_code[3:5], 16)
        b = int(hex_code[5:7], 16)
        name = "Dark Gray"
        if r > 180 and g > 180 and b < 100: name = "Yellow/Gold"
        elif g > 150 and b > 150 and r < 120: name = "Cyan"
        elif g > 150 and r < 150 and b < 150: name = "Green"
        elif r > 180 and g < 150: name = "Red/Orange"
        elif r > 150 and g > 150 and b > 150: name = "Bright White"
        elif (r + g + b) > 180: name = "Vibrant Color"
        try: ctypes.windll.kernel32.SetConsoleMode(ctypes.windll.kernel32.GetStdHandle(-11), 7)
        except Exception: pass
        swatch = f"\033[48;2;{r};{g};{b}m  \033[0m"
        text_colored = f"\033[38;2;{r};{g};{b}m{hex_code} ({name})\033[0m"
        return f"{swatch} {text_colored}"
    except Exception: return hex_code

if __name__ == "__main__":
    t_box, r_box = get_dynamic_car_rois()
    print(f"Target Regions: Rank={r_box}, CarType={t_box}, RefillCoord={REFILL_COORD}")

    time.sleep(2)
    r_ocr, c_ocr, ref_txt, ref_stat = get_selected_car_text(), get_car_type_ocr(), get_refill_text(), is_car_refilling()
    ref_fmt = format_color_for_terminal(ref_txt)
    print(f"OCR: Rank='{r_ocr}', Class='{c_ocr}', Refill='{ref_fmt}' ({ref_stat})")
    print(f"Valid: {is_car_valid(c_ocr, r_ocr, ref_stat)}")
    inspect_wide_ocr()

