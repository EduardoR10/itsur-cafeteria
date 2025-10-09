from datetime import datetime

def generar_folio(seq: int) -> str:

    hoy = datetime.now().strftime("%Y%m%d")
    return f"{hoy}-{seq:04d}"
