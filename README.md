# De Stem van de Amstel - een waternet hackathon

Tijdens deze hackathon duik je in de wereld van waterkwaliteit in de Amstel. Wat gebeurt er eigenlijk in de rivier? Hoe gezond is het water? En hoe kun je dat op een boeiende manier laten zien of vertellen?

Laat je creativiteit de vrije loop:

💧 Visualiseer de data: Bouw een interactieve website of app waarin je waterkwaliteitsdata tot leven brengt. Maak trends zichtbaar, zoom in op specifieke meetpunten of laat gebruikers zelf verkennen wat er in het water gebeurt.

🗣️ Praat met de rivier: Ontwikkel een chatbot die vragen over de waterkwaliteit beantwoordt. Met Text-to-Speech geef je de Amstel letterlijk een stem – hoe zou de rivier klinken als hij zelf kon praten?

🔍 Combineer en verrijk: Denk verder dan alleen de Waternet meetgegevens. Wat als je regendata toevoegt om verbanden te leggen tussen neerslag en vervuiling? Of gebruik lokale nieuwsartikelen en wetenschappelijke publicaties om context te geven aan wat je ziet in de data.

Ontdek de kracht van data en help de Amstel haar verhaal te vertellen!
Meer algemene informatie en het programma kun je vinden op: https://hackathon.waternet-events.nl/.

## Voorbereiden op de hackathon
Om goed voorbereid aan de hackathon te beginnen, hebben we alvast een aantal bronnen en tips verzameld.  
Neem vooral de tijd om hier doorheen te gaan, zodat je tijdens de dag zelf sneller aan de slag kunt.

### Informatieve links:
- [RIVM](https://rvs.rivm.nl/onderwerpen/normen/milieu/oppervlaktewater) - Normen stoffen voor oppervlaktewater kwaliteit
- [Wat is mijn waterkwaliteit](https://watismijnwaterkwaliteit.nl/gebieden/BoezemAmstelland-West) - Informatie waterkwaliteit in Boezem Amstelland-West
- [Aquo-kit](https://www.waterkwaliteitsportaal.nl/Aquo-kit) - Tool die gebruikt wordt voor het berekenen van oppervlaktewater kwaliteit
- [STOWA](https://www.stowa.nl/publicaties/referenties-en-maatlatten-voor-natuurlijke-watertypen-voor-de-kaderrichtlijn-water-2021-2027-versie) - Maatlatten Kaderrichtlijn water

### Inspiratie links
- [Deltares](https://www.deltares.nl/nieuws/werelds-eerste-drijvende-stem-van-de-natuur-verklapt-waterkwaliteit) - Drijvende stem Waterkwaliteit
- [Sensingclues](https://www.sensingclues.org/wildchats) - GenAI-powered conversations with animals
- [NOS](https://nos.nl/regio/limburg/artikel/498094-kunstmatige-intelligentie-geeft-de-maas-een-stem) - Kunstmatige intelligentie geeft de maas een stem

### Documenten
Wil je je alvast inlezen in de achtergrond?  
Ga naar de [`docs`](./docs) folder voor informatie over:
- [De Amstel](./docs/Amstelland_Onepager.pdf)
- [Beoordeling en maatregelen per jaar in factsheets over de Amstelboezem](./docs/factsheets)
- [Maatlatten STOWA kader richtlijn water](./docs/STOWA_2018-49-Maatlatten%20v2024%20DEF.pdf) uitleg hoe de berekening oppervlaktewater kwaliteit wordt gedaan en wat de eisen zijn
- [**OpenAI API** en **Open-WebUI**](./docs/openai%20keys%20en%20open%20webui.pdf) Een korte uitleg hoe je OpenAI API en Open-WebUI kunt opzetten en gebruiken.
- [Activeren en authoriseren GEE](./docs/Activating%20and%20Authenticating%20Google%20Earth%20Engine.pdf)

### Data
Tijdens de hackathon krijg je toegang tot grote datasets over oppervlaktewaterkwaliteit.
Een uitgebreid overzicht en uitleg vind je in [DATA.md](./DATA.md).

Openbare databases zijn natuurlijk ook toegestaan om gebruik van te maken. Een voorbeeld hiervan is:
- [KNMI](https://www.knmi.nl/nederland-nu/klimatologie-metingen-en-waarnemingen) - Website met uitgebreide toegang tot actuele én historische neerslagdata

### Handige tools:
In de hackathon werk je in groepen van 5. Per groep krijg je een OpenAI key. Deze kan je gebruiken om met een LLM te communiceren. Een handige interface tool voor verschillende taal modellen te gebruiken is Open-WebUI. Het zou fijn zijn als deze al voor de hackathon geïnstalleerd kan zijn op je laptop. In [Open-WebUI notebook](./docs/openai%20keys%20en%20open%20webui.pdf) kun je vinden hoe je deze alvast kan installeren. De OpenAI key krijg je op de dag zelf.

- [OpenAI platform](https://platform.openai.com/docs/overview) - OpenAI modellen
- [Open-WebUI](https://github.com/open-webui/open-webui) - GitHub Open-WebUI om te installeren

Onderstaand zijn nog andere interessante tools die je op de dag zelf kunt gebruiken om de Amstel haar verhaal te laten vertellen!
- [Suno](https://suno.com/home) - maak een liedje 
- [Gemini](https://gemini.google/overview/video-generation/) - video genereren
- [Ollama](https://ollama.com/) - gebruik andere taal modellen

### Tutorials
Kijk alvast in de [`tutorials`](./tutorials) folder.  

Daar vind je onder andere:
- Voorbeelden van de beschikbare data (met uitleg hoe je die kunt inladen en verkennen).  
- Google Earth Engine (GEE) tutorials met codevoorbeelden
