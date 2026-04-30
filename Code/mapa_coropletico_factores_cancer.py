# Librerías
import pandas as pd
import plotly.graph_objects as go
import os



# Loading initial parameters
current_path = os.path.dirname(__file__)
merge_file_path = current_path[:-4] + "test_merge.csv"
save_path = os.path.join(current_path[:-4], "Data/mapa_incicencia_cancer.html")

df = pd.read_csv(merge_file_path)
df = df.drop(df.columns[5:15], axis=1)
df = df.drop(df.columns[0], axis=1)
df_wide = df.pivot_table(
    index=["alpha3", "sex_dichotomic",],
    columns="Label",
    values="Crude rate"
).reset_index()

# Separar por sexo
df_m_wide = df_wide[df_wide["sex_dichotomic"] == 1]
df_f_wide = df_wide[df_wide["sex_dichotomic"] == 0]
# También separamos por sexo el df que no ha sido pivotado
df_m = df[df["sex_dichotomic"] == 1]
df_f = df[df["sex_dichotomic"] == 0]

print(df_m.head())
# Crear figura con dos "traces"
fig = go.Figure()

# Función para hacer las traces automáticamente
def make_traces(df, variable, leyenda, definicion):
  # Primero se añade la trace
  fig.add_trace(go.Choropleth(
      locations=df["alpha3"],
      z=df[variable],
      colorscale="YlGnBu",
      colorbar_title=leyenda,
      visible = 'legendonly',
      hovertext= "prueba de hovertext",
      hoverinfo= "all",
      hovertemplate="<b>%{location}</b><br>" + definicion + ": %{z}<extra></extra>"
  ))


# Lista con la información de cada trace con división sexual
traces_male = df_m["Label"].unique()
traces_female = df_f["Label"].unique()
print(traces_female)

# TRACES
leyenda = "Crude rate"
definicion = "Annual rate per 100.000 individuals at risk"
# Masculine traces
for trace in traces_male:
  make_traces(df_m_wide, trace, leyenda, definicion)

# Femenine traces
for trace in traces_female:
  make_traces(df_f_wide, trace, leyenda, definicion)


total_traces = len(traces_male) + len(traces_female)

buttons = []
idx = 0

# --- MALE ---
for trace in traces_male:
    visible = [False] * total_traces
    visible[idx] = True

    buttons.append({
        "label": f"{trace} (Hombres)",
        "method": "update",
        "args": [
            {"visible": visible}
        ]
    })
    idx += 1

# --- FEMALE ---
for trace in traces_female:
    visible = [False] * total_traces
    visible[idx] = True

    buttons.append({
        "label": f"{trace} (Mujeres)",
        "method": "update",
        "args": [
            {"visible": visible}
        ]
    })
    idx += 1

# --- APPLY ---
fig.update_layout(
    title={
        "text": "Incidencia de cáncer por país y tipo de cáncer en 2022 - Comparativa por género"
        },
    updatemenus=[{
        "buttons": buttons,
        "direction": "down",
        "showactive": True,
        "bordercolor": "Black"
    }]
)

# Mapa
fig.update_geos(
    projection_type="natural earth",
    showcoastlines=True,
    coastlinecolor="black",
    showland=True,
    landcolor="lightgray",
    lataxis_showgrid=True,
    lonaxis_showgrid=True
)

# Exportar
fig.write_html(save_path)