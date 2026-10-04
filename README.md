# Speculum Arcanorum · Atlas Tarot

Experiencia interactiva sobre los 22 Arcanos Mayores del Tarot de Marsella, leídos con C. G. Jung, Sallie Nichols y Alejandro Jodorowsky. Sitio estático, sin dependencias ni paso de compilación.

- `public/index.html`: toda la experiencia (HTML, CSS y JS en un solo archivo).
- `public/img/`: estampas en WebP (`NN.webp` 768×1536 y `NN-384.webp` para miniaturas) y `og.jpg`.
- `public/fonts/`: IM Fell English y EB Garamond (SIL Open Font License), autoalojadas.

## Probar en local
    cd public && python3 -m http.server 8000

Para recolocar los puntos de lectura sobre las cartas, abre `?calibrar`.

## Deploy
Cada push a `main` se publica en https://atlas-tarot.web.app mediante GitHub Actions (necesita el secret `FIREBASE_SERVICE_ACCOUNT_ATLAS_TAROT`). Las pull requests generan un canal de vista previa.

Deploy manual: `firebase deploy --only hosting`.

## Transparencia
Estampas generadas con IA (Midjourney) bajo dirección artística humana. Textos y código desarrollados con asistencia de Claude (Anthropic) y revisados por la autoría humana.
