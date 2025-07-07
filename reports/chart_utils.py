# reports/chart_utils.py
import matplotlib.pyplot as plt
import io
import base64

def generate_pie_chart(categorized_entries):
    """
    Kördiagramot generál az ESG kategóriák szerinti adatpontok eloszlásáról.
    Visszaadja a képet base64 kódolású stringként.
    """
    labels = categorized_entries.keys()
    sizes = [len(entries) for entries in categorized_entries.values()]
    
    # Csak akkor generálunk diagramot, ha vannak adatok
    if not any(sizes):
        return None

    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')  # Biztosítja, hogy a diagram kör alakú legyen.
    plt.title('Adatpontok eloszlása ESG-pillérek szerint')

    # A diagramot egy memóriában lévő bufferbe mentjük képként
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    
    # A képet base64 stringgé alakítjuk, hogy beágyazhassuk a HTML-be
    image_base64 = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()
    
    return image_base64