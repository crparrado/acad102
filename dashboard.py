import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io

# ---------------------------------------------------------
# Título fijo del dashboard (no incluye el NRC)
# ---------------------------------------------------------
st.title("ACAD102 2025/10")

# ---------------------------------------------------------
# Carga del archivo .txt
# ---------------------------------------------------------
uploaded_file = st.file_uploader("Sube tu archivo .txt con la tabla", type=["txt"])

if uploaded_file is not None:
    # Leer todo el contenido del archivo
    content = uploaded_file.read().decode("utf-8")
    lines = content.splitlines()

    # ---------------------------------------------------------
    # 1) EXTRAER NRC DE LA PRIMERA LÍNEA
    #    Formato esperado: "ACAD102 - NRC 12345 - 2025/10"
    # ---------------------------------------------------------
    first_line = lines[0].strip() if len(lines) > 0 else ""
    # Ejemplo: "ACAD102 - NRC 14397 - 2025/10"
    # Dividimos por '-'
    parts = [p.strip() for p in first_line.split('-')]
    # parts = ["ACAD102", "NRC 14397", "2025/10"]
    
    nrc = parts[1] if len(parts) >= 2 else "NRC desconocido"
    
    # ---------------------------------------------------------
    # 2) BUSCAR COMENTARIOS
    #    Se asume que en el archivo hay dos secciones:
    #      "Comentarios:"
    #      "Comentarios Música/Vitalizador:"
    # ---------------------------------------------------------
    start_idx = None
    end_idx = None
    for i, line in enumerate(lines):
        if line.strip().startswith("Comentarios:"):
            start_idx = i
        if line.strip().startswith("Comentarios Música/Vitalizador:"):
            end_idx = i

    # Comentarios normales
    comments = []
    # Comentarios de música/vitalizador
    comments_music = []

    if start_idx is not None and end_idx is not None:
        # Líneas entre "Comentarios:" y "Comentarios Música/Vitalizador:"
        comments = lines[start_idx + 1 : end_idx]
        # Líneas después de "Comentarios Música/Vitalizador:"
        comments_music = lines[end_idx + 1 :]
    
    # Si no se encontró "Comentarios Música/Vitalizador:",
    # pueden existir comentarios solo de la primera sección
    elif start_idx is not None and end_idx is None:
        comments = lines[start_idx + 1 :]
    
    # ---------------------------------------------------------
    # 3) DataFrame con datos "ejemplo" quemados
    #    (Puedes parsear la tabla del .txt si deseas automatizarlo)
    # ---------------------------------------------------------
    data = {
        'pregunta': [
            'Los contenidos entregados fueron claros',
            'Las actividades realizadas contribuyeron a mi aprendizaje',
            'Los recursos de apoyo fueron pertinentes a los objetivos de las clases',
            'Mi participación en clases fue activa',
            'El facilitador generó un clima de confianza',
            'El facilitador abrió instancias para aclarar dudas',
            'El facilitador promovió el diálogo colectivo en clases'
        ],
        'nunca':          [0, 0, 0, 0, 0, 0, 0],
        'casi_nunca':     [0, 0, 0, 0, 0, 0, 0],
        'a_veces':        [0, 1, 0, 2, 0, 1, 0],
        'casi_siempre':   [3, 5, 2, 6, 3, 0, 1],
        'siempre':        [14, 11, 15, 9, 14, 16, 16]
    }
    df = pd.DataFrame(data)

    # ---------------------------------------------------------
    # 4) Calcular cantidad de personas que respondieron
    # ---------------------------------------------------------
    total_respondents = df.loc[0, ['nunca','casi_nunca','a_veces','casi_siempre','siempre']].sum()

    # ---------------------------------------------------------
    # 5) Mostrar información general
    # ---------------------------------------------------------
    st.subheader("Información general de la evaluación")
    st.write(f"- **NRC:** {nrc}")
    st.write(f"- **Número de personas que respondieron la encuesta:** {int(total_respondents)}")

    # ---------------------------------------------------------
    # 6) Mostrar tabla de resultados (datos "quemados")
    # ---------------------------------------------------------
    st.subheader("Tabla de resultados")
    st.dataframe(df)

    # ---------------------------------------------------------
    # 7) Graficar cada pregunta (matplotlib) con colores solicitados
    #    y permitir descargar cada gráfica en PNG.
    # ---------------------------------------------------------
    st.subheader("Gráficas de cada pregunta")
    for idx, row in df.iterrows():
        respuestas_dict = {
            'nunca': row['nunca'],
            'casi_nunca': row['casi_nunca'],
            'a_veces': row['a_veces'],
            'casi_siempre': row['casi_siempre'],
            'siempre': row['siempre']
        }
        
        # Crear figura y eje
        fig, ax = plt.subplots()
        
        # Extraer claves y valores para la gráfica
        categorias = list(respuestas_dict.keys())
        valores = list(respuestas_dict.values())
        
        # Graficar barras con color #091b2c
        ax.bar(categorias, valores, color='#091b2c')
        
        # Personalizar ejes de color #ab172b
        ax.spines["bottom"].set_color("#ab172b")
        ax.spines["left"].set_color("#ab172b")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        ax.tick_params(axis='x', colors="#ab172b")
        ax.tick_params(axis='y', colors="#ab172b")
        
        # Título de la gráfica en color negro
        ax.set_title(row['pregunta'], color='black')
        
        # Etiqueta del eje Y en #ab172b, sin etiqueta en X
        ax.set_ylabel("Alumnos", color="#ab172b")
        ax.set_xlabel("")  # Sin etiqueta en eje X

        # Mostrar la figura en Streamlit
        st.pyplot(fig)

        # -------------------------------------------------------
        # Generar botón de descarga en formato PNG
        # -------------------------------------------------------
        img_data = io.BytesIO()
        fig.savefig(img_data, format='png', bbox_inches='tight')
        img_data.seek(0)  # Volver al inicio del archivo en memoria

        # Construimos un nombre de archivo seguro basado en la pregunta
        safe_name = row['pregunta'].replace(" ", "_").replace("á","a").replace("é","e")\
                                   .replace("í","i").replace("ó","o").replace("ú","u")\
                                   .replace("ñ","n").replace(",","").replace("¿","")\
                                   .replace("?","").replace("¡","").replace("!","")\
                                   .replace("(","").replace(")","")
        file_name = f"grafica_{idx}_{safe_name[:30]}.png"  # recortado a 30 chars

        st.download_button(
            label="Descargar gráfica",
            data=img_data,
            file_name=file_name,
            mime="image/png"
        )

        # Cerrar la figura para no acumular
        plt.close(fig)

    # ---------------------------------------------------------
    # 8) Mostrar comentarios
    # ---------------------------------------------------------
    if comments:
        st.subheader("Comentarios")
        for c in comments:
            c = c.strip()
            if c:
                st.write(f"- {c}")

    if comments_music:
        st.subheader("Comentarios Música/Vitalizador")
        for c in comments_music:
            c = c.strip()
            if c:
                st.write(f"- {c}")

else:
    st.info("Por favor, sube primero un archivo .txt para continuar.")
