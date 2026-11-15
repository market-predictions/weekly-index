# OUTCOME — weekly-index (wekelijks rapport, wereldwijde aandelenindices)

> **Doel bevestigd door de eigenaar op 2026-11-15.** De invulling van "klaar als" volgt bij de herbouw (ronde B).

**Doel:** Elke week een correct rapport over een modelportefeuille op wereldwijde aandelenindices bij de lezers, volgens het model van `weekly-etf-eu`.

**Klaar als:**
- Het rapport is op de vaste dag vóór het vaste tijdstip verzonden.
- De portefeuille-historie sluit op de cent; elk getal komt uit de feiten.
- Eén `acceptance.yml` toetst dit (te bouwen).

**Alleen met akkoord van de eigenaar:** ontvangers en live verzenden; beslisregels, universum en benchmark.

**Status:** laatste run van de wekelijkse workflow (na herbouw).

## Open vragen aan de eigenaar
- Hoe wordt een index "gekocht": via een ETF of tracker per index, of via futures/CFD's? Dat bepaalt de prijsdata en het rendement.
- Het spoor met AEX-opties: definitief stoppen?

## Besluiten
- 2026-11-15 — Overgestapt op het outcome-first model (control-plane). Oudere plan-, status- en controledocumenten in deze repo zijn niet meer leidend.
- 2026-11-15 — Actief project, niet dormant.
- 2026-11-15 — Herbouw volgens het model van `weekly-etf-eu`: vaste pijplijn (data → beslissen → feiten → tekst → rapport → mail), AI rekent nooit, één acceptatietoets.
