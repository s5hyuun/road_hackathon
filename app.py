import streamlit as st
import pandas as pd
from datetime import datetime
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns

from PIL import Image

file_path = '/Users/suhyun/Desktop/map/제목 2.png'
# 이미지 열기
img = Image.open(file_path)
# 이미지 리사이즈
image_resized = img.resize((150, 150), resample=Image.LANCZOS)
st.image(image_resized)


# 리사이즈된 이미지 확인 (옵션)
#image_resized.show()

# 파일 경로가 올바른지 확인하세요.
#file_path = '/Users/suhyun/Desktop/map/제목 2.png'
# 이미지 열기
#img = Image.open(file_path)
# 이미지 리사이즈
#image = img.resize((55, 55), resample=Image.LANCZOS)
#st.image(img)


# 한글폰트 적용
matplotlib.rcParams['axes.unicode_minus'] = False
plt.rcParams["font.family"] = 'NanumGothic'

#st.set_page_config(page_title="포트홀", page_icon="📊")

st.markdown(" # Daero")
st.sidebar.header("사이드바")
st.write(
    """ 도로 안전과 입지 분석을 시각화하는 클러스터링 솔루션 """
)

# CSV 파일을 미리 읽어옵니다. (세션 상태에 저장)
if 'original_df' not in st.session_state:
    st.session_state.original_df = pd.read_csv('/Users/suhyun/Desktop/map/k-means_df.csv')

def main():
    # 현재 필터링된 데이터프레임을 세션 상태에서 관리
    df = st.session_state.original_df.copy()

    with st.sidebar:
        current_year = datetime.now().year

        # 기본 연도 목록 설정 (2021~2024)
        default_years = ["2021", "2022", "2023", "2024"]

        # 세션 상태를 사용하여 동적으로 연도 목록을 관리합니다.
        if 'years' not in st.session_state:
            st.session_state.years = default_years.copy()

        # 연도 선택
        year_option = st.selectbox("연도 선택", sorted(st.session_state.years) + ["직접 입력"])

        if year_option == "직접 입력":
            year_input = st.text_input("연도 입력", "")
            if year_input:
                if not year_input.isdigit() or int(year_input) < current_year:
                    st.warning("올바른 연도를 입력하세요. (현재 연도 또는 그 이후의 연도)")
                    year = None
                else:
                    year = int(year_input)
                    # 입력된 연도가 목록에 없으면 추가
                    if year_input not in st.session_state.years:
                        st.session_state.years.append(year_input)
            else:
                year = None
        else:
            year = int(year_option)

        # 월 선택
        month = st.selectbox("월 선택", ["1월", "2월", "3월", "4월", "5월", "6월", "7월", "8월", "9월", "10월", "11월", "12월"])

        # 구 선택
        cities = ['수성구', "중구", "동구", "남구", "달서구", "북구", "서구"]
        selected_city = st.selectbox("구 선택", cities)

        # 구에 따른 동 목록 정의
        district_options = {
            '수성구': ['만촌동', '황금동', '욱수동', '두산동', '범어동', '상동', '대흥동', '이천동', '지산동',
                      '신매동', '파동', '시지동', '중동', '가천동', '노변동', '사월동', '매호동', '범물동', '삼덕동',
                      '연호동', '고모동', '성동'],
            '중구': ['대봉동', '봉산동', '대신동', '달성동', '남산동', '공평동', '문화동', '동산동', '도원동', '덕산동', '수창동', '인교동', '동문동', '교동', '포정동', '사일동', '화전동', '남일동', '전동', '수동', '상서동', '하서동'],
            "동구": ['율하동', '효목동', '신서동', '용계동', '방촌동', '검사동', '지묘동', '진인동', '지저동',
                    '신암동', '신천동', '각산동', '불로동', '봉무동', '백안동', '덕곡동', '신평동', '내동',
                    '미곡동', '입석동', '괴전동', '중대동', '동호동', '신기동', '대림동', '능성동', '숙천동',
                    '미대동', '율암동', '서호동', '도동', '사복동', '도학동', '송정동', '금강동'],
            "남구": ['이천동', '봉덕동', '대명동'],
            "달서구": ['장동', '이곡동', '갈산동', '도원동', '두류동', '진천동', '성당동', '신당동', '호산동',
                      '송현동', '장기동', '유천동', '월성동', '본동', '대천동', '용산동', '본리동', '감삼동',
                      '상인동', '월암동', '대곡동', '파호동', '죽전동', '호림동'],
            "북구": ['침산동', '태전동', '읍내동', '복현동', '연경동', '관음동', '동천동', '산격동', '국우동',
                    '매천동', '사수동', '구암동', '서변동', '학정동', '팔달동', '노곡동', '금호동', '대현동',
                    '조야동', '동호동', '검단동', '동변동', '도남동'],
            "서구": ['이현동', '평리동', '중리동', '내당동', '비산동', '상리동']
        }

        # 선택된 구에 따른 동 목록 필터링
        districts = district_options.get(selected_city, [])
        selected_districts = st.multiselect("동 선택", districts)

        # 확인 버튼
        if st.button('확인'):
            # 필터링 로직을 적용한 후 df를 업데이트
            if year is not None:
                df = df[df['연도'] == year]

            if month:
                df = df[df['월'] == int(month.replace("월", ""))]

            if selected_city:
                df = df[df['구'] == selected_city]

            if selected_districts:
                df = df[df['동'].isin(selected_districts)]

            # 필터링된 데이터프레임을 세션 상태에 저장
            st.session_state.filtered_df = df

    # 확인 버튼을 누른 후 필터링된 데이터프레임을 오른쪽 화면에 표시
    if 'filtered_df' in st.session_state:
        #st.write(f"선택한 연도: {year}")
        #st.write(f"선택한 월: {month}")
        #st.write(f"선택한 구: {selected_city}")
        #st.write(f"선택한 동: {selected_districts}")

        st.write("필터링된 데이터:")
        st.dataframe(st.session_state.filtered_df)  # 데이터프레임을 표 형태로 오른쪽 화면에 표시

if __name__ == "__main__":
    main()