# Fresh Terms of Service (Session 10): sources and licences

These three documents are used to check ClauseGuard on real Terms of Service it has never seen. None of the three companies is in the UNFAIR-ToS dataset (not in its train, validation or test split). Their owners publish them under open licences, which allow us to store the text here with attribution.

| File | Document | Owner | Licence | Source (pinned commit) |
|---|---|---|---|---|
| `basecamp_terms.txt` | Terms of Service (Basecamp, HEY and other 37signals products), last updated January 6, 2023 | 37signals LLC | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | [basecamp/policies `terms/index.md`](https://github.com/basecamp/policies/blob/05fb1f9ddaaf604fc5816990fa66f3ffd7f0a462/terms/index.md) |
| `cloudup_terms.txt` | Cloudup Terms of Service, effective May 15, 2015 | Automattic Inc. | [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) | [Automattic/legalmattic `Terms of Service/Cloudup/EN-Terms-of-Service.md`](https://github.com/Automattic/legalmattic/blob/99aa482bf6b602645bcb50c47a68db48a76dbce0/Terms%20of%20Service/Cloudup/EN-Terms-of-Service.md) |
| `crowdsignal_terms.txt` | Crowdsignal Terms and Conditions | Automattic Inc. | [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) | [Automattic/legalmattic `Terms of Service/Crowdsignal/Crowdsignal Terms and Conditions.md`](https://github.com/Automattic/legalmattic/blob/99aa482bf6b602645bcb50c47a68db48a76dbce0/Terms%20of%20Service/Crowdsignal/Crowdsignal%20Terms%20and%20Conditions.md) |

**Changes made:** each file was converted from Markdown to plain text by `scripts/fresh_docs.py` (front matter, links, emphasis and list markers removed; one paragraph or list item per line). No words were changed. The two Automattic documents remain under CC BY-SA 4.0 in this converted form. The SHA-256 of each file and its sentence count are in `manifest.json`; `python scripts/fresh_docs.py --check` verifies them.

**Limits:** two of the three documents come from the same company (Automattic), and all three are from software companies, so this is a small check, not a representative sample of Terms of Service.

The labels the team adds to these documents (`data/fresh_labels/`) are our own work. They mark potentially unfair clauses in the eight UNFAIR-ToS categories; they are not legal advice and say nothing about whether these companies' terms are lawful.
