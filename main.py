from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse

app = FastAPI()

# Sabit stok veritabanı (Vercel'de dosya bulamama sorununu %100 çöker ve uçuk hız sağlar)
STOKLAR = [
    {"UrunKodu": "CNT-01", "UrunAdi": "310luk Siyah Conta", "Fiyat": 150.0, "StokAdeti": 450},
    {"UrunKodu": "CNT-02", "UrunAdi": "320cük Çelik Conta", "Fiyat": 220.0, "StokAdeti": 0},
    {"UrunKodu": "VLV-05", "UrunAdi": "Pirinç Vana 1/2", "Fiyat": 450.0, "StokAdeti": 12}
]

@app.get("/", response_class=HTMLResponse)
def anasayfa(q: str = Query(None)):
    sonuclar_html = ""
    if q:
        q_lower = q.lower()
        filtreli = [
            row for row in STOKLAR 
            if q_lower in str(row.get('UrunAdi', '')).lower() or q_lower in str(row.get('UrunKodu', '')).lower()
        ]
        
        for index, row in enumerate(filtreli):
            stok_adet = row.get('StokAdeti', 0)
            stok_var = stok_adet > 0
            urun_kodu = row.get('UrunKodu', '')
            urun_adi = row.get('UrunAdi', '')
            fiyat = row.get('Fiyat', 0)
            
            if stok_var:
                stok_durum = f"Stokta Var ({stok_adet} adet)"
                renk = "#157a3a"
                buton_html = f'''
                <div style="display: flex; gap: 8px; align-items: center; margin-top: 10px;">
                    <div style="display: flex; border: 1px solid #cbd5e1; border-radius: 6px; overflow: hidden; background: #fff;">
                        <button onclick="adetDegistir({index}, -1)" style="background: #f1f5f9; border: none; padding: 8px 12px; cursor: pointer; font-weight: bold; font-size: 14px;">-</button>
                        <input type="number" id="adet_{index}" value="1" min="1" max="{stok_adet}" style="width: 40px; text-align: center; border: none; font-size: 14px; outline: none;" readonly>
                        <button onclick="adetDegistir({index}, 1, {stok_adet})" style="background: #f1f5f9; border: none; padding: 8px 12px; cursor: pointer; font-weight: bold; font-size: 14px;">+</button>
                    </div>
                    <button onclick="sepeteEkle('{urun_kodu}', '{urun_adi}', {index})" 
                            style="flex-grow: 1; background: #0f2744; color: white; border: none; padding: 9px 12px; border-radius: 6px; font-weight: 600; font-size: 13px; cursor: pointer;">
                        Sepete Ekle
                    </button>
                </div>'''
            else:
                stok_durum = "Tükendi"
                renk = "#b42318"
                buton_html = '''
                <div style="margin-top: 10px;">
                    <button disabled style="width: 100%; background: transparent; border: 1px solid #cbd5e1; color: #94a3b8; padding: 9px; border-radius: 6px; font-weight: 600; font-size: 13px; cursor: not-allowed;">
                        Tükendi
                    </button>
                </div>'''
            
            try:
                fiyat_formatli = f"{float(fiyat):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + " ₺"
            except:
                fiyat_formatli = f"{fiyat} ₺"

            sonuclar_html += f"""
            <div style="background: #ffffff; border: 1px solid #e2e8f0; padding: 12px; margin-bottom: 10px; border-radius: 8px; box-shadow: 0 1px 2px rgba(0,0,0,0.02);">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 6px;">
                    <div>
                        <span style="font-size: 11px; font-weight: bold; background: #f1f5f9; color: #0f2744; padding: 2px 6px; border-radius: 4px;">{urun_kodu}</span>
                        <h3 style="margin: 6px 0 0 0; color:#0f172a; font-size: 14px; font-weight: 600;">{urun_adi}</h3>
                    </div>
                    <div style="text-align: right;">
                        <span style="font-size: 15px; font-weight: 700; color:#0f172a; font-variant-numeric: tabular-nums;">{fiyat_formatli}</span>
                    </div>
                </div>
                <div style="font-size: 12px; margin-bottom: 4px;">
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
            <script>
                let sepet = JSON.parse(localStorage.getItem('b2b_sepet')) || {{}};

                function adetDegistir(index, miktar, maxStok) {{
                    let input = document.getElementById('adet_' + index);
                    let mevcut = parseInt(input.value) || 1;
                    let yeni = mevcut + miktar;
                    if (yeni < 1) yeni = 1;
                    if (maxStok && yeni > maxStok) yeni = maxStok;
                    input.value = yeni;
                }}

                function sepeteEkle(kod, ad, index) {{
                    let adet = parseInt(document.getElementById('adet_' + index).value) || 1;
                    sepet[kod] = {{ ad: ad, adet: adet }};
                    localStorage.setItem('b2b_sepet', JSON.stringify(sepet));
                    sepetiGuncelle();
                    
                    let btn = event.target;
                    let eskiText = btn.innerText;
                    btn.innerText = "Eklendi ✓";
                    btn.style.background = "#157a3a";
                    setTimeout(() => {{
                        btn.innerText = eskiText;
                        btn.style.background = "#0f2744";
                    }}, 1000);
                }}

                function sepettenCikar(kod) {{
                    delete sepet[kod];
                    localStorage.setItem('b2b_sepet', JSON.stringify(sepet));
                    sepetiGuncelle();
                }}

                function sepetiGuncelle() {{
                    let listeDiv = document.getElementById('sepet-listesi');
                    let sayacSpan = document.getElementById('sepet-sayac');
                    let altBar = document.getElementById('sepet-alt-bar');
                    
                    listeDiv.innerHTML = '';
                    let toplamUrun = 0;
                    let mesajMetni = "Merhaba, aşağıdaki ürünlerden sipariş vermek istiyorum:\\n";

                    for (let kod in sepet) {{
                        toplamUrun++;
                        let item = sepet[kod];
                        mesajMetni += "- " + kod + " " + item.ad + " x " + item.adet + " adet\\n";
                        
                        listeDiv.innerHTML += `
                            <div style="display: flex; justify-content: space-between; align-items: center; background: #f8fafc; padding: 8px 12px; margin-bottom: 6px; border-radius: 6px; font-size: 13px;">
                                <div><b>${kod}</b> - ${item.ad} <span style="color:#64748b;">(${item.adet} ad)</span></div>
                                <button onclick="sepettenCikar('${kod}')" style="background:none; border:none; color:#b42318; cursor:pointer; font-weight:bold;">Sil</button>
                            </div>
                        `;
                    }}

                    sayacSpan.innerText = toplamUrun;
                    if (toplamUrun > 0) {{
                        altBar.style.display = 'block';
                    }} else {{
                        altBar.style.display = 'none';
                        listeDiv.innerHTML = '<p style="text-align:center; color:#64748b; font-size:13px; margin:10px 0;">Sepetiniz boş.</p>';
                    }}
                    
                    window.whatsappMesaji = mesajMetni;
                }}

                function whatsappGonder() {{
                    let tel = "905555555555";
                    let url = "https://wa.me/" + tel + "?text=" + encodeURIComponent(window.whatsappMesaji);
                    window.open(url, '_blank');
                }}

                window.onload = function() {{
                    sepetiGuncelle();
                }};
            </script>
        </head>
        <body style="font-family: ui-sans-serif, system-ui, 'Segoe UI', sans-serif; max-width: 600px; margin: 0 auto; padding: 0 0 80px 0; background-color: #f6f7f9; color: #0f172a;">
            
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

            <div id="sepet-alt-bar" style="display: none; position: fixed; bottom: 0; left: 0; right: 0; background: #ffffff; border-top: 1px solid #cbd5e1; padding: 12px 16px; box-shadow: 0 -4px 12px rgba(0,0,0,0.08); max-width: 600px; margin: 0 auto; z-index: 100;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <span style="font-weight: 700; font-size: 14px; color: #0f2744;">🛒 Sepetim (<span id="sepet-sayac">0</span> Ürün)</span>
                    <button onclick="whatsappGonder()" style="background: #25D366; color: white; border: none; padding: 10px 16px; border-radius: 6px; font-weight: bold; font-size: 14px; cursor: pointer;">
                        WhatsApp ile Sipariş Gönder 🚀
                    </button>
                </div>
                <div id="sepet-listesi" style="max-height: 120px; overflow-y: auto; border-top: 1px solid #f1f5f9; padding-top: 6px;"></div>
            </div>

        </body>
    </html>
    """
    return html_icerik