import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import linprog

st.title("Optimasi Produksi dengan Linear Programming")
st.write("""
Aplikasi ini membantu menentukan kombinasi produk optimal untuk memaksimalkan keuntungan 
dengan kendala sumber daya (waktu, bahan baku, tenaga kerja).
""")

# Input Pengguna
st.sidebar.header("Input Parameter")

num_products = st.sidebar.number_input("Jumlah Produk", min_value=2, max_value=5, value=2)

# Input keuntungan dan kendala
product_names = []
profits = []
constraints = []

cols = st.columns(num_products)
for i in range(num_products):
    with cols[i]:
        product_names.append(st.text_input(f"Nama Produk {i+1}", value=f"Produk {i+1}"))
        profits.append(st.number_input(f"Keuntungan/Unit ({product_names[i]})", min_value=0.0, value=10.0))

st.subheader("Kendala Sumber Daya")
num_constraints = st.number_input("Jumlah Jenis Kendala (e.g., bahan baku, waktu)", min_value=1, max_value=3, value=1)

# Matriks kendala (A) dan batas (b)
A = []
b = []

for j in range(num_constraints):
    st.write(f"### Kendala {j+1}")
    constraint_name = st.text_input(f"Nama Kendala {j+1} (e.g., Jam Kerja)", value=f"Kendala {j+1}")
    constraint_cols = st.columns(num_products + 1)
    
    constraint_row = []
    for i in range(num_products):
        with constraint_cols[i]:
            constraint_row.append(st.number_input(f"Penggunaan {constraint_name} per {product_names[i]}", min_value=0.0, value=1.0))
    
    with constraint_cols[-1]:
        constraint_limit = st.number_input(f"Total {constraint_name} Tersedia", min_value=0.0, value=10.0)
    
    A.append(constraint_row)
    b.append(constraint_limit)

# Solve Linear Programming
if st.button("Hitung Solusi Optimal"):
    # Ubah ke bentuk standar linprog (minimisasi, jadi kita negasikan keuntungan)
    c = [-p for p in profits]  # Koefisien tujuan (untuk minimisasi)
    
    # Batasan: A_ub @ x <= b_ub
    A_ub = np.array(A)
    b_ub = np.array(b)
    
    # Batasan non-negatif
    bounds = [(0, None) for _ in range(num_products)]
    
    # Solusi
    result = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method='highs')
    
    if result.success:
        st.success("Solusi Optimal Ditemukan!")
        st.subheader("Hasil Optimasi")
        
        total_profit = 0
        for i in range(num_products):
            st.write(f"Produksi {product_names[i]}: **{round(result.x[i], 2)}** unit")
            total_profit += result.x[i] * profits[i]
        
        st.metric("Total Keuntungan Maksimal", f"Rp {total_profit:,.2f}")
        
        # Visualisasi (khusus 2 produk)
        if num_products == 2:
            st.subheader("Visualisasi Area Feasible")
            fig, ax = plt.subplots()
            
            # Plot kendala
            x = np.linspace(0, max(result.x[0]*1.5, 5), 100)
            for j in range(num_constraints):
                if A[j][1] != 0:  # Hindari pembagian oleh 0
                    y = (b[j] - A[j][0] * x) / A[j][1]
                    ax.plot(x, y, label=f'{constraint_name}: {A[j][0]}x + {A[j][1]}y ≤ {b[j]}')
                    ax.fill_between(x, 0, y, alpha=0.1)
            
            # Titik solusi optimal
            ax.scatter(result.x[0], result.x[1], color='red', label=f'Solusi Optimal ({result.x[0]:.1f}, {result.x[1]:.1f})')
            
            ax.set_xlabel(f"Produksi {product_names[0]}")
            ax.set_ylabel(f"Produksi {product_names[1]}")
            ax.set_title("Daerah Feasible dan Solusi Optimal")
            ax.legend()
            ax.grid(True)
            st.pyplot(fig)
    else:
        st.error("Tidak ditemukan solusi feasible. Periksa kembali kendala Anda.")

st.caption("""
**Catatan**: 
- Untuk visualisasi, saat ini hanya mendukung 2 produk.
- Sistem mengasumsikan semua variabel non-negatif.
""")
