import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np



from PIL import Image

file_path = '/Users/suhyun/Desktop/map/제목 2.png'
# 이미지 열기
img = Image.open(file_path)
# 이미지 리사이즈
image_resized = img.resize((150, 150), resample=Image.LANCZOS)
st.image(image_resized)
#st.write(
#    """ 도로 안전과 입지 분석을 시각화하는 클러스터링 솔루션 """
#)

# CSV 파일 업로드
csv_file = st.file_uploader('파일 업로드', type=['csv', 'excel'])

# 업로드된 파일을 Pandas DataFrame으로 읽기
if csv_file is not None:
    df = pd.read_csv(csv_file)

    # 날짜 관련 컬럼이 제대로 파싱되었는지 확인
    required_columns = ['연도', '월', '일', '구', '포트홀 위험 지수']
    if not all(col in df.columns for col in required_columns):
        st.error(f"데이터에 {', '.join(required_columns)} 컬럼이 없습니다. 데이터를 확인해주세요.")
    else:
        # 필터링을 위한 셀렉트박스
        year_options = ['전체'] + sorted(df['연도'].unique().tolist())
        month_options = ['전체'] + sorted(df['월'].unique().tolist())
        day_options = ['전체'] + sorted(df['일'].unique().tolist())
        gu_options = ['전체'] + sorted(df['구'].unique().tolist())

        selected_year = st.selectbox("연도 선택", year_options)
        selected_month = st.selectbox("월 선택", month_options)
        selected_day = st.selectbox("일 선택", day_options)
        selected_gu = st.selectbox("구 선택", gu_options)

        # 데이터프레임을 화면에 출력
        st.write("업로드된 데이터:")
        st.write(df)

        # 필터링된 데이터
        filtered_df = df.copy()

        if selected_year != '전체':
            filtered_df = filtered_df[filtered_df['연도'] == int(selected_year)]
        if selected_month != '전체':
            filtered_df = filtered_df[filtered_df['월'] == int(selected_month)]
        if selected_day != '전체':
            filtered_df = filtered_df[filtered_df['일'] == int(selected_day)]
        if selected_gu != '전체':
            filtered_df = filtered_df[filtered_df['구'] == selected_gu]

        # 그래프 출력
        if not filtered_df.empty:
            # 포트홀 위험 지수 히스토그램 데이터를 위한 설정
            data = filtered_df['포트홀 위험 지수'].dropna()
            n_bins = 30
            counts, bins = np.histogram(data, bins=n_bins)

            # 애플 스타일의 히스토그램 애니메이션 생성
            fig = go.Figure()

            # 초기 히스토그램 설정
            fig.add_trace(go.Bar(
                x=bins[:-1],
                y=[0] * n_bins,
                marker=dict(color='#007AFF'),
                name='포트홀 위험 지수'
            ))

            # 프레임 생성
            frames = [go.Frame(data=[go.Bar(x=bins[:-1], y=counts[:i])]) for i in range(1, n_bins + 1)]

            # 애니메이션을 자동 재생하도록 설정
            fig.update_layout(
                title=f"포트홀 위험 지수 분포 애니메이션 ({selected_year}년 {selected_month}월 {selected_day}일, {selected_gu})",
                xaxis_title="포트홀 위험 지수",
                yaxis_title="빈도",
                template="simple_white",
                font=dict(family="Arial, sans-serif", size=18, color="#333"),
                margin=dict(l=20, r=20, t=50, b=20),
                updatemenus=[dict(
                    type="buttons",
                    buttons=[dict(
                        label="Play",
                        method="animate",
                        args=[None, dict(frame=dict(duration=100, redraw=True), fromcurrent=True, mode='immediate')],
                    )],
                    direction="left",
                    pad={"r": 10, "t": 87},
                    x=0.17,
                    xanchor="right",
                    y=0,
                    yanchor="top"
                )],
                sliders=[dict(
                    steps=[dict(
                        method="animate",
                        args=[[f.name], dict(mode="immediate", frame=dict(duration=100, redraw=True), transition=dict(duration=0))],
                        label=f"{i+1}"
                    ) for i, f in enumerate(frames)],
                    transition=dict(duration=0),
                    x=0.1,
                    xanchor="left",
                    y=0,
                    yanchor="top",
                    pad=dict(t=50)
                )]
            )

            # 프레임 추가
            fig.frames = frames

            # Streamlit에서 Plotly 그래프 표시
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("선택한 조건에 해당하는 데이터가 없습니다.")
else:
    st.info("파일을 업로드해주세요.")