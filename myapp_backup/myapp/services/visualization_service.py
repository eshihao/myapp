import os
import numpy as np

from config import Config


# =============================
# 1. 基础 slice 生成 (可选)
# =============================
def generate_slice(image_path: str, slice_idx: int, save_dir: str) -> str:
    """
    生成单张切片 png，兼容旧前端需求
    """
    import matplotlib.pyplot as plt

    image = np.load(image_path)  # 假设 [C, D, H, W] 或 [D,H,W]
    if image.ndim == 4:  # [1, D, H, W]
        image = image[0]

    slice_img = image[slice_idx]

    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, f"slice_{slice_idx}.png")

    plt.imshow(slice_img, cmap="gray")
    plt.axis("off")
    plt.savefig(save_path, bbox_inches="tight")
    plt.close()

    return save_path


# =============================
# 2. 前端可拖拽的 3D npy 数据接口
# =============================
def load_npy_for_3d(npy_filename: str, normalize: bool = True) -> dict:
    """
    读取 npy 文件，并返回前端可直接渲染的体数据

    返回结构:
    {
        "shape": [D, H, W],
        "dtype": "float32",
        "volume": list  # 或者 list of list... (前端可以直接用)
    }
    """
    npy_path = os.path.join(Config.UPLOAD_DIR, npy_filename)
    if not os.path.exists(npy_path):
        return {"error": "File not found"}

    data = np.load(npy_path)  # [C,D,H,W] or [D,H,W]
    if data.ndim == 4:
        data = data[0]

    if normalize:
        data_min = float(data.min())
        data_max = float(data.max())
        if data_max - data_min > 1e-6:
            data = (data - data_min) / (data_max - data_min)
        else:
            data = np.zeros_like(data)

    return {
        "shape": data.shape,
        "dtype": str(data.dtype),
        "volume": data.tolist()  # 转成 list 给前端
    }


# =============================
# 3. 快速 slice preview 接口
# =============================
def get_slice_preview(npy_filename: str, axis: int = 0, slice_idx: int = 0):
    """
    返回指定 axis 和 slice_idx 的切片数据，前端可直接渲染
    """
    npy_path = os.path.join(Config.UPLOAD_DIR, npy_filename)
    if not os.path.exists(npy_path):
        return {"error": "File not found"}

    data = np.load(npy_path)
    if data.ndim == 4:  # [C,D,H,W]
        data = data[0]

    if axis == 0:
        slice_data = data[slice_idx, :, :]
    elif axis == 1:
        slice_data = data[:, slice_idx, :]
    elif axis == 2:
        slice_data = data[:, :, slice_idx]
    else:
        return {"error": "Invalid axis"}

    # normalize 0-1
    min_val, max_val = float(slice_data.min()), float(slice_data.max())
    slice_norm = (slice_data - min_val) / (max_val - min_val + 1e-8)

    return {
        "shape": slice_norm.shape,
        "data": slice_norm.tolist()
    }
