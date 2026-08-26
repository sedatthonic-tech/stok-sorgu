from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
import pandas as pd
import os

app = FastAPI()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXCEL_DOSYASI = os.path.join(BASE_DIR, "stoklar.xlsx")

@app.get("/", response_class=HTMLResponse)
def anasayfa(q: str = Query(None)):
    try:
        df = pd.read_excel(EXCEL_DOSYASI)
    except Exception as e:
        return f"<html><body><h2>Excel okunamadı veya stoklar.xlsx bulunamadı.</h2><p>{e}</p></body></html>"
    
    sonuclar_html = ""
    if q:
        filtreli = df[df['UrunAdi'].str.contains(q, case=False, na=False) | df['UrunKodu'].str.contains(q, case=False, na=False)]
        for _, row in filtreli.iterrows():
            stok_adet = row['StokAdeti']
            stok_var = stok_adet > 0
            
            # Stok durumuna göre renk ve metin
            if stok_var:
                stok_durum = f"Stokta Var ({stok_adet} adet)"
                renk = "#157a3a"
                buton_html = f'''
                <a href="https://wa.me/905555555555?text=Merhaba,%20{row['UrunKodu']}%20-%20{row['UrunAdi']}%20ürününden%20sipariş%20vermek%20istiyorum." 
                   target="_blank" 
                   style="display:block; text-align:center; background: #0f2744; color: white; padding: 10px; text-decoration: none; border-radius: 6px; font-weight:bold; font-size:14px;">
                   WhatsApp ile Sipariş Yaz
                </a>'''
            else:
                stok_durum = "Tükendi"
                renk = "#b42318"
                buton_html = '''
                <button disabled 
                        style="display:block; width:100%; text-align:center; background: transparent; border: 1px solid #ccc; color: #888; padding: 10px; border-radius: 6px; font-weight:bold; font-size:14px; cursor:not-allowed;">
                    Tükendi (Sipariş Verilemez)
                </button>'''
            
            # Fiyat formatı (Türkçe format: 150,00 ₺)
            try:
                fiyat_formatli = f"{float(row['Fiyat']):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + " ₺"
            except:
                fiyat_formatli = f"{row['Fiyat']} ₺"

            sonuclar_html += f"""
            <div style="background: #ffffff; border-bottom: 1px solid #eee; padding: 12px; margin-bottom: 8px; border-radius: 8px; box-shadow: 0 1px 2px rgba(0,0,0,0.04);">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 6px;">
                    <div>
                        <span style="font-size: 12px; font-weight: bold; background: #f1f5f9; color: #0f2744; padding: 2px 6px; border-radius: 4px;">{row['UrunKodu']}</span>
                        <h3 style="margin: 6px 0 0 0; color:#0f172a; font-size: 15px; font-weight: 600;">{row['UrunAdi']}</h3>
                    </div>
                    <div style="text-align: right;">
                        <span style="font-size: 16px; font-weight: 700; color:#0f172a; font-variant-numeric: tabular-nums;">{fiyat_formatli}</span>
                    </div>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; font-size: 13px;">
                    <span style="color: {renk}; font-weight: 600;">● {stok_durum}</span>
                </div>
                {buton_html}
            </div>
            """
    
    html_icerik = f"""
    <html>
        <head>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>B2B Stok Sorgu</title>
        </head>
        <body style="font-family: ui-sans-serif, system-ui, 'Segoe UI', sans-serif; max-width: 600px; margin: 0 auto; padding: 0; background-color: #f6f7f9; color: #0f172a;">
            
            <!-- Yapışkan Üst Şerit -->
            <div style="position: sticky; top: 0; background: #ffffff; z-index: 10; padding: 12px 16px; border-bottom: 1px solid #e5e7eb; display: flex; justify-content: space-between; align-items: center;">
                <span style="font-weight: 700; font-size: 15px; color: #0f2744;">📦 Toptan Stok Paneli</span>
                <span style="font-size: 11px; color: #64748b; background: #f1f5f9; padding: 4px 8px; border-radius: 4px;">Güncelleme: Bugün</span>
            </div>

            <div style="padding: 16px;">
                <form method="get" style="display: flex; gap: 8px; margin-bottom: 16px;">
                    <input type="text" name="q" placeholder="Ürün kodu veya adı girin..." value="{q if q else ''}" 
                           style="flex-grow: 1; padding: 12px; border: 1px solid #cbd5e1; border-radius: 8px; font-size: 16px; outline: none; background: #fff;"
                           inputmode="search" autocomplete="off" autofocus>
                    <button type="submit" style="padding: 12px 20px; background-color: #0f2744; color: white; border: none; border-radius: 8px; font-size: 15px; font-weight: 600; cursor: pointer;">Ara</button>
                </form>

                <div>
                    {sonuclar_html if q else "<p style='text-align:center; color:#64748b; margin-top: 40px; font-size: 14px;'>Aramak istediğiniz ürünün kodunu veya adını yukarı yazın.</p>"}
                </div>
            </div>
        </body>
    </html>
    """
    return html_icerik