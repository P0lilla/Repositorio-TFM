# Librerías
import pandas as pd
import plotly.graph_objects as go
import os



# Loading initial parameters
current_path = os.path.dirname(__file__)
merge_file_path = current_path[:-4] + "test_merge.csv"
save_path = os.path.join(current_path[:-4], "Data/mapa_cancer_mas_comun.html")

df = pd.read_csv(merge_file_path)
df = df.drop(df.columns[5:15], axis=1)
df = df.drop(df.columns[0], axis=1)

# Asignamos un número a cada tipo de cáncer
tipos_cancer = df["Label"].unique()

mapeo_cancer = {etiqueta: i for i, etiqueta in enumerate(tipos_cancer)}

# Separar por sexo
df_m = df[df["sex_dichotomic"] == 1]
df_f = df[df["sex_dichotomic"] == 0]

# Seleccionar el tipo de cancer más frecuente y asignarle su número
df_m = df_m.sort_values(['alpha3', 'Crude rate'], ascending=[True, False])
df_m = df_m.groupby('alpha3').first().reset_index()
df_m["Label_num"] = df_m["Label"].map(mapeo_cancer)

df_f = df_f.sort_values(['alpha3', 'Crude rate'], ascending=[True, False])
df_f = df_f.groupby('alpha3').first().reset_index()
df_f["Label_num"] = df_f["Label"].map(mapeo_cancer)

# Crear figura con dos "traces"
fig = go.Figure()

# MALES
fig.add_trace(go.Choropleth(
   locations = df_m["alpha3"],
   z=df_m["Label_num"],
   colorscale="viridis",
   text=df_m["Label"],
   hovertemplate="<b>%{location}</b><br>" +
                  "Cáncer más común: %{text}<br>" +
                  "<extra></extra>",
   showscale=False,
   visible=True
))

# FEMALES
fig.add_trace(go.Choropleth(
   locations = df_f["alpha3"],
   z=df_f["Label_num"],
   colorscale="viridis",
   text=df_f["Label"],
   hovertemplate="<b>%{location}</b><br>" +
                  "Cáncer más común: %{text}<br>" +
                  "<extra></extra>",
   showscale=False,
   visible=False
))

# Configurar los botones
fig.update_layout(
    updatemenus=[
        dict(
            buttons=list([
                dict(
                    args=[{"visible": [True, False]}],  # Solo hombres visible
                    label="Hombres",
                    method="update"
                ),
                dict(
                    args=[{"visible": [False, True]}],  # Solo mujeres visible
                    label="Mujeres",
                    method="update"
                )
            ]),
            direction="down",
            showactive=True,
            x=0.02,
            xanchor="left",
            y=1.02,
            yanchor="top",
            bgcolor="white",
            bordercolor="black",
            borderwidth=1,
            font=dict(size=12)
        )
    ],
    title="Cáncer con mayor incidencia por país en 2022 - Comparativa por género",
    geo=dict(
        projection_type="natural earth",
        showcoastlines=True,
        coastlinecolor="black",
        showland=True,
        landcolor="lightgray",
        lataxis_showgrid=True,
        lonaxis_showgrid=True
    )
)


# Exportar
fig.write_html(save_path)