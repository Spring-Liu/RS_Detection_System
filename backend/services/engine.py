from ultralytics import YOLO
from sahi import AutoDetectionModel
from sahi.predict import get_sliced_prediction
from sahi.utils.cv import visualize_object_predictions
import numpy as np
import cv2
import os
from config import DEVICE

class DetectionEngine:
    def __init__(self):
        self.device = DEVICE
        # 简单的内存缓存，防止每次请求都重新加载模型
        # Key: "category/model_name", Value: YOLO model object
        self.loaded_models = {} 

    def _get_or_load_model(self, category, model_name):
        """
        内部方法：根据分类和名称获取模型实例
        实现简单的缓存机制，避免重复读取磁盘
        """
        # 1. 构造文件路径
        base_dir = os.path.join("weights", category)
        model_path = os.path.join(base_dir, model_name)

        # 2. 检查文件是否存在
        if not os.path.exists(model_path):
            # 容错：有些时候文件名可能带路径，只取文件名再试一次
            model_path = os.path.join(base_dir, os.path.basename(model_name))
            if not os.path.exists(model_path):
                raise ValueError(f"❌ 模型文件未找到: {model_path} (Category: {category})")

        # 3. 检查缓存
        cache_key = f"{category}/{model_name}"
        if cache_key in self.loaded_models:
            return self.loaded_models[cache_key], model_path

        # 4. 显存管理 (简单策略：如果加载超过 3 个模型，就清空旧的，防止显存爆炸)
        if len(self.loaded_models) >= 3:
            print("⚠️ 显存保护：清空旧模型缓存...")
            self.loaded_models.clear()

        # 5. 加载新模型
        print(f"📥 正在加载模型到显存: {cache_key}...")
        try:
            model = YOLO(model_path)
            self.loaded_models[cache_key] = model
            return model, model_path
        except Exception as e:
            raise RuntimeError(f"模型加载失败: {e}")

    def run_inference(self, pil_image, model_name, category, conf, use_sahi):
        """
        统一推理入口
        :param category: 'aerial' 或 'sar'
        """
        # 1. 获取模型实例和路径
        yolo_model, model_path = self._get_or_load_model(category, model_name)
        
        stats = {}
        final_image_bgr = None
        mode_used = "Unknown"

        # 2. SAHI 切片推理逻辑
        if use_sahi:
             # ultralytics 的 engine可以用 'yolov8' 兼容加载 RT-DETR
             sahi_model = AutoDetectionModel.from_pretrained(
                model_type='yolov8', 
                model_path=model_path, #  使用动态获取的路径
                confidence_threshold=conf,
                device=self.device
            )
             
             result = get_sliced_prediction(
                pil_image, sahi_model, 
                slice_height=640, slice_width=640,
                overlap_height_ratio=0.2, overlap_width_ratio=0.2
            )
             
             # 统计结果
             object_prediction_list = result.object_prediction_list
             for obj in object_prediction_list:
                name = obj.category.name
                stats[name] = stats.get(name, 0) + 1
             
             # 绘图
             vis_res = visualize_object_predictions(np.array(pil_image), object_prediction_list)
             final_image_bgr = cv2.cvtColor(vis_res['image'], cv2.COLOR_RGB2BGR)
             mode_used = f"SAHI ({category}/{model_name})"

        # 3. 普通 YOLO/RT-DETR 推理逻辑
        else:
            img_np = np.array(pil_image)
            # 使用加载好的 yolo_model
            results = yolo_model.predict(source=img_np, conf=conf, device=self.device, save=False)
            
            final_image_bgr = results[0].plot()
            boxes = results[0].boxes
            
            if len(boxes) > 0:
                names = yolo_model.names
                cls_ids = boxes.cls.cpu().numpy()
                unique, counts = np.unique(cls_ids, return_counts=True)
                stats = {names[int(u)]: int(c) for u, c in zip(unique, counts)}
            
            mode_used = f"Standard ({category}/{model_name})"

        return final_image_bgr, len(stats), stats, mode_used

# 创建全局单例
detector = DetectionEngine()