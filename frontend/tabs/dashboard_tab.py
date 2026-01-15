import streamlit as st
import pandas as pd
import plotly.express as px
from utils.api_client import fetch_history_data

# --- Session State 缓存数据 ---
if 'dashboard_data' not in st.session_state:
    st.session_state['dashboard_data'] = None

# --- 数据加载函数 ---
def load_data():
    """从后端加载历史数据并缓存到 Session State"""
    with st.spinner("🚀 正在加载和分析历史数据..."):
        success, result = fetch_history_data("/analytics")

        if success:
            raw_data = result
            if len(raw_data) > 0:
                df = pd.DataFrame(raw_data)
                if 'created_at' in df.columns:
                    df['created_at'] = pd.to_datetime(df['created_at'])
                    # 按时间倒序排列
                    df.sort_values(by='created_at', ascending=False, inplace=True)

                # 缓存处理后的数据
                st.session_state['dashboard_data'] = df
                return True
            else:
                st.session_state['dashboard_data'] = pd.DataFrame() # 空DataFrame
                st.info("📂 数据库中暂无检测记录。")
                return False
        else:
            st.error(f"❌ 数据加载失败: {result}")
            st.session_state['dashboard_data'] = None
            return False

# --- 主渲染函数 ---
def render_dashboard_tab():
    st.markdown("## 📊 历史数据分析大屏")

    # --- 1. 数据加载与刷新 ---
    if st.session_state['dashboard_data'] is None:
        # 首次加载
        load_data()

    # 刷新按钮 (放在更显眼的位置)
    if st.button("🔄 立即刷新数据"):
        load_data()
        st.rerun() # 触发重绘以显示新数据

    df = st.session_state['dashboard_data']

    if df is None:
        # 错误或加载中
        return

    if df.empty:
        st.info("请先前往【图片检测】或【视频检测】页面生成数据。")
        return

    # ----------------------------------------------------
    # I. 核心指标卡 (KPI) - 使用卡片视觉
    # ----------------------------------------------------
    st.markdown("### 关键绩效指标 (KPIs)")

    with st.container(border=True):
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)

        # 1. 累计任务数
        total_tasks = len(df)
        kpi1.metric("累计检测任务", f"{total_tasks} 次", delta_color="off")

        # 2. 累计目标数
        total_objects = df['object_count'].sum() if 'object_count' in df.columns else 0
        kpi2.metric("累计发现目标", f"{total_objects} 个", delta_color="off")

        # 3. 平均目标密度 (每张图/视频帧的平均目标数)
        avg_objects = total_objects / total_tasks if total_tasks > 0 else 0
        kpi3.metric("平均目标密度", f"{avg_objects:.2f} 个/任务", delta_color="off")

        # 4. 最近检测时间
        latest_time = df['created_at'].iloc[0].strftime('%Y-%m-%d %H:%M')
        kpi4.metric("最近活动时间", latest_time, delta_color="off")

    st.divider()

    # ----------------------------------------------------
    # II. 可视化图表 - 使用分栏和子标题隔离
    # ----------------------------------------------------

    st.markdown("### 深度分析图表")

    # --- A. 目标数量趋势 (折线图) ---
    with st.container(border=True):
        st.subheader("📈 目标数量趋势分析")

        if 'created_at' in df.columns and 'object_count' in df.columns:
            # 按天聚合，显示每日总目标数量
            df_daily = df.set_index('created_at').resample('D')['object_count'].sum().reset_index()
            df_daily.columns = ['日期', '目标总量']

            fig_line = px.line(
                df_daily, 
                x='日期', 
                y='目标总量', 
                markers=True, 
                title='每日目标数量变化趋势',
                labels={'日期': '检测日期', '目标总量': '目标总数'}
            )
            fig_line.update_layout(hovermode="x unified")
            st.plotly_chart(fig_line, use_container_width=True, config={'displayModeBar': False})
        else:
            st.warning("数据中缺少时间或数量信息，无法绘制趋势图。")

    st.markdown("") # 视觉间距

    chart1, chart2 = st.columns(2)

    # --- B. 算法模式分布 (饼图) ---
    with chart1:
        with st.container(border=True):
            st.subheader("🤖 算法模式分布")

            if 'model_type' in df.columns:
                fig_pie = px.pie(
                    df, 
                    names='model_type', 
                    title='不同检测模式的使用占比', 
                    hole=0.5,
                    color_discrete_sequence=px.colors.sequential.Teal
                )
                fig_pie.update_traces(textposition='inside', textinfo='percent+label', marker=dict(line=dict(color='#000000', width=1)))
                st.plotly_chart(fig_pie, use_container_width=True, config={'displayModeBar': False})
            else:
                st.info("数据中缺少模型类型信息。")

    # --- C. 类别总览 (柱状图) ---
    with chart2:
        with st.container(border=True):
            st.subheader("🏆 全库各类目标检出总量")

            # 解析 JSON details 字段并累加 (与原逻辑相同)
            total_cls_counts = {}
            for index, row in df.iterrows():
                details = row.get('details')
                if details and isinstance(details, dict):
                    for k, v in details.items():
                        total_cls_counts[k] = total_cls_counts.get(k, 0) + v

            if total_cls_counts:
                df_counts = pd.DataFrame(list(total_cls_counts.items()), columns=['类别', '数量'])
                df_counts.sort_values(by='数量', ascending=True, inplace=True) # 升序用于条形图

                fig_bar = px.bar(
                    df_counts, 
                    x='数量', 
                    y='类别', # 转换为条形图 (Bar Chart) 视觉效果更好
                    color='类别', 
                    orientation='h',
                    text_auto=True,
                    title='各类目标累计检测数量统计'
                )
                fig_bar.update_layout(showlegend=False, hovermode="y unified")
                st.plotly_chart(fig_bar, use_container_width=True, config={'displayModeBar': False})
            else:
                st.info("暂无具体的类别统计数据。")

    # --- D. 原始数据表 (折叠) ---
    st.divider()
    with st.expander("📝 展开查看原始数据库记录"):
        # 隐藏 ID 和 Details 字段，只显示关键信息
        cols_to_display = ['created_at', 'model_name', 'category', 'object_count', 'user_id']
        display_df = df[[col for col in cols_to_display if col in df.columns]]
        st.dataframe(display_df, use_container_width=True, hide_index=True)