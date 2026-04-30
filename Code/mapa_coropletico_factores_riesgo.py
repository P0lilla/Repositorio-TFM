# Librerías
import pandas as pd
import plotly.graph_objects as go
import os

# Loading initial parameters
current_path = os.path.dirname(__file__)
merge_file_path = current_path[:-4] + "test_merge.csv"
save_path = os.path.join(current_path[:-4], "Data/mapa_factores_riesgo.html")
df = pd.read_csv(merge_file_path)

# Separar por sexo
df_m = df[df["sex_dichotomic"] == 1]
df_f = df[df["sex_dichotomic"] == 0]

# Como solo interesan los valores de los factores de riesgo/pais
# eliminamos los registros duplicados de cada país.
df_sin_duplicados_m = df_m.drop_duplicates(subset=['alpha3'])
df_sin_duplicados_f = df_f.drop_duplicates(subset=['alpha3'])

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
      hovertemplate="<b>%{location}</b><br>" + definicion + ": %{z}<extra></extra>"
  ))


# Lista con la información de cada trace con división sexual
traces_sex = [["Alcohol", "g pure alcohol/day", "Alcohol, average daily intake in grams among drinkers."],
          ["IPA", "Prevalence", "Percent of population attaining less than 150<br>minutes of moderate-intensity physical activity<br>per week or less than 75 minutes of vigorous-intensity<br>physical activity per week, or equivalent."],
          ["Obesity", "Prevalence", "Obesity among adults, BMI ≥ 30"],
          ["Smoking", "Prevalence", "Current tobacco use among persons aged 15<br>years and older prevalence, age-standardized"]]

# Lista con los traces sin división
traces_sin = [["AirPollution", "migrograms/m3", "Concentration of fine particulate matter (PM2.5) (Annual mean)"],
          ["Breastfeeding", "%", "Continued breastfeeding (12-23 months) %"],
          ["HepatitisB", "Prevalence", "Percent of total population who are HBsAg positive"],
          ["HepatitisC", "Prevalence", "Percent of total population who are HCsAg positive"],
          ["HumanPapilomavirus", "Inmunization coverage (%)", "HPV immunization coverage estimates among<br>primary target cohort (9-14 years old girls) (%)"],
          ["UVR", "J/m2", "Population-weighted average daily ambient UVR level"]]

# TRACES
# Masculine traces
for trace in traces_sex:
  make_traces(df_sin_duplicados_m, trace[0], trace[1], trace[2])

# Femenine traces
for trace in traces_sex:
  make_traces(df_sin_duplicados_f, trace[0], trace[1], trace[2])

# sin división sexual
for trace in traces_sin:
  make_traces(df_sin_duplicados_f, trace[0], trace[1], trace[2])


total_traces = len(traces_sex) * 2 + len(traces_sin)

buttons = []
idx = 0

# --- MALE ---
for trace in traces_sex:
    visible = [False] * total_traces
    visible[idx] = True

    buttons.append({
        "label": f"{trace[0]} (Hombres)",
        "method": "update",
        "args": [
            {"visible": visible}
        ]
    })
    idx += 1

# --- FEMALE ---
for trace in traces_sex:
    visible = [False] * total_traces
    visible[idx] = True

    buttons.append({
        "label": f"{trace[0]} (Mujeres)",
        "method": "update",
        "args": [
            {"visible": visible}
        ]
    })
    idx += 1

# --- NO DIVISION ---
for trace in traces_sin:
    visible = [False] * total_traces
    visible[idx] = True

    buttons.append({
        "label": f"{trace[0]}",
        "method": "update",
        "args": [
            {"visible": visible}
        ]
    })
    idx += 1
# --- APPLY ---
fig.update_layout(
    title={
        "text": "Prevalencia de factores de riesgo - Comparativa por género"},
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