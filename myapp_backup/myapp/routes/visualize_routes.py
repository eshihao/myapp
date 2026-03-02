from flask import Blueprint, request, jsonify
from services.visualization_service import load_npy_for_3d, get_slice_preview
from models import NpyFile
import os

visualize_bp = Blueprint("visualize", __name__)


@visualize_bp.route("/api/visualize/volume", methods=["GET"])
def visualize_volume():
    """
    获取整个 npy 体数据用于前端 3D 渲染
    请求参数:
        file_id: 上传后的 npy 文件 ID
        normalize: 是否归一化 0-1 (可选, 默认 True)
    """
    file_id = request.args.get("file_id", type=int)
    normalize = request.args.get("normalize", default=True, type=lambda x: x.lower() == "true")

    if not file_id:
        return jsonify({"error": "缺少 file_id"}), 400

    npy_file = NpyFile.query.get(file_id)
    if not npy_file or not os.path.exists(npy_file.filepath):
        return jsonify({"error": "文件不存在"}), 404

    result = load_npy_for_3d(os.path.basename(npy_file.filepath), normalize=normalize)
    return jsonify(result)


@visualize_bp.route("/api/visualize/slice", methods=["GET"])
def visualize_slice():
    """
    获取指定 axis 的切片数据
    请求参数:
        file_id: 上传后的 npy 文件 ID
        axis: 0/1/2
        slice_idx: int
    """
    file_id = request.args.get("file_id", type=int)
    axis = request.args.get("axis", default=0, type=int)
    slice_idx = request.args.get("slice_idx", default=0, type=int)

    if not file_id:
        return jsonify({"error": "缺少 file_id"}), 400

    npy_file = NpyFile.query.get(file_id)
    if not npy_file or not os.path.exists(npy_file.filepath):
        return jsonify({"error": "文件不存在"}), 404

    result = get_slice_preview(os.path.basename(npy_file.filepath), axis=axis, slice_idx=slice_idx)
    return jsonify(result)
