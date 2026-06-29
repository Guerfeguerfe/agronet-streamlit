from __future__ import annotations

from io import BytesIO

import qrcode


def gerar_qr_png(conteudo: str) -> bytes:
    qr = qrcode.QRCode(version=1, box_size=10, border=3)
    qr.add_data(conteudo)
    qr.make(fit=True)
    imagem = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    imagem.save(buffer, format="PNG")
    return buffer.getvalue()
