# Quote Provenance And Source Surface Contract

**Version**: v0.1
**Status**: canonical for US quote-bearing thesis verification prompts and evidence review
**Applies to**: `research-thesis-verifier`, `research-thesis-drafter` when PM authorizes external search, `research-evidence-reviewer`
**Related**: [`evidence_source_trust_contract.md`](evidence_source_trust_contract.md), [`the_timestamp_semantic.md`](the_timestamp_semantic.md)

---

## 0. Authority

This contract starts from a quote, not from a known event.

The failure mode it prevents is attribution laundering: a secondary source says a person "opened with" or "will say" a phrase, and the verifier treats that sentence as a fact about the official event before discovering where the phrase actually appeared.

`evidence_source_trust_contract.md` answers whether a publisher is trustworthy enough to anchor `ai_verified=true`.

This contract answers three earlier questions:

1. What is the quote's provenance chain.
2. Which source surface actually supports the wording and claimed placement.
3. Once the event is identified, which US official or US issuer source must be checked.

This v0.1 contract is intentionally US-only for mandatory official-source checks. Non-US events use ordinary trust-tier judgment unless a future version admits the class.

---

## 1. Reader End-State

After reading a verifier or drafter output governed by this contract, the next reviewer should be able to tell:

- what exact quote or phrase was investigated
- who the quote was attributed to before verification
- which event, date, venue, and document family the search discovered
- whether the quote was found in an official source, a secondary source, or only a media preview
- which source surface supports the quote
- whether the claimed surface matches the found surface
- which official source patterns were attempted, and what each attempt returned
- whether the quote had prior public use before the discovered event

If the reviewer still has to infer whether a quote came from prepared testimony, delivered oral remarks, Q&A, media preview, or later paraphrase, the contract has not been satisfied.

---

## 2. Quote-First Provenance Workflow

When the input is a quote or phrase attributed to a person, do not start by assuming the event. First split the claim into open slots:

| Slot | Question |
|---|---|
| `quoted_text` | What exact phrase is being verified |
| `attributed_person` | Who is alleged to have said or written it |
| `claimed_event` | What event is alleged, if any |
| `claimed_surface` | Written statement, oral opening, Q&A, media preview, or paraphrase |
| `claimed_date` | What date is alleged, if any |
| `claimed_placement` | Opening line, later body, closing frame, answer to a question, or unspecified |

Treat all slots except `quoted_text` as unverified until the search discovers supporting surfaces.

### Search Order

Use this order before writing an evidence verdict:

1. Exact quote plus person.
2. Exact quote alone.
3. Key phrase plus person.
4. Key phrase variants plus person.
5. Prior-public-use check: search whether the exact quote or close slogan appeared before the discovered event.
6. Secondary-source extraction: read result snippets or pages only to extract date, venue, event title, document title, and surface labels such as `prepared remarks`, `opening statement`, `embargoed until delivery`, `transcript`, `he will say`, or `according to`.
7. Official-source lookup using the discovered event metadata.
8. Surface comparison: compare the claimed surface with the found surface.

Do not treat a secondary-source result as final proof. Use it to discover where the official or primary material should live.

---

## 3. Provenance Fields Required In Evidence Prose

Until schema promotes these into structured fields, verifier and drafter prose must make the following items recoverable for quote-bearing evidence:

| Item | Required content |
|---|---|
| `quoted_text` | Exact quote or phrase under verification |
| `attributed_person` | Person or institution the quote is attributed to |
| `discovered_event` | Event name / venue / committee / issuer call / filing family discovered by search |
| `discovered_event_date` | Date of the discovered event when available |
| `claimed_surface` | The surface implied by the original claim |
| `found_surface` | The surface where the quote was actually found |
| `semantic_status` | `semantic_true`, `semantic_false`, or `semantic_ambiguous` for the underlying meaning independent of exact wording and placement |
| `quote_status` | `verbatim_present`, `near_paraphrase`, `not_found_on_claimed_surface`, or `reported_by_secondary_only` |
| `prior_public_use` | Whether the exact quote or close slogan appeared before the discovered event |
| `official_source_attempts` | Official source patterns attempted and result for each |
| `source_time_relation_to_event` | Whether each secondary source was published before, during, or after the discovered event |

The prose may be compact, but a reviewer must be able to reconstruct the provenance chain without rerunning the search.

---

## 4. Source Surface Taxonomy

Every quote-bearing claim must name one found surface.

| Surface | Definition | Common failure |
|---|---|---|
| `written_submission` | Prepared statement, submitted testimony, published filing, official PDF, or written press release | Calling prepared text "delivered oral opening" |
| `oral_delivery_prefix` | The first delivered oral segment, usually courtesy, framing, and opening lines | Saying a later line was the opening line |
| `oral_delivery_main` | Later delivered remarks, hearing testimony body, Q&A answer, or speech body | Flattening the body into the prefix |
| `oral_delivery_closing` | Closing segment of opening remarks, closing statement, or final quoted frame | Calling the end of opening remarks the whole-event closing |
| `media_preview_before_event` | Pre-event article saying a person "will say" or previewing prepared remarks | Treating previewed prepared language as delivered verbatim |
| `post_event_paraphrase` | Post-event media summary, analyst paraphrase, headline framing, or excerpted interpretation | Treating paraphrase as a direct quote |

Placement claims must match the surface. `Opened orally with X` is supported only by `oral_delivery_prefix`. `Written opening statement contains X` is supported by `written_submission`.

### Surface-Time Discipline

A source published before the event start time can help discover prepared text and event metadata, but it cannot verify oral delivery. Any pre-event article with language such as `will say`, `prepared remarks`, `embargoed until delivery`, or `opening statement` maps to `media_preview_before_event` unless an official or transcript surface later confirms delivery.

For claims about what someone `said`, `opened with`, `testified`, or `answered`, the verifier must attempt an oral surface:

- official hearing transcript when posted
- official video or committee recording when available
- secondary transcript or video time-code when official transcript is not posted

Official written testimony can verify `written_submission`; it cannot by itself verify `oral_delivery_prefix`, `oral_delivery_main`, or `oral_delivery_closing`.

---

## 5. US Official Source Mapping After Event Discovery

Use this mapping only after quote-first search identifies a US official, US regulatory, US macro, or US issuer event.

| US event class | Mandatory official source pattern | Notes |
|---|---|---|
| `congressional_hearing` | `senate.gov`, `house.gov`, committee subdomain, `govinfo.gov`, `congress.gov` | Search hearing page, submitted testimony PDFs, official video or transcript when available |
| `fed_speech_or_testimony` | `federalreserve.gov`, relevant regional Fed domain, congressional source when testimony | Distinguish prepared remarks, delivered remarks, Q&A, and transcript |
| `fomc_statement` | `federalreserve.gov/monetarypolicy/fomccalendars.htm`, FOMC statement pages | Statement text is the primary surface |
| `fomc_minutes_or_vote` | `federalreserve.gov/monetarypolicy/fomcminutes*`, FOMC implementation notes | Minutes, vote record, implementation note are separate surfaces |
| `sec_filing` | `sec.gov/edgar`, issuer filing accession page | Company-hosted copy can supplement, EDGAR is mandatory |
| `company_earnings` | Company IR domain, SEC 8-K or 10-Q when applicable | IR release, deck, transcript, and filing are separate surfaces |
| `us_macro_data` | `bls.gov`, `bea.gov`, `census.gov`, `treasury.gov`, `federalreserve.gov`, `fred.stlouisfed.org` | Pick the agency that owns the series |
| `tariff_trade_action` | `ustr.gov`, `federalregister.gov`, `whitehouse.gov`, `cbp.gov` | Announcement, legal notice, implementation guidance are separate surfaces |
| `us_court_ruling` | US court website, `supreme.justia.com`, official docket where available | Media summary is not a ruling surface |
| `us_energy_data_or_policy` | `eia.gov`, `ferc.gov`, `energy.gov`, relevant US regulator or agency | Forecast report, inventory data, and policy release are separate surfaces |
| `financial_regulatory_action` | `cftc.gov`, `sec.gov`, `occ.gov`, `fdic.gov`, `federalreserve.gov`, `ferc.gov`, state PUC site | Regulator order or filing is mandatory |
| `us_sanctions_action` | `ofac.treasury.gov`, `treasury.gov`, `federalregister.gov`, `whitehouse.gov` | Press coverage cannot substitute for list entry or official notice |
| `us_antitrust_action` | `ftc.gov`, `justice.gov/atr`, `federalregister.gov` | Complaint, consent order, or decision text is the primary surface |

If the discovered event is not US-linked, record it as outside this contract's mandatory-source scope and use ordinary trust-tier judgment.

---

## 6. Official Source Attempt Proof

For US official or US issuer quote verification, the verifier must record proof of attempted official lookup.

| Field | Required content |
|---|---|
| `attempted_official_patterns` | Domains or URL patterns searched, such as `site:banking.senate.gov Warsh April 21 2026 testimony` |
| `official_source_results` | Per pattern: `found`, `not_posted_as_of_query_time`, `inaccessible`, `query_failed`, or `not_relevant` |
| `official_source_urls` | Official URLs found, or empty if none |
| `secondary_sources_used_for_discovery` | Secondary URLs used only to infer event metadata |
| `oral_surface_attempts` | Transcript or video surfaces checked when the claim is about oral delivery |

If Perplexity returns only T2/T3 sources, that is not evidence that official sources are unavailable. The verifier must perform direct official lookup against the patterns discovered above before writing a verdict.

---

## 7. Query Design Rule For Verbatim Claims

A verifier must split verbatim verification into at least two independent questions:

1. Open-ended provenance question: where does this quote or phrase appear, and what event metadata is attached.
2. Surface-location question: does the phrase appear on the claimed official surface.

A query that presumes the phrase exists in a claimed location creates confirmation bias. The failure signal is a prompt shaped like: `Quote the exact opening language including <phrase>`.

---

## 8. Escalation Rule

If the mandatory official source is not available after direct official lookup, the output must say so explicitly:

`Official source not available after attempted patterns <patterns>; secondary sources used as best-available discovery only; found_surface=<surface>; quote_status=<status>; ai_verified remains false until official confirmation exists.`

If a T2 or T3 source reports a quote that is absent from the available official surface, the caller must downgrade the attribution:

`reported by <source>; not found on <official surface> as of <query time>; attribution pending or secondary-only.`

Do not silently convert this into a verified direct quote.

---

## 9. Evidence-Reviewer Audit Expectations

When reviewing an `evidence_record`, `research-evidence-reviewer` must judge:

- `quote_provenance_audit`: whether the caller started from the quote and reconstructed person / event / date / surface instead of assuming the event
- `official_source_attempt_audit`: whether attempted official patterns and results are recorded
- `source_surface_attribution`: whether the quote or paraphrase is tied to one of the six source surfaces
- `semantic_truth_audit`: whether the underlying meaning is supported even when exact wording or surface attribution needs revision
- `verbatim_location_support`: whether the evidence supports both the wording and the claimed placement
- `surface_time_audit`: whether pre-event media was prevented from validating oral delivery
- `oral_surface_attempt_audit`: whether oral claims attempted transcript or video surfaces
- `prior_public_use_audit`: whether the quote's prior public use was checked when novelty or origin is implied
- `secondary_only_downgrade`: whether T2/T3-only claims were downgraded and kept `ai_verified=false`

These checks complement `source_trust_verdict`, `belief_delta_coherence`, and `response_supports_claim`. They do not replace them.

---

## 10. Aggregate Rule

`semantic_status` and `quote_status` answer different questions.

- `semantic_status=semantic_true` means the underlying meaning is supported.
- `quote_status` and `found_surface` describe exact wording and placement.

A surface mismatch does not automatically force `final_verdict=partial`. The aggregate verdict depends on the scoped claim in `evidence_summary`:

- If `evidence_summary` claims the original attribution is fully true, then a surface mismatch is `partial` or `rejected`.
- If `evidence_summary` explicitly scopes itself as `semantic_true + attribution correction`, then the evidence can be `verified` when official sources support the semantic claim and the surface correction is clearly stated.
- If oral delivery remains secondary-only, the evidence can still be `verified` for the scoped correction when it does not claim official oral proof. The rationale must state which oral surface remains secondary.

Do not use `semantic_true` to launder a false verbatim or placement claim. Use it only when the record explicitly says which part is true and which attribution layer needs revision.

---

## 11. Minimal Example

Input claim:

`Person X opened a confirmation hearing by saying "Y".`

Contract-compliant verification starts with the quote:

- search exact quote + person
- search exact quote alone
- use secondary results only to discover event metadata
- search official committee page and submitted testimony
- compare written statement, oral opening, oral body, and media preview surfaces

Possible verdict:

`semantic_true for the inflation-responsibility meaning if official written text or delivered oral variant supports the same claim; false for oral_delivery_prefix if the delivered first lines do not contain Y; true with revision for written_submission if the submitted statement contains Y later in the document.`

---

## 12. Warsh Dogfood Finding

The Warsh quote test demonstrates why this contract starts from quote provenance rather than event mapping.

Starting claim:

`Kevin Warsh opened his April 2026 Senate Banking confirmation hearing with "Inflation is a choice".`

Quote-first search finds:

- exact quote plus person surfaces prepared / written material and media previews
- exact quote search also finds prior public use before the hearing
- secondary sources reveal the event metadata: Senate Banking confirmation hearing, April 21, 2026
- official Senate Banking testimony URL confirms the written submission contains `Inflation is a choice, and the Fed must take responsibility for it`
- oral transcript comparison shows the oral opening begins with courtesy / biographical material, not the exact quote
- oral delivery later uses the variant `Inflation is the Fed's choice`
- media previews before the hearing cannot attest oral delivery
- prior public use means the hearing was a reuse of a known slogan rather than the origin of the phrase

The correct verdict is:

`semantic_true for Warsh's inflation-responsibility framework; false for oral_delivery_prefix; true with revision for written_submission; true with variant wording for oral_delivery_main; media previews are discovery surfaces, not oral-delivery proof; prior public use prevents treating the hearing as the origin of the phrase.`
