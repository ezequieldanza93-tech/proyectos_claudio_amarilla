# Catálogo de productos de cultivo — mercado argentino

Datos técnicos y de identificación de productos de cultivo que se venden en Argentina, para la app **Brújula**: sugerencias de marca y modelo, dosis por litro, fichas de equipamiento y sustratos.

- **Relevado:** 19/11/2026
- **Sin precios.** Cada producto tiene al menos una fuente con fecha de captura.
- Lo que no figura en ninguna fuente queda en `null`: **no se completó ningún dato por suposición.**

## Qué hay

| Archivo | Productos | Verificados | Con conflicto | Marcas |
|---|---:|---:|---:|---|
| `fertilizantes.json` | 22 | 22 | 2 | Cannabiogen (Delta 9), Mamboretá, Namaste, Top Crop |
| `foliares.json` | 40 | 40 | 0 | BioProyect, Green Leaf (4 en 1 / 6 en 1), La Pota, Mamboretá, Namaste, NoStress, Pangea, Power, Revienta, Top Crop, Vamp |
| `sustratos.json` | 40 | 40 | 3 | Biobizz, Cultivate, Growers, Landiner, Lizard, Silver, Terrafertil (Growmix), Vamp |
| `luces.json` | 62 | 61 | 3 | Amnesia (Eco y Cob YXO), Bioled, Cosmel, Growtech, GS Iluminación, Lux, Mars Hydro |
| `carpas.json` | 24 | 21 | 1 | cultivARG, Garden HighPro |
| `ventilacion.json` | 18 | 18 | 3 | Agroled, Garden HighPro, Growtech, Santa Planta, VT Fans |
| `clima.json` | 14 | 14 | 0 | Garden HighPro, Wentux |
| `geneticas.json` | 26 | 26 | 0 | BSF Seeds (autoflorecientes), Clon Factory (clones) |
| **Total** | **246** | **242** | **12** | |

Además:

- `marcas.json`: las marcas de cada categoría, para las sugerencias de la app.
- `marcas_sugeridas.json`: marcas argentinas que aparecieron durante el relevamiento y **no** se cargaron. Quedan para que las apruebes.
- `fuentes.csv`: una fila por fuente (`id, url, fuente_tipo, fecha_captura`). Son 364 fuentes de 34 dominios: 134 de fabricante, 69 de distribuidor y 161 de vendedor.
- `pendientes.md`: lo que no se pudo verificar, los conflictos y las decisiones que quedan para vos.
- `esquema/catalogo.schema.json`: el JSON Schema (draft 2020-12) que valida todos los archivos.
- `herramientas/`: los scripts para validar, unir, aplicar la verificación y revisar una muestra.

## Cómo se generó

1. **Fuentes, en orden de prioridad:** sitio del fabricante → distribuidor argentino → grow shop argentino. Las principales:
   - Sitios oficiales: Namaste, Mamboretá, Terrafertil, Vamp, Growtech, Amnesia, Wentux, BSF Seeds Argentina y Clon Factory.
   - La distribuidora **Santa Planta**, por su API pública de WooCommerce.
   - **38 grow shops argentinos con sitio propio** (Tiendanube, WooCommerce, Empretienda), leídos por su sitemap.
2. **Extranjeros:** la ficha de un fabricante de afuera se usó solo cuando una fuente argentina mostraba que el producto se vende acá.
3. **Mercado Libre no se usó.** Su `robots.txt` prohíbe todo a `ClaudeBot` y `Claude-User` en `www`, `articulo` y `listado`.
4. **Reglas de recorrido:** se respetó el `robots.txt` de cada sitio (incluido el `Crawl-delay: 60` de Amnesia), con pausas de al menos 1,5 s, sin login y sin evadir bloqueos (403, Cloudflare, bloqueo por país). Firecrawl no tenía créditos, así que se usaron Python `requests`, WebFetch y WebSearch.
5. **Reparto:** un agente por categoría, y cada marca con un solo dueño para no duplicar. Una segunda pasada completó las marcas que solo aparecían en Mercado Libre, buscándolas en los grow shops.
6. **Normalización:** las unidades son fijas (W, cm, µmol/s, µmol/J, m³/h, L, ml/L, g/L, °C, % HR, `4"`/`6"`). Los nombres van tal cual los escribe la marca. Las descripciones y notas están en español.

## Verificación de todo el catálogo

Cada producto se volvió a abrir en su fuente, en dos pasos:

1. Un verificador comparó **campo por campo** y marcó tres tipos de problema: valor distinto, dato que no está en la fuente, y dato que estaba en la fuente pero quedó vacío.
2. Un segundo verificador, independiente, intentó **refutar** cada observación. Solo se corrigió lo confirmado con **cita textual** de la fuente.

| Tramo | Productos | Correcciones confirmadas | Refutadas | Dudosas |
|---|---:|---:|---:|---:|
| Insumos y genéticas | 128 | 21 | 3 | 7 |
| Equipamiento | 103 | 26 | 4 | 12 |

- Dos correcciones confirmadas se **revirtieron** porque contradecían una regla:
  - **pH de Hydro P:** el verificador eligió un valor entre dos fuentes que no coinciden, y la regla dice no elegir.
  - **Marca de una Probox:** el verificador la dejó como «Garden», lo que creaba una marca suelta que no existe.
- **Las dudas se resolvieron con la regla de conflictos:** cuando dos fuentes no coinciden, el campo queda en `null` y los dos valores van a `conflictos`.
- **`verificado: true`** quiere decir que el producto pasó este doble chequeo sin dudas abiertas. Los 4 que quedan en `false` están detallados en `pendientes.md`.
- **Amnesia** se verificó aparte, respetando su `Crawl-delay: 60`: en el Eco 180w, `dimmer: true` no figuraba en la ficha y pasó a `null`.
- **Cob YXO de Amnesia** (15, agregados después por decisión de Ezequiel): se extrajeron de las fichas guardadas y se controló que cada número cargado figure en su ficha.

**Correcciones que hizo el orquestador, aparte de la verificación:**

- La dosis del «6 en 1» se había convertido de «tapas» a ml usando la equivalencia de otro producto (el 4 en 1). Quedó sin ml/L.
- Delta 9 pasó a `fertilizantes.json`, solo con la dosis de riego.
- Growmix quedó como línea de Terrafertil.
- La línea «Yacarí» se corrigió a «Yacaré», que es lo que dice la fuente.
- Se agregaron conflictos de pH y CE entre la web y el PDF de Terrafertil, y el de presentaciones de Namaste Detox.
- Se quitó un ventilador de la tienda de Growtech que no era de su marca.

## Revisión de muestra (10 productos al azar)

- **Cómo se eligieron:** al azar entre los 231 productos que había antes de sumar los Cob YXO, con semilla fija `2026-11-19`, así que se puede reproducir. Script: `python -P herramientas/revisar_muestra.py 10 2026-11-19`.
- **Cómo se revisaron:** se volvió a abrir cada fuente, se buscó cada dato no nulo en su texto y se revisó a mano lo que no apareció.

| Producto | Categoría | Campos | Resultado |
|---|---|---:|---|
| `growers-light-soil` | sustrato | 6 | OK (`uso_indicado: indoor` revisado a mano: la ficha dice «CULTIVO INTERIOR») |
| `clon-factory-arkham-polaris` | genética | 13 | OK |
| `cultivarg-classic-doble-120x60x160` | carpa | 11 | OK (bocas revisadas a mano: «extractor techo 2 de 6″», «ventilación 2 de 6″ zona alta», «intracción 2 de 6″ zona baja») |
| `bsf-seeds-orange-blossom-xxl-auto` | genética | 11 | OK |
| `top-crop-top-auto` | fertilizante | 4 | OK |
| `vamp-sustrato-magico` | sustrato | 3 | OK |
| `gs-iluminacion-panel-led-px430b` | luz | 10 | OK |
| `top-crop-calmag` | fertilizante | 5 | OK |
| `mamboreta-d` | foliar | 5 | OK |
| `nostress-aceite-de-neem` | foliar | 5 | OK |

**Resultado: 10 de 10 productos y 73 de 73 campos coinciden con la fuente.** 72 se confirmaron por búsqueda automática y 1 a mano. No apareció ningún dato inventado ni ningún valor distinto al de la fuente.

## Fotos (`imagen_url`)

**243 de 246** productos tienen el link a su foto. En la app aparece el botón **«Foto»**, que abre ese link en otra pestaña. Solo se guarda el link: las imágenes no se copian al repo.

- **De dónde sale:** de una página que ya es fuente del producto, en orden fabricante → distribuidor → vendedor. Es la imagen principal que declara la página (`og:image`). En Santa Planta sale de su API, y en Amnesia de la imagen principal de la ficha.
  - **Terrafertil:** la imagen del bloque `p-thumbnail` (la bolsa), no la del banner.
  - **Namaste:** la imagen que declara el código del sitio oficial.
  - **Clon Factory:** la foto del esqueje, cuyo archivo lleva el nombre del clon.
- **Cómo se controló:**
  - se descartan logos y banners (una tienda declaraba su logo como foto);
  - se revisaron a ojo todas las fotos de Terrafertil y una muestra al azar de 20 del resto, y todas coinciden con el producto;
  - se comprobó que cada link responda con una imagen.
- **Sin foto (3):**
  - `terrafertil-growmix-master-e` y `terrafertil-growmix-citrus-ii`: la página del fabricante muestra la bolsa de **otro** producto (Master E/P y Citrus).
  - `clon-factory-billy-seeds-purple-karma`: la única imagen candidata tiene la etiqueta «BSOD74», que es otro clon.
- **Fotos compartidas:** algunos productos hermanos comparten foto porque así la publica la fuente. Por ejemplo, Wentux Pro-26 y Pro-26 6s, o la bolsa genérica «Específico» de Growmix.
- Script: `python -P herramientas/agregar_fotos.py buscar | completar | aplicar`. Respeta el `robots.txt`, hace pausas por dominio y guarda caché en `.cache/`.

## Convenciones de los campos

- **Comunes:** `id`, `categoria`, `marca`, `linea`, `producto`, `modelo`, `descripcion_corta`, `fuentes`, `conflictos` y `verificado`.
  - Opcional `notas`, en español, para aclarar de dónde sale un dato o por qué falta.
  - Opcional `imagen_url`, el link a la foto (ver arriba).
- **`conflictos`:** `[{"campo": "...", "valores": [{"valor": ..., "url": "..."}, ...]}]`. El campo en sí queda en `null`.
- **`dosis_fabricante`:** `[{etapa, min, max, unidad_por_litro, detalle}]`. `detalle` lleva el contexto tal cual la fuente: semana, frecuencia, o qué significa «otra».
- **`presentaciones_ml`** (fertilizantes) y **`presentaciones`** (foliares) están en la unidad de `unidad` (ml o g): 1 L = 1000.
- **Potencia de luces:** `potencia_real_w` es el consumo. `potencia_anunciada_w` (opcional) es la del nombre comercial cuando difiere. Un PPFD (µmol/m²/s) nunca se carga como PPF (µmol/s): va a `notas`.
- **Agregados respecto del pedido original:**
  - categoría `genetica` (`geneticas.json`), con banco o vivero en `marca` y criador en `linea`;
  - `modo_aplicacion` en fertilizantes y foliares;
  - `potencia_anunciada_w` en luces;
  - `detalle` en las dosis.

## Validar y regenerar

Desde `catalogo/`:

```
python -P herramientas/armar.py validar                 # esquema + 0 sin fuente + 0 ids duplicados + campos en conflicto en null
python -P herramientas/armar.py indices                 # regenera marcas.json, fuentes.csv y marcas_sugeridas.json
python -P herramientas/revisar_muestra.py 10 2026-11-19 # revisión de muestra contra las fuentes
```

`armar.py unir <archivo.json>` vuelve a armar un archivo final desde `tmp/`, que no se sube al repo. **Pisa las correcciones de la verificación**, así que no hay que usarlo sobre archivos ya verificados.
