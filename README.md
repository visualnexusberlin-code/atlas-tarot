# Speculum Arcanorum · Atlas Tarot

Experiencia interactiva sobre los 22 Arcanos Mayores del Tarot de Marsella, leídos con C. G. Jung, Sallie Nichols y Alejandro Jodorowsky. Sitio estático, sin dependencias ni paso de compilación.

- `public/index.html`: toda la experiencia (HTML, CSS y JS en un solo archivo).
- `public/cartas/`: las 22 estampas en WebP (768×1536).
- `public/vendor/three.module.min.js`: Three.js 0.169 (MIT), autoalojado, para la sección de arquetipos.
- `public/img/og.jpg`: imagen para compartir en redes.
- Fuentes IM Fell English y EB Garamond (SIL OFL) incrustadas en el HTML.

## Versión inglesa
`public/en/index.html` se genera a partir del español; no se edita a mano:

    python3 tools/make_en.py

Los textos ingleses están en `tools/i18n_en.py`. Si cambias un texto en el español, el script se detiene y dice cuál ya no encuentra, para que la traducción no se quede atrás sin aviso.

## Probar en local
    cd public && python3 -m http.server 8000

Para recolocar los puntos de lectura sobre las cartas, abre `?calibrar`.

## Deploy
Cada push a `main` se publica en https://atlas-tarot.web.app mediante GitHub Actions (necesita el secret `FIREBASE_SERVICE_ACCOUNT_ATLAS_TAROT`). Las pull requests generan un canal de vista previa.

Deploy manual: `firebase deploy --only hosting`.

## Transparencia
Estampas generadas con IA (Midjourney) bajo dirección artística humana. Textos y código desarrollados con asistencia de Claude (Anthropic) y revisados por la autoría humana.
