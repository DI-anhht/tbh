import argparse
import json
import os
import random
import time

import pyautogui

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "chest_coords.json")


def calibrate():
    print("=== CALIBRATE ===")
    print("Di chuột lên RƯƠNG 1 (xanh) rồi nhấn Enter...")
    input()
    x1, y1 = pyautogui.position()
    print(f"[+] Rương 1: X={x1} Y={y1}")

    print("Di chuột lên RƯƠNG 2 (nâu) rồi nhấn Enter...")
    input()
    x2, y2 = pyautogui.position()
    print(f"[+] Rương 2: X={x2} Y={y2}")

    coords = {
        "chest1": {"x": x1, "y": y1},
        "chest2": {"x": x2, "y": y2},
    }
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(coords, f, indent=2)
    print(f"[+] Đã lưu tọa độ vào {CONFIG_FILE}")
    print("Chạy lại script KHÔNG có --calibrate để auto click.\n")


def human_delay(mean: float, std: float, lo: float, hi: float) -> float:
    """Delay theo phân phối chuẩn (Gaussian), kẹp trong [lo, hi]."""
    return max(lo, min(hi, random.gauss(mean, std)))


def human_click(x: int, y: int, jitter: int):
    """Click có lệch tọa độ ngẫu nhiên và thời gian di chuột giống người."""
    tx = x + random.randint(-jitter, jitter)
    ty = y + random.randint(-jitter, jitter)
    pyautogui.moveTo(tx, ty, duration=random.uniform(0.2, 0.6))
    pyautogui.click()
    return tx, ty


def auto_click(
    mean: float = 45.0,
    std: float = 12.0,
    lo: float = 30.0,
    hi: float = 90.0,
    jitter: int = 5,
    break_every: int = 30,
    session_max: float = 90.0,
    loop_count: int = 0,
):
    if not os.path.exists(CONFIG_FILE):
        print("[!] Chưa có tọa độ. Chạy trước:")
        print("    python main.py --calibrate")
        return

    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        coords = json.load(f)

    c1 = coords["chest1"]
    c2 = coords["chest2"]

    print("\n=== AUTO CLICK ===")
    print(f"Rương 1: {c1['x']}, {c1['y']}")
    print(f"Rương 2: {c2['x']}, {c2['y']}")
    print(f"Delay: gauss mean={mean:.0f}s std={std:.0f}s, clamp [{lo:.0f}-{hi:.0f}]s")
    print(f"Jitter: +/-{jitter}px | Nghỉ dài: mỗi {break_every} vòng" if break_every else f"Jitter: +/-{jitter}px | Không nghỉ dài")
    print(f"Phiên tối đa: {session_max:.0f} phút" if session_max else "Phiên: không giới hạn")
    print(f"Loop: {'vô hạn' if loop_count == 0 else loop_count}")
    print("Nhấn Ctrl+C để dừng.\n")

    start = time.time()
    count = 0
    try:
        while loop_count == 0 or count < loop_count:
            if session_max and (time.time() - start) >= session_max * 60:
                print(f"\n[+] Hết phiên {session_max:.0f} phút ({count} vòng). Tự dừng.")
                break

            tx, ty = human_click(c1["x"], c1["y"], jitter)
            print(f"[{count}] Click rương 1 @ {tx},{ty}")
            time.sleep(random.uniform(0.4, 1.2))

            tx, ty = human_click(c2["x"], c2["y"], jitter)
            print(f"[{count}] Click rương 2 @ {tx},{ty}")

            count += 1

            # Nghỉ dài định kỳ để giống nhịp người thật
            if break_every and count % break_every == 0:
                rest = random.uniform(180, 480)  # 3-8 phút
                print(f"[+] Nghỉ dài {rest / 60:.1f} phút sau {count} vòng...")
                time.sleep(rest)
                continue

            wait = human_delay(mean, std, lo, hi)
            print(f"[+] Chờ {wait:.1f}s rồi click tiếp...")
            time.sleep(wait)
    except KeyboardInterrupt:
        print("\n[!] Dừng auto click.")


def main():
    parser = argparse.ArgumentParser(description="Auto click 2 rương trong game TBH")
    parser.add_argument("--calibrate", action="store_true", help="Lấy tọa độ 2 rương")
    parser.add_argument("--mean", type=float, default=45.0, help="Delay trung bình giữa các lần click (giây)")
    parser.add_argument("--std", type=float, default=12.0, help="Độ lệch chuẩn của delay (giây)")
    parser.add_argument("--min", type=float, default=30.0, help="Delay tối thiểu (giây, dùng để kẹp)")
    parser.add_argument("--max", type=float, default=90.0, help="Delay tối đa (giây, dùng để kẹp)")
    parser.add_argument("--jitter", type=int, default=5, help="Lệch tọa độ click ngẫu nhiên +/- px")
    parser.add_argument("--break-every", type=int, default=30, help="Nghỉ dài 3-8 phút sau mỗi N vòng (0 = không nghỉ)")
    parser.add_argument("--session-max", type=float, default=90.0, help="Tự dừng sau X phút online (0 = không giới hạn)")
    parser.add_argument("--count", type=int, default=0, help="Số lần lặp (0 = vô hạn)")
    args = parser.parse_args()

    if args.calibrate:
        calibrate()
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
        )


if __name__ == "__main__":
    main()
