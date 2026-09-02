# Fontes do catálogo regional

O catálogo inicial usa referências geográficas públicas apenas para localizar a praia. **Buracos, canais, coroas, estruturas, riscos e acessos específicos não são inventados pelo seed**: esses dados devem ser cadastrados no backoffice após validação local.

## Referências geográficas

| Praia | Município no catálogo | Latitude | Longitude | Referência |
|---|---|---:|---:|---|
| Praia de Itaúna | Saquarema | -22.93598 | -42.44065 | OpenStreetMap/Mapcarta: https://mapcarta.com/pt/W46963508 |
| Praia da Vila | Saquarema | -22.93451 | -42.50155 | OpenStreetMap/Mapcarta: https://mapcarta.com/pt/W1287775556 |
| Praia de Jaconé | Saquarema | -22.93734 | -42.64155 | GeoNames/Mapcarta: https://mapcarta.com/pt/36393812 |
| Praia de Barra Nova | Saquarema | -22.93300 | -42.58500 | UFRJ, tabela de praias amostradas: https://pantheon.ufrj.br/bitstream/11422/28086/1/962247.pdf |
| Praia de Massambaba | Arraial do Cabo | -22.93667 | -42.31499 | GeoNames/Wikidata/Mapcarta: https://mapcarta.com/pt/19262194 |
| Praia Grande | Arraial do Cabo | -22.96644 | -42.02239 | Apple Maps, referência geográfica pública: https://maps.apple.com/place?auid=13408026279516079296 |
| Praia do Foguete | Cabo Frio | -22.91781 | -42.03436 | OpenStreetMap/Mapcarta: https://mapcarta.com/pt/W293327504 |
| Praia do Peró | Cabo Frio | -22.861328 | -41.985153 | INEA, estação de amostragem de praias: https://www.inea.rj.gov.br/wp-content/uploads/2018/12/Coordenadas-Geogr%C3%A1ficas-das-Esta%C3%A7%C3%B5es-de-Amostragem-Praias.pdf |

## Qualidade editorial

`sea_bearing_deg`, perfil de praia e relações do Neo4j são uma **base editorial operacional** para o motor de recomendação e não devem ser tratados como levantamento topográfico, laudo ambiental ou garantia de captura. O painel administrativo existe para refinar esses dados com observação local.

A plataforma deve sempre apresentar recomendações como apoio informativo. Segurança, legislação, unidades de conservação, acesso à faixa de areia, condições de corrente e sinalização local prevalecem sobre qualquer score ou recomendação automatizada.
