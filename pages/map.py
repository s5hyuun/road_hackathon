import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
import geopandas as gpd
from PIL import Image

# 이미지 파일 경로 및 리사이즈
file_path = '/Users/suhyun/Desktop/map/제목 2.png'
img = Image.open(file_path)
image_resized = img.resize((150, 150), resample=Image.LANCZOS)
st.image(image_resized)

st.markdown(" # Daero")

# 파일 업로드 설정
file_path = st.file_uploader('CSV 파일 업로드', type=['csv'])
geojson_file_path = st.file_uploader('GeoJSON 파일 업로드', type=['geojson'])

if file_path and geojson_file_path:
    # 데이터 읽기
    df = pd.read_csv(file_path)
    gdf = gpd.read_file(geojson_file_path)

    # '구' 필드 추출
    gdf['구'] = gdf['adm_nm'].apply(lambda x: x.split()[1])

    # Streamlit 앱 제목 설정
    st.title('대구 구별 클러스터 데이터 시각화 및 하이라이트')

    # 클러스터 의미 정의
    cluster_labels = {
        '0': '낮은위험지수 & 낮은중요도',
        '1': '높은 위험지수 & 낮은중요도',
        '2': '높은위험지수 & 높은중요도',
        '3': '낮은위험지수 & 높은중요도'
    }

    # 구 선택을 위한 셀렉트박스 생성
    gu_option = st.selectbox('구를 선택하세요:', gdf['구'].unique())

    # 클러스터 선택을 위한 멀티셀렉트 생성 (중복 선택 가능)
    cluster_options = st.multiselect(
        '클러스터를 선택하세요:',
        options=[label for label in cluster_labels.values()],
        default=[label for label in cluster_labels.values()]
    )

    # 클러스터 ID와 레이블 매핑
    reverse_cluster_labels = {v: k for k, v in cluster_labels.items()}
    selected_cluster_ids = [reverse_cluster_labels[label] for label in cluster_options]

    # 선택한 구에 해당하는 경계 데이터 필터링
    selected_gu = gdf[gdf['구'] == gu_option]

    # 지도 중심 설정
    center_lat = selected_gu.geometry.centroid.y.mean()
    center_lon = selected_gu.geometry.centroid.x.mean()

    # 지도 생성 (여기서 타일 스타일 변경 가능)
    m = folium.Map(location=[center_lat, center_lon], zoom_start=12, tiles='cartodb positron')

    # 선택한 구의 경계를 지도에 추가 및 하이라이트
    folium.GeoJson(
        selected_gu.geometry,
        name=f'{gu_option} 경계선',
        style_function=lambda x: {
            'color': '#3186cc',
            'weight': 3,
            'fillOpacity': 0.1
        }
    ).add_to(m)

    # 전체 대구 지도에 다른 구도 표시 (약하게)
    for _, row in gdf[gdf['구'] != gu_option].iterrows():
        folium.GeoJson(
            row.geometry,
            name=row['구'],
            style_function=lambda x: {
                'color': 'grey',
                'weight': 1,
                'fillOpacity': 0.1
            }
        ).add_to(m)

    # 해당 구의 선택한 클러스터 데이터 필터링
    cluster_data = df[(df['구'] == gu_option) & (df['kmeans_cluster'].astype(str).isin(selected_cluster_ids))]

    # 클러스터 색상 지정 (예시)
    cluster_colors = {'0': '#2ca02c', '1': '#1f77b4', '2': '#d62728', '3': '#ffeb3b'}  # 노란색으로 변경

    # 클러스터 데이터 시각화
    for lat, lon, cluster_id in zip(cluster_data['위도'], cluster_data['경도'], cluster_data['kmeans_cluster']):
        folium.CircleMarker(
            location=[lat, lon],
            radius=0.5,  # 마커 크기
            color=cluster_colors[str(cluster_id)],
            fill=True,
            fill_color=cluster_colors[str(cluster_id)],
            fill_opacity=0.7,
            popup=f'클러스터 {cluster_id}'
        ).add_to(m)

    # 레전드 추가
    legend_html = '''
    <div style="position: fixed; 
                bottom: 50px; left: 50px; width: 200px; height: 150px; 
                background-color: white; z-index:9999; font-size:14px;
                border:2px solid grey; padding: 10px;">
        <b>클러스터 색상</b><br>
        <i style="background: #2ca02c; color: white; padding: 2px;">&nbsp;&nbsp;&nbsp;</i> 낮은위험지수 & 낮은중요도<br>
        <i style="background: #1f77b4; color: white; padding: 2px;">&nbsp;&nbsp;&nbsp;</i> 높은 위험지수 & 낮은중요도<br>
        <i style="background: #d62728; color: white; padding: 2px;">&nbsp;&nbsp;&nbsp;</i> 높은위험지수 & 높은중요도<br>
        <i style="background: #ffeb3b; color: white; padding: 2px;">&nbsp;&nbsp;&nbsp;</i> 낮은위험지수 & 높은중요도<br>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))

    # Folium 지도 렌더링
    folium_static(m)

    # 선택한 구의 클러스터 데이터를 데이터프레임으로 표시
    st.subheader(f'{gu_option}의 클러스터 데이터 (선택한 클러스터만)')
    st.dataframe(cluster_data)
