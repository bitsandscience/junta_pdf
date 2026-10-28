
from pathlib import Path
from pypdf import PdfReader, PdfWriter

# =====================================
# CONFIGURACIÓN
# =====================================

carpeta = Path(r"C:\Users\Carlos\Documents\junta_pdf")
salida = carpeta / "PDF_FINAL.pdf"
limite_kb = 1024


# =====================================
# FUNCIÓN PARA SELECCIONAR PÁGINAS
# =====================================

def seleccionar_paginas(total):
    """
    Permite introducir:
    1,3,5
    2-6
    1,3-5,8

    Devuelve índices de páginas empezando en 0.
    """

    while True:
        entrada = input(
            "\n¿Qué páginas quieres incluir? "
            "(Ejemplo: 1,3-5,8): "
        ).strip()

        try:
            paginas = []

            for parte in entrada.split(","):
                parte = parte.strip()

                if "-" in parte:
                    inicio, fin = map(
                        int, parte.split("-")
                    )

                    if inicio > fin:
                        raise ValueError()

                    paginas.extend(
                        range(inicio, fin + 1)
                    )
                else:
                    paginas.append(int(parte))

            if not paginas:
                raise ValueError()

            if any(p < 1 or p > total for p in paginas):
                print(
                    f"ERROR: las páginas deben estar "
                    f"entre 1 y {total}."
                )
                continue

            # Eliminar duplicados manteniendo orden
            paginas = list(dict.fromkeys(paginas))

            return [p - 1 for p in paginas]

        except ValueError:
            print(
                "Formato incorrecto. "
                "Ejemplo válido: 1,3-5,8"
            )


# =====================================
# BUSCAR PDFs
# =====================================

archivos = sorted(
    p for p in carpeta.glob("*.pdf")
    if p.name != salida.name
)

if not archivos:
    raise RuntimeError(
        "No se encontraron archivos PDF."
    )

writer = PdfWriter()

print("\n====================================")
print("    UNIR PDFs SELECCIONANDO PÁGINAS")
print("====================================")


# =====================================
# PROCESAR CADA PDF
# =====================================

for pdf in archivos:

    reader = PdfReader(str(pdf))
    total = len(reader.pages)

    print("\n------------------------------------")
    print(f"Archivo: {pdf.name}")
    print(f"Número de páginas: {total}")
    print("------------------------------------")

    while True:
        respuesta = input(
            "¿Quieres incluir TODAS las páginas? "
            "(s/n): "
        ).strip().lower()

        if respuesta in ("s", "si", "sí"):
            paginas = list(range(total))
            break

        elif respuesta in ("n", "no"):
            paginas = seleccionar_paginas(total)
            break

        else:
            print("Responde 's' o 'n'.")

    print(
        f"Se añadirán {len(paginas)} "
        f"páginas de {pdf.name}"
    )

    for numero in paginas:
        writer.add_page(reader.pages[numero])


# =====================================
# COMPRIMIR CONTENIDO
# =====================================

print("\nComprimiendo PDF...")

for i, pagina in enumerate(writer.pages, start=1):
    try:
        pagina.compress_content_streams()
    except Exception as e:
        print(
            f"No se pudo comprimir "
            f"la página {i}: {e}"
        )


# =====================================
# GUARDAR PDF FINAL
# =====================================

with open(salida, "wb") as f:
    writer.write(f)

total_paginas = len(writer.pages)

writer.close()


# =====================================
# COMPROBAR TAMAÑO
# =====================================

tamano_kb = salida.stat().st_size / 1024

print("\n====================================")
print("         RESULTADO FINAL")
print("====================================")

print(f"Archivo: {salida.name}")
print(f"Páginas totales: {total_paginas}")
print(f"Tamaño: {tamano_kb:.2f} KB")

if tamano_kb <= limite_kb:
    print("OK: el PDF cumple el límite de 1024 KB")
else:
    print("AVISO: el PDF supera los 1024 KB")

print("====================================")
