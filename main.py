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
            stok_durum = f"Stokta Var ({row['StokAdeti']} adet)" if row['StokAdeti'] > 0 else "Tükendi"
            renk = "green" if row['StokAdeti'] > 0 else "red"
            
            wa_mesaj = f"Merhaba, {row['UrunKodu']} - {row['UrunAdi']} ürününden sipariş vermek istiyorum."
            wa_link = f"https://wa.me/905555555555?text={wa_mesaj}"
            
            sonuclar_html += f"""
            <div style="border: 1px solid #ddd; padding: 15px; margin-bottom: 15px; border-radius: 8px; background-color: #fafafa;">
                <h3 style="margin-top:0; color:#333;">{row['UrunAdi']} <span style="color:#666; font-size:14px;">({row['UrunKodu']})</span></h3>
                <p style="font-size: 16px;">Fiyat: <b style="color:#000;">{row['Fiyat']} TL</b></p>
                <p>Durum: <span style="color: {renk}; font-weight: bold;">{stok_durum}</span></p>
                <a href="{wa_link}" target="_blank" style="display:inline-block; margin-top:5px; background: #25D366; color: white; padding: 10px 15px; text-decoration: none; border-radius: 5px; font-weight:bold;">WhatsApp ile Sipariş Yaz</a>
            </div>
            """
    
    html_icerik = f"""
    <html>
        <head>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>B2B Stok Sorgu</title>
        </head>
        <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2 style="text-align: center; color: #2c3e50;">Canlı Stok & Fiyat Arama</h2>
            <form method="get" style="display: flex; gap: 10px;">
                <input type="text" name="q" placeholder="Ürün kodu veya adı girin..." value="{q if q else ''}" style="flex-grow: 1; padding: 12px; border: 1px solid #ccc; border-radius: 6px; font-size: 16px;">
                <button type="submit" style="padding: 12px 20px; background-color: #2c3e50; color: white; border: none; border-radius: 6px; font-size: 16px; cursor: pointer;">Ara</button>
            </form>
            <hr style="margin: 25px 0; border: 0; border-top: 1px solid #eee;">
            <div>
                {sonuclar_html if q else "<p style='text-align:center; color:#7f8c8d;'>Lütfen yukarıdan arama yapınız.</p>"}
            </div>
        </body>
    </html>
    """
    return html_icerik