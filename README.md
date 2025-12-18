#  Platforma do Badania Jakości Wideo (QoE)

Aplikacja webowa stworzona w **Streamlit** służąca do przeprowadzania subiektywnych testów oceny jakości wideo (QoE - Quality of Experience).

Projekt został zaprojektowany zgodnie z metodologią badawczą, eliminując wpływ jakości łącza internetowego uczestnika na płynność odtwarzania wideo.

## Główne Funkcjonalności

* **Mechanizm "Download-then-Play":** Niestandardowy odtwarzacz wideo (JS/HTML), który wymusza pobranie 100% pliku do pamięci podręcznej przeglądarki przed umożliwieniem odtwarzania. Gwarantuje to brak "lagów" i zacięć sieciowych podczas oceny.
* **Faza Treningowa:** Użytkownik przechodzi obowiązkową fazę szkoleniową (2 filmy), której wyniki nie są wliczane do analizy końcowej (zgodnie z zaleceniami ITU-T).
* **Hosting Cloudflare R2:** Wykorzystanie darmowego transferu (zero egress fees) do serwowania ciężkich plików wideo.
* **Backend Google Sheets:** Automatyczny zapis metryczki demograficznej oraz ocen (MOS) w czasie rzeczywistym do Arkuszy Google.
* **Responsywność:** Aplikacja dostosowana do urządzeń mobilnych i desktopowych.

## https://video-qoe-test-cr4kqtcofajchzdjtt7p8q.streamlit.app
