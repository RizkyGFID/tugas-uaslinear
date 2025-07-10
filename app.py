import streamlit as st
import pandas as pd
from pulp import LpProblem, LpMaximize, LpVariable, lpSum, value

st.title("🔧 Aplikasi Optimasi Produksi (Linear Programming)")
st.markdown("Optimasi keuntungan produksi dengan batasan sumber daya menggunakan Linear Programming.")

# Jumlah produk dan kendala
num_products = st.number_input("Jumlah produk", min_value=2, step=1, value=2)
num_constraints = st.number_input("Jumlah kendala sumber daya", min_value=1, step=1, value=2)

st.subheader("📦 Masukkan Data Produk")
product_names = []
profits = []
for i in range(num_products):
    col1, col2 = st.columns([2, 1])
    with col1:
        name = st.text_input(f"Nama Produk {i+1}", f"Produk_{i+1}")
    with col2:
        profit = st.number_input(f"Keuntungan per unit {name}", value=0.0)
    product_names.append(name)
    profits.append(profit)

st.subheader("⚙️ Masukkan Data Kendala")
constraint_names = []
resource_limits = []
constraint_matrix = []

for j in range(num_constraints):
    st.markdown(f"### Kendala {j+1}")
    cname = st.text_input(f"Nama Kendala {j+1}", f"Kendala_{j+1}")
    constraint_names.append(cname)

    row = []
    for i in range(num_products):
        val = st.number_input(f"{cname} - {product_names[i]}", value=0.0, key=f"{j}_{i}")
        row.append(val)
    constraint_matrix.append(row)

    limit = st.number_input(f"Total {cname} tersedia", value=0.0, key=f"limit_{j}")
    resource_limits.append(limit)

if st.button("🚀 Hitung Solusi Optimal"):
    # Definisi model LP
    model = LpProblem("Optimasi_Produksi", LpMaximize)

    # Variabel keputusan
    x = [LpVariable(f"x{i}", lowBound=0, cat='Continuous') for i in range(num_products)]

    # Fungsi tujuan: Maksimalkan keuntungan
    model += lpSum([profits[i] * x[i] for i in range(num_products)]), "Total_Keuntungan"

    # Kendala sumber daya
    for j in range(num_constraints):
        model += lpSum([constraint_matrix[j][i] * x[i] for i in range(num_products)]) <= resource_limits[j], constraint_names[j]

    # Menyelesaikan model
    model.solve()

    st.subheader("📈 Hasil Optimasi")
    hasil = {product_names[i]: x[i].varValue for i in range(num_products)}
    hasil["Total Keuntungan"] = value(model.objective)

    st.write(pd.DataFrame([hasil]))
else:
    st.info("Masukkan data terlebih dahulu, lalu klik **Hitung Solusi Optimal**.")

