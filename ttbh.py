import argparse
import json
import os
import random
import time

import pyautogui

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "chest_coords.json")


# ---------------------------------------------------------------------------
# Calibrate
# ---------------------------------------------------------------------------

def calibrate():
    print("=== CALIBRATE RƯƠNG ===")
    print("Di chuột lên RƯƠNG 1 (xanh) rồi nhấn Enter...")
    input()
    x1, y1 = pyautogui.position()
    r1, g1, b1 = pyautogui.pixel(x1, y1)
    print(f"[+] Rương 1: X={x1} Y={y1} | màu RGB=({r1},{g1},{b1})")

    print("Di chuột lên RƯƠNG 2 (nâu) rồi nhấn Enter...")
    input()
    x2, y2 = pyautogui.position()
    r2, g2, b2 = pyautogui.pixel(x2, y2)
    print(f"[+] Rương 2: X={x2} Y={y2} | màu RGB=({r2},{g2},{b2})")

    coords = _load_coords()
    coords["chest1"] = {"x": x1, "y": y1, "color": [r1, g1, b1]}
    coords["chest2"] = {"x": x2, "y": y2, "color": [r2, g2, b2]}
    _save_coords(coords)
    print(f"[+] Đã lưu tọa độ rương vào {CONFIG_FILE}\n")


def calibrate_transfer():
    print("=== CALIBRATE NÚT CHUYỂN ĐỒ ===")
    print("Di chuột lên NÚT CHUYỂN ĐỒ (auto transfer từ túi vào rương) rồi nhấn Enter...")
    input()
    x, y = pyautogui.position()
    print(f"[+] Nút transfer: X={x} Y={y}")

    coords = _load_coords()
    coords["transfer_btn"] = {"x": x, "y": y}
    _save_coords(coords)
    print(f"[+] Đã lưu tọa độ nút transfer vào {CONFIG_FILE}\n")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_coords():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def _save_coords(coords):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(coords, f, indent=2)


def _gauss_delay(mean, std, lo, hi):
    return max(lo, min(hi, random.gauss(mean, std)))


def human_click(x: int, y: int, jitter: int):
    """Click có lệch tọa độ ngẫu nhiên và thời gian di chuột giống người."""
    tx = x + random.randint(-jitter, jitter)
    ty = y + random.randint(-jitter, jitter)
    pyautogui.moveTo(tx, ty, duration=random.uniform(0.2, 0.6))
    # Dừng nhẹ để con trỏ "ổn định" trước khi bấm (nhiều game bỏ qua click quá nhanh)
    time.sleep(random.uniform(0.05, 0.15))
    # Tách nhấn/thả với thời gian giữ nút giống người thật
    pyautogui.mouseDown(tx, ty, button="left")
    time.sleep(random.uniform(0.05, 0.12))
    pyautogui.mouseUp(tx, ty, button="left")
    return tx, ty

def _jitter(val, amount):
    return val + random.randint(-amount, amount)


def _color_match(x, y, expected, tol):
    """True nếu màu pixel tại (x,y) khớp với màu 'expected' trong ngưỡng tol."""
    if not expected:
        return True  # config cũ chưa lưu màu -> click mù như trước
    try:
        r, g, b = pyautogui.pixel(x, y)
    except Exception as e:
        print(f"[!] Không đọc được màu pixel: {e}")
        return True
    er, eg, eb = expected
    return abs(r - er) <= tol and abs(g - eg) <= tol and abs(b - eb) <= tol


# ---------------------------------------------------------------------------
# Transfer items
# ---------------------------------------------------------------------------

def transfer_items(coords, jitter=5):
    if "transfer_btn" not in coords:
        print("[!] Chưa calibrate nút transfer. Chạy: python main.py --calibrate-transfer")
        return False

    btn = coords["transfer_btn"]
    x = _jitter(btn["x"], jitter)
    y = _jitter(btn["y"], jitter)
    pyautogui.click(x, y)
    print(f"[TRANSFER] Click nút chuyển đồ @ {x},{y}")
    return True


def transfer_loop(every, unit, jitter=5):
    coords = _load_coords()
    if "transfer_btn" not in coords:
        print("[!] Chưa calibrate nút transfer. Chạy: python ttbh.py --calibrate-transfer")
        return

    interval = every * (3600 if unit == "h" else 60)
    unit_label = "giờ" if unit == "h" else "phút"
    print(f"\n=== TRANSFER LOOP ===")
    print(f"Chuyển đồ mỗi {every} {unit_label}. Nhấn Ctrl+C để dừng.\n")

    count = 0
    try:
        while True:
            count += 1
            transfer_items(coords, jitter)
            time.sleep(interval)
    except KeyboardInterrupt:
        print(f"\n[!] Dừng sau {count} lần.")


# ---------------------------------------------------------------------------
# Auto click
# ---------------------------------------------------------------------------

def auto_click(mean, std, lo, hi, jitter, break_every, session_max, loop_count, transfer_every, transfer_unit, color_tol):
    coords = _load_coords()

    if "chest1" not in coords or "chest2" not in coords:
        print("[!] Chưa có tọa độ rương. Chạy trước:")
        print("    python ttbh.py --calibrate")
        return

    c1 = coords["chest1"]
    c2 = coords["chest2"]

    has_transfer = "transfer_btn" in coords
    transfer_interval = transfer_every * (3600 if transfer_unit == "h" else 60)

    check_color = "color" in c1 or "color" in c2

    print("\n=== AUTO CLICK ===")
    print(f"Rương 1: ({c1['x']}, {c1['y']})  |  Rương 2: ({c2['x']}, {c2['y']})")
    print(f"Delay: ~{mean}s ± {std}s  (kẹp [{lo}s, {hi}s])")
    if check_color:
        print(f"Nhận diện màu: BẬT (sai số ±{color_tol}/kênh) — chỉ click khi rương xuất hiện")
    else:
        print("Nhận diện màu: TẮT (config chưa lưu màu — chạy lại --calibrate để bật)")
    if has_transfer:
        unit_label = "giờ" if transfer_unit == "h" else "phút"
        print(f"Transfer đồ: mỗi {transfer_every} {unit_label}")
    else:
        print("[!] Chưa calibrate nút transfer — bỏ qua tính năng chuyển đồ")
    print("Nhấn Ctrl+C để dừng.\n")

    session_start = time.time()
    last_transfer = time.time()
    count = 0

    try:
        while loop_count == 0 or count < loop_count:
            now = time.time()

            # Kiểm tra session-max
            if session_max > 0 and (now - session_start) >= session_max * 60:
                print(f"\n[!] Đã đạt session-max {session_max} phút. Dừng.")
                break

            # Kiểm tra transfer đồ
            if has_transfer and (now - last_transfer) >= transfer_interval:
                transfer_items(coords, jitter)
                last_transfer = time.time()
                time.sleep(1.5)  # chờ animation

            # Click rương 1 (chỉ khi màu khớp -> rương đang xuất hiện)
            if _color_match(c1["x"], c1["y"], c1.get("color"), color_tol):
                x1 = _jitter(c1["x"], jitter)
                y1 = _jitter(c1["y"], jitter)
                pyautogui.click(x1, y1)
                print(f"[{count+1}] Click rương 1 @ {x1},{y1}")
                time.sleep(random.uniform(0.4, 1.2))  # nghỉ ngắn giữa 2 rương
            else:
                print(f"[{count+1}] Rương 1 chưa xuất hiện — bỏ qua")

            # Click rương 2 (chỉ khi màu khớp)
            if _color_match(c2["x"], c2["y"], c2.get("color"), color_tol):
                x2 = _jitter(c2["x"], jitter)
                y2 = _jitter(c2["y"], jitter)
                pyautogui.click(x2, y2)
                print(f"[{count+1}] Click rương 2 @ {x2},{y2}")
            else:
                print(f"[{count+1}] Rương 2 chưa xuất hiện — bỏ qua")

            time.sleep(_gauss_delay(mean, std, lo, hi))
            count += 1

            # Nghỉ dài sau mỗi N vòng
            if break_every > 0 and count % break_every == 0:
                rest = random.uniform(180, 480)  # 3–8 phút
                print(f"\n[~] Nghỉ {rest/60:.1f} phút sau {count} vòng...\n")
                time.sleep(rest)

    except KeyboardInterrupt:
        print(f"\n[!] Dừng sau {count} vòng.")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Auto click 2 rương trong game TBH")

    parser.add_argument("--calibrate", action="store_true", help="Lấy tọa độ 2 rương")
    parser.add_argument("--calibrate-transfer", action="store_true", help="Lấy tọa độ nút chuyển đồ")
    parser.add_argument("--transfer-loop", action="store_true", help="Chỉ chuyển đồ định kỳ, không mở rương")

    parser.add_argument("--mean", type=float, default=45.0, help="Delay trung bình giữa các lần click (giây)")
    parser.add_argument("--std", type=float, default=12.0, help="Độ lệch chuẩn của delay (giây)")
    parser.add_argument("--min", type=float, default=30.0, help="Delay tối thiểu (giây)")
    parser.add_argument("--max", type=float, default=90.0, help="Delay tối đa (giây)")
    parser.add_argument("--jitter", type=int, default=5, help="Lệch tọa độ click ngẫu nhiên +/- px")
    parser.add_argument("--break-every", type=int, default=0, help="Nghỉ dài 3-8 phút sau mỗi N vòng (0 = không nghỉ)")
    parser.add_argument("--session-max", type=float, default=0, help="Tự dừng sau X phút online (0 = không giới hạn)")
    parser.add_argument("--count", type=int, default=0, help="Số lần lặp (0 = vô hạn)")
    parser.add_argument("--transfer-every", type=float, default=4.0, help="Chuyển đồ vào rương mỗi X giờ/phút (0 = tắt)")
    parser.add_argument("--transfer-unit", choices=["h", "m"], default="h", help="Đơn vị thời gian cho --transfer-every: h = giờ, m = phút (mặc định: h)")
    parser.add_argument("--color-tol", type=int, default=25, help="Ngưỡng sai số màu mỗi kênh RGB khi nhận diện rương (lớn hơn = dễ khớp hơn)")

    args = parser.parse_args()

    if args.calibrate:
        calibrate()
    elif args.calibrate_transfer:
        calibrate_transfer()
    elif args.transfer_loop:
        transfer_loop(args.transfer_every, args.transfer_unit, args.jitter)
    else:
        auto_click(
            mean=args.mean,
            std=args.std,
            lo=args.min,
            hi=args.max,
            jitter=args.jitter,
            break_every=args.break_every,
            session_max=args.session_max,
            loop_count=args.count,
            transfer_every=args.transfer_every,
            transfer_unit=args.transfer_unit,
            color_tol=args.color_tol,
        )


if __name__ == "__main__":
    main()
