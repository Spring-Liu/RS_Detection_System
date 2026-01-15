import streamlit as st
import pandas as pd
# 引入解码函数，防止 Base64 图片报错
from utils.api_client import send_detect_request, decode_base64_image


def render_image_tab(model_dict: dict):

    # -----------------------------------------
    # 1. 局部检测控制台 (现在位于页面顶部)
    # -----------------------------------------
    st.markdown("#### 🕹️ 检测参数配置")

    # 使用 col1/col2/col3 将参数横向排列
    col1, col2, col3, col4, col5 = st.columns([1.5, 2, 1.5, 1.5, 1.5])

    with col1:

        category_choice = st.selectbox(
            "检测场景", 
            ["aerial", "sar"],
            format_func=lambda x: "✈️ 航拍 (Aerial)" if x == "aerial" else "📡 雷达 (SAR)",
            key="img_scene_select" # 确保 key 唯一
        )

    # 提取可用模型列表
    available_models = model_dict.get(category_choice, ["default"])

    with col2:

        model_choice = st.selectbox("选择模型权重", available_models, key="img_model_select")

    with col3:

        conf_thres = st.slider("置信度", 0.0, 1.0, 0.35, key="img_conf_slider")

    with col4:

        use_sahi = st.checkbox("开启 SAHI", value=False, key="img_sahi_checkbox")

    with col5:

        enhance_choice = st.selectbox("图像增强", ["None", "CLAHE", "Gamma"], key="img_enhance_select")

    st.markdown("---") # 分割线

    # -----------------------------------------
    # 2. 图片上传和检测区域
    # -----------------------------------------

    st.info(f"当前参数：场景={category_choice}, 模型={model_choice}, 置信度={conf_thres}, SAHI={use_sahi}, 增强={enhance_choice}")

    # 1. 文件上传
    uploaded_file = st.file_uploader("上传图片", type=['jpg', 'jpeg', 'png', 'bmp', 'webp'])

    if uploaded_file is not None:

        # 2. 触发检测按钮
        if st.button("🚀 开始检测", type="primary"):

            with st.spinner("正在请求后端推理..."):
                file_bytes = uploaded_file.getvalue()

                # 调用 API，使用函数内部定义的局部变量
                success, result = send_detect_request(
                    file_bytes, 
                    uploaded_file.name, 
                    uploaded_file.type, 
                    model_choice,    
                    category_choice, 
                    conf_thres,      
                    use_sahi,        
                    enhance_choice   
                )

            # 3. 结果展示
            if success:
                col_img, col_stat = st.columns([2, 1])

                with col_img:
                    img_obj = decode_base64_image(result["image_base64"])
                    if img_obj:
                        st.image(img_obj, caption=f"检测结果 ({result['mode']})", use_container_width=True)
                    else:
                        st.error("图片数据解析失败")

                with col_stat:
                    st.success(f"检测到 {result['total_objects']} 个目标")

                    # 渲染统计表格
                    if result["details"]:
                        df = pd.DataFrame(list(result["details"].items()), columns=["类别", "数量"])
                        st.dataframe(df, use_container_width=True, hide_index=True)
                    else:
                        st.info("未检测到目标")
            else:
                st.error(f"检测失败: {result}")