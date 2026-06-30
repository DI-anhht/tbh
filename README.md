# ttbh

Auto click 2 rương trong game **TBH**. Mô phỏng thao tác giống người thật (delay ngẫu nhiên theo phân phối chuẩn, lệch tọa độ click, nghỉ dài định kỳ) 

## Yêu cầu

- Python >= 3.11
- [`uv`](https://github.com/astral-sh/uv) (khuyến nghị) hoặc `pip`

## Cài đặt

```bash
# Dùng uv
uv sync

# Hoặc dùng pip
pip install pyautogui
```

## Sử dụng

### 1. Hiệu chỉnh tọa độ (chạy lần đầu)

Lấy tọa độ 2 rương trên màn hình và lưu vào `chest_coords.json`:

```bash
python ttbh.py --calibrate
```

Làm theo hướng dẫn: di chuột lên từng rương rồi nhấn `Enter`.

**(Tùy chọn)** Lấy tọa độ nút chuyển đồ từ túi vào rương (dùng cho tính năng `--transfer-every`):

```bash
python ttbh.py --calibrate-transfer
```

### 2. Chạy auto click

```bash
python ttbh.py
```

Nhấn `Ctrl+C` để dừng bất kỳ lúc nào.

## Tùy chọn

| Tham số | Mặc định | Mô tả |
|---|---|---|
| `--calibrate` | – | Lấy tọa độ 2 rương |
| `--calibrate-transfer` | – | Lấy tọa độ nút chuyển đồ từ túi vào rương |
| `--transfer-loop` | – | Chỉ chuyển đồ định kỳ, không mở rương (dùng chung `--transfer-every` + `--transfer-unit`) |
| `--mean` | `45.0` | Delay trung bình giữa các lần click (giây) |
| `--std` | `12.0` | Độ lệch chuẩn của delay (giây) |
| `--min` | `30.0` | Delay tối thiểu (giây, dùng để kẹp) |
| `--max` | `90.0` | Delay tối đa (giây, dùng để kẹp) |
| `--jitter` | `5` | Lệch tọa độ click ngẫu nhiên +/- px |
| `--break-every` | `30` | Nghỉ dài 3-8 phút sau mỗi N vòng (`0` = không nghỉ) |
| `--session-max` | `90.0` | Tự dừng sau X phút online (`0` = không giới hạn) |
| `--count` | `0` | Số lần lặp (`0` = vô hạn) |
| `--transfer-every` | `4.0` | Tự động chuyển đồ từ túi vào rương mỗi X giờ/phút (`0` = tắt) |
| `--transfer-unit` | `h` | Đơn vị cho `--transfer-every`: `h` = giờ, `m` = phút |

### Ví dụ

```bash
# Click nhanh hơn, delay trung bình 20s
python ttbh.py --mean 20 --min 15 --max 40

# Chạy 100 vòng rồi dừng, không nghỉ dài
python ttbh.py --count 100 --break-every 0

# Tự chuyển đồ vào rương mỗi 2 giờ (cần calibrate-transfer trước)
python ttbh.py --transfer-every 2

# Tự chuyển đồ vào rương mỗi 30 phút (kèm mở rương)
python ttbh.py --transfer-every 30 --transfer-unit m

# Chỉ chuyển đồ, không mở rương, mỗi 2 giờ
python ttbh.py --transfer-loop --transfer-every 2

# Chỉ chuyển đồ, không mở rương, mỗi 45 phút
python ttbh.py --transfer-loop --transfer-every 45 --transfer-unit m
```

## Lưu ý

- Tọa độ trong `chest_coords.json` phụ thuộc vào độ phân giải và vị trí cửa sổ game. Đổi màn hình/cửa sổ thì cần `--calibrate` lại.
- Công cụ chỉ dùng cho mục đích học tập/cá nhân.
