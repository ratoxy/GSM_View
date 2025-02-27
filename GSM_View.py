import folium
import numpy as np
import streamlit as st
from shapely.geometry import Point, Polygon
import geopandas as gpd

def gerar_setor(lat, lon, azimute, alcance, abertura=120):
    """
    Gera os pontos do setor da célula GSM.
    """
    pontos = []
    for angulo in np.linspace(azimute - abertura / 2, azimute + abertura / 2, num=30):
        angulo_rad = np.radians(angulo)
        dlat = (alcance / 111) * np.cos(angulo_rad)
        dlon = (alcance / (111 * np.cos(np.radians(lat)))) * np.sin(angulo_rad)
        pontos.append((lat + dlat, lon + dlon))
    pontos.append((lat, lon))  # Fechar o setor
    return pontos

def main():
    st.set_page_config(layout="wide")
    st.title("GSM Sector View - NAIIC Santarém")
    
    # Coordenadas padrão (Santarém, Portugal)
    lat_default = 39.2369
    lon_default = -8.6859
    azimute_default = 90
    alcance_default = 2.0
    
    # Layout superior com os controles
    col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])
    with col1:
        lat = st.number_input("Latitude da BTS", value=lat_default, format="%.6f")
    with col2:
        lon = st.number_input("Longitude da BTS", value=lon_default, format="%.6f")
    with col3:
        azimute = st.slider("Azimute", 0, 360, azimute_default)
    with col4:
        alcance = st.number_input("Alcance (km)", value=alcance_default, format="%.1f", step=0.1)
    with col5:
        mapa_tipo = st.selectbox("Tipo de mapa", ["Padrão", "Satélite", "Híbrido"])
    
    # Escolher o tipo de mapa corretamente
    if mapa_tipo == "Padrão":
        tiles = "CartoDB positron"
    elif mapa_tipo == "Satélite":
        tiles = "Esri WorldImagery"
    elif mapa_tipo == "Híbrido":
        tiles = "Esri WorldImagery"
        attr = ""
    else:
        attr = ""
    
    # Gerar setor
    setor_coords = gerar_setor(lat, lon, azimute, alcance)
    setor_poly = Polygon(setor_coords)
    
    # Criar mapa com folium
    if mapa_tipo == "Híbrido":
        mapa = folium.Map(location=[lat, lon], zoom_start=13, tiles=tiles, attr=attr)
    else:
        mapa = folium.Map(location=[lat, lon], zoom_start=13, tiles=tiles)
    folium.Marker([lat, lon], tooltip="BTS").add_to(mapa)
    
    # Adicionar setor ao mapa
    folium.Polygon(
        locations=setor_coords,
        color="blue",
        fill=True,
        fill_color="blue",
        fill_opacity=0.3
    ).add_to(mapa)
    
    # Exibir mapa no Streamlit ocupando toda a largura
        # Adicionar camada de rótulos se for híbrido
    if mapa_tipo == "Híbrido":
        folium.TileLayer(
            tiles="https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}",
            attr="Esri",
            name="Labels",
            overlay=True
        ).add_to(mapa)
    
    folium.LayerControl().add_to(mapa)  # Adiciona controle para alternar camadas
    
    st.components.v1.html(mapa._repr_html_(), height=900)

if __name__ == "__main__":
    main()
