import streamlit as st
import pandas as pd
# 假设你的 model_list 依赖于 get_remote_model_list
from utils.api_client import get_remote_model_list, send_detect_request, decode_base64_image


def render_comparison_tab(model_dict: dict):
    st.markdown("### ⚔️ 深度对比分析 (A/B Testing)")
    st.info("支持对比不同模型，或对比 **同一模型** 在 **不同配置**（如是否开启SAHI、不同增强方式）下的表现。")

    # --- 1. 全局设置 ---
    with st.container():
        col_file, col_cat = st.columns([2, 1])
        with col_file:
            uploaded_file = st.file_uploader("上传测试图片", type=['jpg', 'jpeg', 'png', 'bmp'])
        with col_cat:
            category = st.radio(
                "检测场景",
                ("aerial", "sar"),
                format_func=lambda x: "✈️ 航拍" if x == "aerial" else "📡 SAR",
                key="comp_scene_select"
            )
        conf_thres = st.slider("全局置信度阈值 (Confidence)", 0.0, 1.0, 0.35, help="控制两个模型的检测灵敏度", key="comp_conf_slider")

    st.divider()

    # --- 2. 提取可用模型 (使用传入的 model_dict) ---
    all_models = model_dict

    if isinstance(all_models, dict):
        model_list = all_models.get(category, [])
    else:
        model_list = []

    if not model_list:
        st.warning(f"⚠️ {category} 场景下暂无模型，请先上传。")
        return

    # --- 3. 左右分栏配置 ---
    col_a, col_b = st.columns(2)
    model_a_config = {}
    model_b_config = {}

    # === 配置组 A ===
    with col_a:
        st.markdown("#### 🅰️ 配置组 A")
        # ⚠️ 确保 key 唯一
        model_a_config['name'] = st.selectbox("选择模型", model_list, key="model_a_sel") 
        col_a_p1, col_a_p2 = st.columns(2)
        with col_a_p1:
            model_a_config['sahi'] = st.checkbox("开启 SAHI", value=False, key="sahi_a")
        with col_a_p2:
            model_a_config['enhance'] = st.selectbox("增强", ["None", "CLAHE", "Gamma"], key="enhance_a")
            
        st.caption(f"配置: **{model_a_config['name']}** + SAHI({model_a_config['sahi']}) + {model_a_config['enhance']}")

    # === 配置组 B ===
    with col_b:
        st.markdown("#### 🅱️ 配置组 B")
        default_idx = 1 if len(model_list) > 1 else 0
        # ⚠️ 确保 key 唯一
        model_b_config['name'] = st.selectbox("选择模型", model_list, index=default_idx, key="model_b_sel")
        col_b_p1, col_b_p2 = st.columns(2)
        with col_b_p1:
            model_b_config['sahi'] = st.checkbox("开启 SAHI", value=False, key="sahi_b")
        with col_b_p2:
            model_b_config['enhance'] = st.selectbox("增强", ["None", "CLAHE", "Gamma"], key="enhance_b")

        st.caption(f"配置: **{model_b_config['name']}** + SAHI({model_b_config['sahi']}) + {model_b_config['enhance']}")

    # --- 4. 执行对比 ---
    result_placeholder = st.empty()

    if st.button("🚀 运行对比实验", type="primary", use_container_width=True):
        if not uploaded_file:
            st.toast("请先上传一张图片！", icon="⚠️")
            return

        file_bytes = uploaded_file.getvalue()
        file_name = uploaded_file.name
        file_type = uploaded_file.type

        # === 第一步：执行后端请求 (不渲染界面) ===
        with st.spinner("正在并行推理两个模型配置，请稍候..."):
            # 请求 A
            success_a, data_a = send_detect_request(
                file_bytes, file_name, file_type, 
                model_name=model_a_config['name'], 
                category=category, 
                conf=conf_thres, 
                use_sahi=model_a_config['sahi'],
                enhance_type=model_a_config['enhance']
            )

            # 请求 B
            success_b, data_b = send_detect_request(
                file_bytes, file_name, file_type, 
                model_name=model_b_config['name'], 
                category=category, 
                conf=conf_thres, 
                use_sahi=model_b_config['sahi'],
                enhance_type=model_b_config['enhance']
            )

        # 将结果渲染到占位符中
        with result_placeholder.container():
            # === 第二步：优先展示结论 (结论置顶) ===
            if success_a and success_b:
                st.success("✅ 对比实验完成")

                count_a = data_a['total_objects']
                count_b = data_b['total_objects']
                diff = count_a - count_b

                # 结论逻辑
                if diff == 0:
                    msg = f"👉 **结论**：两种配置检测能力一致，均检测到 **{count_a}** 个目标。"
                elif diff > 0:
                    msg = f"👉 **结论**：配置组 A ({model_a_config['name']}) 更优，多检测出 **{diff}** 个目标 (A:{count_a} vs B:{count_b})。"
                else:
                    msg = f"👉 **结论**：配置组 B ({model_b_config['name']}) 更优，多检测出 **{abs(diff)}** 个目标 (B:{count_b} vs A:{count_a})。"
                
                if model_a_config['name'] == model_b_config['name']:
                    msg += " (同一模型不同配置)"
                    
                st.info(msg, icon="📝")

            # 如果有失败的情况
            elif not success_a or not success_b:
                error_msg_a = data_a.get('detail', str(data_a)) if not success_a else "成功"
                error_msg_b = data_b.get('detail', str(data_b)) if not success_b else "成功"

                st.error(f"❌ 对比实验失败：\n\n**A组错误:** {error_msg_a}\n\n**B组错误:** {error_msg_b}")
                return 

            st.divider()

            # === 第三步：渲染详细结果 (图片和表格) ===
            res_col1, res_col2 = st.columns(2)

            # 渲染 A
            with res_col1:
                st.markdown(f"**🅰️ A组结果 ({model_a_config['name']})**")
                img_obj_a = decode_base64_image(data_a["image_base64"])
                if img_obj_a:
                    st.image(img_obj_a, use_container_width=True, caption=f"A组: {data_a['total_objects']} 目标")

                if data_a["details"]:
                    df_a = pd.DataFrame(list(data_a["details"].items()), columns=["类别", "数量"])
                    st.dataframe(df_a, use_container_width=True, hide_index=True)
                else:
                    st.caption("无检测目标")

            # 渲染 B
            with res_col2:
                st.markdown(f"**🅱️ B组结果 ({model_b_config['name']})**")
                img_obj_b = decode_base64_image(data_b["image_base64"])
                if img_obj_b:
                    st.image(img_obj_b, use_container_width=True, caption=f"B组: {data_b['total_objects']} 目标")

                if data_b["details"]:
                    df_b = pd.DataFrame(list(data_b["details"].items()), columns=["类别", "数量"])
                    st.dataframe(df_b, use_container_width=True, hide_index=True)
                else:
                    st.caption("无检测目标")