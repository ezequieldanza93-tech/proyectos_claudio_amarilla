# Pendientes del catálogo

Relevamiento del 19/11/2026. Acá está lo que no se pudo verificar, los productos dudosos, los conflictos entre fuentes y las decisiones que quedan para vos.

## 1. Decisiones para vos

1. **«Advance»**: en Argentina no apareció ninguna línea «Advance». En los grow shops se abrevia así a **Advanced Nutrients** (ej. «Advance Big Bud»), que vende Santa Planta. No se cargó: está en `marcas_sugeridas.json`. ¿Es esa?
2. **«Delta 9»**: es un producto de **Cannabiogen** (bioestimulante de floración a base de algas), no una marca. Está en `fertilizantes.json` con marca «Cannabiogen», solo con la dosis de riego; la dosis foliar quedó en `notas`. No tiene relación con «Advance».
3. **«4 en 1» y «6 en 1»**: son los Preventivos de **Green Leaf** (neem, jabón potásico, diatomeas, canela; el 6 en 1 suma cola de caballo y ortiga). La dosis del 6 en 1 viene en «tapas» sin equivalencia en ml: quedó sin ml/L.
4. **Go Green**: no vende ventilación. «Go Green Argentina» vende fertilizantes, sustratos y paneles LED (en sugeridas). ¿Era otra marca, como «Grow Green»?
5. **SL Growled**: no hay prueba de que sea `growled.com.ar` (tienda «Grow Led», sin «SL» ni razón social). En los buscadores aparece solo en Mercado Libre, como importador de kits. No se cargó nada. ¿Tenés un link?
6. **Cogoshop**: su dominio redirige a su tienda oficial de Mercado Libre, y no aparece en ningún grow shop con sitio propio. Sin datos.
7. **Growmix Indoor**: no existe con ese nombre en el sitio de Terrafertil. Lo más parecido es **MultiPro Indoor** (20 L, línea de jardín), cargado como `terrafertil-multipro-indoor`. ¿Es ese?
8. **Mars Hydro**: en los grow shops argentinos figura como «Mars» (Mars Optoelectrónica). Se cargó como «Mars Hydro».
9. **Agroled**: no tiene sitio propio y no queda claro si es marca o tienda. Se cargaron 2 coolers porque así figura en los títulos.
10. **Bioled**: no se pudo confirmar que sea Bioledarg SRL.
11. **Lux**: la única fuente argentina con la marca es Kaizen Grow Shop.
12. **BSF autoflorecientes**: `sexo` quedó en null porque las fichas de las automáticas no dicen «feminizada».
13. **Mamboretá**: los cebos y granulados (BOLITA, B+R, GRILLO, MIREX-S), la pintura-trampa A-TRAPA y el hormiguicida KAPUT no se diluyen en agua. Están en `foliares.json` con la dosis en `notas`. ¿Los querés en la app?
14. **Garden HighPro Probox 80x80x160** de Santa Planta: no aclara si es Basic o Eco Pro. Puede ser el mismo producto que `garden-highpro-probox-ecopro-80x80x160`, y no se fusionó.
15. **VT Fans**: `vt-fans-cooler-4-220v` (Goblin) puede ser el mismo producto que `vt-fans-turbina-cooler-extractor-4-ruleman` (Ganga). No se fusionó.

## 2. Límites que afectaron la cobertura

- **Mercado Libre no se relevó.** Los `robots.txt` de `www`, `articulo` y `listado.mercadolibre.com.ar` dicen `User-agent: ClaudeBot / Claude-User — Disallow: /`, y se respetó. Lo que solo se vende ahí quedó afuera. La vía legítima es el conector oficial de Mercado Libre de claude.ai: ya está autorizado y se activa en una sesión nueva.
- **Firecrawl sin créditos** hasta el 21/11. Se usaron Python `requests`, WebFetch y WebSearch (que solo ve resultados de EE. UU.).
- **Sitios bloqueados, no evadidos:** `cultivarg.com.ar` (403, «acceso solo desde Argentina»), `cosmel.com.ar` (Cloudflare), `topcrop.com` (403), `patagonianc.com.ar` (robots bloquea a ClaudeBot), El Grow Shop (Cloudflare).
- **`amnesiagrow.com.ar`** pide `Crawl-delay: 60` y bloquea las URLs con «?». Se respetó: un pedido por minuto desde el sitemap.
- Las búsquedas internas de varias Tiendanube (`/search/`) están prohibidas por robots. Se usaron sus sitemaps.

## 3. Conflictos entre fuentes (14)

En cada uno el campo quedó en null y los valores están en `conflictos`, sin elegir ninguno.

- `namaste-clonaste` · **presentaciones_ml**: `"300 cc"` ([fuente](https://namastenutrientes.com)) vs `"30 cc"` ([fuente](https://santaplanta.com.ar/producto/namaste-clonaste-30-gr/))
- `namaste-detox` · **presentaciones_ml**: `[500, 2000]` ([fuente](https://namastenutrientes.com)) vs `[600, 5000]` ([fuente](https://santaplanta.com.ar/producto/namaste-detox-500-ml/))
- `terrafertil-growmix-hydro-p` · **ph_declarado**: `"50 – 55%"` ([fuente](https://terrafertil.com/productos/hydro-p/)) vs `"5.20 - 6.00"` ([fuente](https://terrafertil.com/wp-content/uploads/FT-Growmix_HydroP.pdf))
- `terrafertil-growmix-master-e-p` · **ce_declarada**: `"0,20 – 0,50 mS/cm"` ([fuente](https://terrafertil.com/productos/master-e-p/)) vs `"0,40 - 0,70 mS/cm"` ([fuente](https://terrafertil.com/wp-content/uploads/FT-Growmix_MasterEP.pdf))
- `terrafertil-growmix-z-floricultura` · **ph_declarado**: `"5,00 - 6,00"` ([fuente](https://terrafertil.com/productos/z-floricultura/)) vs `"5,00 - 5,80"` ([fuente](https://terrafertil.com/wp-content/uploads/FT-Growmix_ZFloricultura.pdf))
- `terrafertil-growmix-z-floricultura` · **ce_declarada**: `"0,20 - 0,60 mS/cm"` ([fuente](https://terrafertil.com/productos/z-floricultura/)) vs `"0,20 - 0,80 mS/cm"` ([fuente](https://terrafertil.com/wp-content/uploads/FT-Growmix_ZFloricultura.pdf))
- `mars-hydro-infinitta-225` · **potencia_real_w**: `220` ([fuente](https://goblin.com.ar/cultivo-indoor/iluminacion/paneles-led/mars-leds-infinitta-225)) vs `225` ([fuente](https://gangagrow.com.ar/productos/mars-panel-led-infinitta-225-225w/))
- `mars-hydro-marsmachine-225cx` · **potencia_real_w**: `225` ([fuente](https://goblin.com.ar/cultivo-indoor/iluminacion/paneles-led/mars-leds-marsmachine-225cx)) vs `220` ([fuente](https://gangagrow.com.ar/productos/mars-panel-led-marsmachine-225cx-220w-kiu7l/))
- `mars-hydro-sunflash-153e` · **ppf_umol_s**: `"~379 a 390 µmol/s (PPF total)"` ([fuente](https://goodsmokegrow.com.ar/productos/led-mars-sunflash-153e-pabec/)) vs `"379 µmol/s/m² (PPFD a 30 cm, no PPF)"` ([fuente](https://goblin.com.ar/cultivo-indoor/iluminacion/paneles-led/mars-leds-sunflash-153-e))
- `garden-highpro-probox-basic-100x100x200` · **ventanas**: `3` ([fuente](https://www.growshopping.com.ar/productos/carpa-probox-basic-100-x-100-x-200-indoor-garden-highpro/)) vs `2` ([fuente](https://lacasadelcultivo.com.ar/productos/carpas-garden-highpro-cultivo-indoor-profesional-100x100x200/))
- `agroled-cooler-turbina-4-ruleman-220v` · **rpm**: `2600` ([fuente](https://www.upgrowshop.com/productos/cooler-turbina-agroled-220v-4-pulgadas-ruleman-indoor-up/)) vs `2700` ([fuente](https://gangagrow.com.ar/productos/agroled-turbina-cooler-4-con-ruleman-irmh1/))
- `agroled-cooler-turbina-4-ruleman-220v` · **caudal_m3h**: `135.9` ([fuente](https://kaizengrowshop.com/productos/cooler-ruleman-220v-4-agroled/)) vs `84.9` ([fuente](https://gangagrow.com.ar/productos/agroled-turbina-cooler-4-con-ruleman-irmh1/)) vs `95` ([fuente](https://www.upgrowshop.com/productos/cooler-turbina-agroled-220v-4-pulgadas-ruleman-indoor-up/))
- `garden-highpro-profan-extractor-4-15w` · **rpm**: `2300` ([fuente](https://www.upgrowshop.com/productos/extractor-axial-inline-garden-high-pro-profan-4-pulgadas/)) vs `2200` ([fuente](https://www.upgrowshop.com/productos/extractor-axial-inline-profan-4-pulgadas-cultivo-indoor/))
- `garden-highpro-profan-clip-fan-20w-oscilante` · **diametro**: `"15 cm"` ([fuente](https://www.upgrowshop.com/productos/ventilador-profesional-garden-high-pro-oscilante-clipfan-20w-15cm/)) vs `"20 cm"` ([fuente](https://cultivourbano.com.ar/cultivadores/herramientas/ventilador-oscilante-indoor-profan-garden-highpro-carpa-clip))

## 4. Productos sin sus datos clave

Productos cargados (sirven para sugerir marca y modelo) cuyas fuentes no dan ninguno de los datos técnicos principales de su categoría. Por ejemplo: luz sin potencia real ni PPF, sustrato sin litros, pH ni CE, fertilizante sin dosis ni presentaciones.

- **Bioled** (3): `bioled-330i`, `bioled-440i`, `bioled-pf-100`
- **Garden HighPro** (2): `garden-highpro-profan-extractor-100`, `garden-highpro-humipro-4l`
- **Growtech** (2): `growtech-quantum-q150`, `growtech-quantum-q300`
- **GS Iluminación** (3): `gs-iluminacion-panel-led-mx150`, `gs-iluminacion-panel-led-mx200`, `gs-iluminacion-panel-led-mx300`
- **Lux** (5): `lux-eco-full-spectrum-200w`, `lux-eco-full-spectrum-300w`, `lux-eco-full-spectrum-400w`, `lux-eco-full-spectrum-600w`, `lux-samsung-yxo-eco-full-spectrum-600w`
- **Mamboretá** (1): `mamboreta-brillo-foliar`
- **Mars Hydro** (1): `mars-hydro-marsmachine-225cx`
- **Namaste** (1): `namaste-clonaste`
- **Vamp** (1): `vamp-sustrato-magico`
- **VT Fans** (2): `vt-fans-turbina-cooler-extractor-3-ruleman`, `vt-fans-turbina-cooler-extractor-4-ruleman`
- **Wentux** (9): `wentux-controlador-clima-pro-26`, `wentux-controlador-clima-pro-26-6s`, `wentux-controlador-co2-kit`, `wentux-controlador-co2-1-salida`, `wentux-controlador-co2-2-salidas`, `wentux-controlador-co2-dual`, `wentux-controlador-indoor-pro`, `wentux-sensor-co2-wifi`, `wentux-sensor-humedad-temperatura-wifi`

## 5. Verificación contra las fuentes

Cada producto se volvió a abrir en su fuente. Un primer verificador comparó campo por campo, y un segundo intentó refutar cada diferencia. Solo se corrigieron las diferencias confirmadas con cita textual de la fuente.

Abajo está todo lo que el segundo verificador dejó como **dudoso**. La mayoría ya quedó **resuelto como conflicto** (sección 3: campo en null y los dos valores guardados). También quedaron resueltos:

- **Cosmel Sunshine 600:** el `tipo` inferido pasó a null.
- **Pangea:** la descripción se toma literalmente del nombre del producto.
- **Clonaste, notas:** reflejan la indicación de Santa Planta (1 cm de tallo); el fabricante dice 2 cm.

Siguen **abiertos** solo los de los productos con `verificado: false`, al final de esta sección.

- `cultivarg-eco-100x100x200` · largo_cm: dudoso — La unica fuente: el titulo/URL dicen 100x100x200 pero el detalle dice 120 x 120 x 200; el texto es identico al de la pagina del modelo 120 (copiado). Fuente internamente contradictoria. (https://kaizengrowshop.com/productos/carpa-cultivarg-100x100x200-eco/)
- `cultivarg-eco-100x100x200` · ventanas: dudoso — El texto existe pero es boilerplate identico al de la pagina del modelo 120, que ademas dice 120x120 en el detalle; no es confiable para este modelo. (https://kaizengrowshop.com/productos/carpa-cultivarg-100x100x200-eco/)
- `cultivarg-eco-80x80x180` · ventanas: dudoso — Dos fuentes difieren: Astrogrow (https://www.astrogrow.com.ar/productos/carpa-cultivarg-eco-80x80x180/) lista 'Ventanas de intracción pasiva 2 zona baja' y 'Ventanas de acceso 2 en paredes laterales'; Goodsmoke describe una ventana inferior y no menciona ventanas de acceso. No es contradiccion estricta (Goodsmoke omite), pero no se elige. (https://goodsmokegrow.com.ar/productos/carpa-cultivarg-eco-80x80x180-1f4zs/)
- `garden-highpro-probox-basic-100x100x200` · ventanas: dudoso — Las fuentes discrepan: Growshopping dice '3 Ventanas para flujo de aire pasivo: 20 x 12 cm'; La Casa del Cultivo (https://lacasadelcultivo.com.ar/productos/carpas-garden-highpro-cultivo-indoor-profesional-100x100x200/) dice '2 ventanas de 2 x 12 pulgadas'. Conflicto ya registrado en el catálogo; dejar null es correcto. (https://www.growshopping.com.ar/productos/carpa-probox-basic-100-x-100-x-200-indoor-garden-highpro/)
- `garden-highpro-probox-propagator-s-60x40x40` · ventanas: dudoso — La fuente menciona una ventana de aire y una ventana transparente de observacion; la cita es real. Pero el esquema no define si 'ventanas' cuenta la de observacion, y las notas del catalogo ya describen ambas. UpGrowshop no menciona ventanas. Ambiguo entre 1 y 2. (https://www.growshopping.com.ar/productos/carpa-probox-propagator-60-x-40-x-40-indoor-garden-highpro/)
- `cosmel-sunshine-600` · tipo: dudoso — La fuente no dice 'Full spectrum' ni otro tipo del enum; es una clasificacion por inferencia (espectro blanco amplio), razonable pero no textual. (https://kaizengrowshop.com/productos/led-cosmel-sunshine-600w/)
- `gs-iluminacion-panel-led-mx50` · panel_largo_cm: dudoso — Solo Martinez Grow da medidas (25x15x15 cm, peso 5 kg), parecen medidas de embalaje y no del panel (cobertura 60x60, 65 W); Kaizen, Growshopping y Punto Verde no traen dimensiones. Además el orden largo/ancho/alto es ambiguo y la observación cubre un solo campo. (https://martinezgrow.com/producto/led-gs-mx50/)
- `mars-hydro-marsmachine-225cx` · potencia_real_w: dudoso — Fuentes en conflicto: gangagrow dice 'Potencia: 220W reales'; goblin (https://goblin.com.ar/cultivo-indoor/iluminacion/paneles-led/mars-leds-marsmachine-225cx) dice 225W. No se elige. (https://gangagrow.com.ar/productos/mars-panel-led-marsmachine-225cx-220w-kiu7l/)
- `mars-hydro-sunflash-153e` · ppf_umol_s: dudoso — goodsmokegrow da PPF ~379 a 390 µmol/s (y PPFD 635 a 30 cm); goblin.com.ar da 379 µmol/s/m² como PPFD a 30 cm. Es un rango aproximado, no un valor único, y las fuentes discrepan en qué mide el 379. (https://goodsmokegrow.com.ar/productos/led-mars-sunflash-153e-pabec/)
- `agroled-cooler-turbina-4-ruleman-220v` · caudal_m3h: dudoso — Fuentes en conflicto: Upgrowshop 95 m3/h; Kaizen 135.9 m3/h (80 CFM) https://kaizengrowshop.com/productos/cooler-ruleman-220v-4-agroled/; Gangagrow 84.9 m3/h (50 CFM) https://gangagrow.com.ar/productos/agroled-turbina-cooler-4-con-ruleman-irmh1/. El conflicto ya esta en el catalogo; no se elige. (https://www.upgrowshop.com/productos/cooler-turbina-agroled-220v-4-pulgadas-ruleman-indoor-up/)
- `agroled-cooler-turbina-4-ruleman-220v` · rpm: dudoso — Upgrowshop y Kaizen (50 Hz) dicen 2600; Gangagrow dice 2700 https://gangagrow.com.ar/productos/agroled-turbina-cooler-4-con-ruleman-irmh1/. Conflicto ya registrado en el catalogo. (https://www.upgrowshop.com/productos/cooler-turbina-agroled-220v-4-pulgadas-ruleman-indoor-up/)
- `garden-highpro-profan-extractor-4-15w` · rpm: dudoso — Dos fichas de Upgrowshop: esta dice 2300 y https://www.upgrowshop.com/productos/extractor-axial-inline-profan-4-pulgadas-cultivo-indoor/ dice 2200 (segun catalogo). Conflicto registrado; no se elige. (https://www.upgrowshop.com/productos/extractor-axial-inline-garden-high-pro-profan-4-pulgadas/)
- `namaste-clonaste` · presentaciones_ml: dudoso — Fabricante dice 300 CC, Santa Planta 30 CC; conflicto ya registrado en conflictos. Dejar [] hasta resolver. (https://namastenutrientes.com)
- `namaste-clonaste` · presentaciones_ml: dudoso — Misma discrepancia 300 vs 30 entre fuentes; el catálogo lo dejó vacío con conflicto documentado. (https://santaplanta.com.ar/producto/namaste-clonaste-30-gr/)
- `namaste-clonaste` · notas: dudoso — Las notas copian fielmente Santa Planta (cubrir 1 cm del tallo, 10 segundos, con pincel); el fabricante dice 2 cm basales sumergidos. Dos fuentes distintas, no error del catálogo. (https://namastenutrientes.com)
- `pangea-d-killer-diatomeas` · descripcion_corta: dudoso — La ficha solo dice 'PANGEA D-KILLER DIATOMEAS'; 'Tierra de diatomeas' es lectura directa del nombre y el catalogo ya aclara que la ficha no tiene descripcion. No es dato inventado claro. (https://santaplanta.com.ar/producto/pangea-d-killer-diatomeas-100-gr/)
- `terrafertil-growmix-master-e-p` · ce_declarada: dudoso — Dos fuentes del fabricante discrepan: la web dice 'CE | 1 | : | 0,20 – 0,50 mS/cm' y el PDF FT-Growmix_MasterEP.pdf dice 0.40 - 0.70 mS/cm (la web tambien difiere en humedad 55-60% vs 50-60%). El catalogo usa el PDF sin registrar conflicto; corresponde registrar conflicto, no elegir. (https://terrafertil.com/productos/master-e-p/)
- `terrafertil-growmix-z-floricultura` · ph_declarado: dudoso — Web dice 5,00 - 6,00 y la ficha PDF dice 5.00 - 5.80: dos fuentes del fabricante discrepan. (https://terrafertil.com/productos/z-floricultura/)
- `terrafertil-growmix-z-floricultura` · ce_declarada: dudoso — Web dice 0,20 - 0,60 y la ficha PDF dice 0.20 - 0.80 mS/cm: dos fuentes discrepan. (https://terrafertil.com/productos/z-floricultura/)

Productos con `verificado: false`: `amnesia-linea-eco-180w`, `gs-iluminacion-panel-led-mx50`, `cultivarg-eco-100x100x200`, `cultivarg-eco-80x80x180`, `garden-highpro-probox-propagator-s-60x40x40`.

## 6. No cargado y por qué

- **Kits, combos, packs y accesorios** sin dato técnico propio (filtros, ductos, poleas, timers, tijeras, mallas), en todas las marcas.
- **Namaste**: Nutripack (kit). El sitio oficial no publica dosis por litro. Las dosis de Shanti, Detox, Bio Protect y Bio Neem salen de Santa Planta.
- **Top Crop**: Green Explosion, Cyclone, Tripacks. Sin ficha del fabricante (403). Las dosis y el NPK salen de grow shops argentinos. Para Deeper Underground otras tiendas citan 1 ml/L y 2-4 ml/L, y no se cruzaron.
- **Biobizz**: fertilizantes y foliares (Santa Planta no trae dosis, y las de biobizz.com están en una tabla en imagen). All·Mix y versiones Peat Free: sin vendedor argentino verificable.
- **Vamp**: abonos y enmiendas (Bokashi, Vampkashi, Humuskashi, Polvos de Roca, Mulching), porque no hay categoría en el esquema. Hechizo Bloom y Boom: sin dosis.
- **Terrafertil**: línea GardenPro (paisajismo), turbas, perlita, vermiculita, enmiendas y semillas.
- **Santa Planta**: «Turbina Lateral 4 2026» y «Turbina Lineal 6 XXL 2026», porque la ficha no dice que sean de su marca. Datos disponibles: 400 m³/h, 58 W, 2800 rpm y 900 m³/h, 85 W, 2800 rpm.
- **Growtech**: deshumidificadores y humidificador sin marca nombrada, y outlet o reacondicionados. Lucius y Cogordo son otras marcas (en sugeridas).
- **Garden HighPro**: Mushpro, Master, Magnum, Bunker y Prohygro no aparecieron en fuentes argentinas. Las bocas de las carpas Basic quedaron en null porque las fuentes dan solo el total de mangas.
- **Mars Hydro**: Sunflash 225E, 420E/420CL, 659E, Orbiter 80/SL 120, Infinitta Lite 225 y Sunflash 710, porque no se leyó ninguna ficha técnica de esos modelos.
- **Cosmel**: sus controladores de clima y el expansor de potencia (solo en su sitio con Cloudflare y en Mercado Libre). Se cargaron sus LEDs (Kaizen).
- **cultivARG**: Eco 150 y 240 sin fuente leída. Faltan bocas en Eco 100/120 y Classic 100/120.
- **Clon Factory**: Fancy Gummy y Tropicana WFC se venden en grow shops pero no tienen ficha oficial.
- **BSF Seeds**: los 5 mixes automáticos (packs) y todas las fotoperiódicas (fuera del pedido).
- **Green Leaf «Jabón Potásico»** de Santa Planta: la descripción es la de un fertilizante (error de la ficha).
- **«NEEM PURO»** de Santa Planta: sin marca identificable.
