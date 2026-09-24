# Everyday app: architecture and privacy

The application must call `moveq-core`. A JavaScript reimplementation of Gini, Palma, or the concentration index is rejected. Two implementations drift, and the number a household sees would not be the number a researcher gets.

## Decision

**Server-side Python, calling `moveq-core`.** Not a browser reimplementation. Not WebAssembly: this repository does not ship a compiled core, and the public site does not claim one. A later WASM build could keep data on the device, but only if it executes the same Python core. Until that build exists, the architecture that satisfies the constraint is a Python process.

This is implementable. It is not a rejection of the app. It is a rejection of any interface that recomputes the metric in the browser.

## Privacy

Default: **retain nothing**.

Household inputs (names, hours, care, money) are used to compute a result and then discarded. No account, no stored rota, no log line that contains the inputs. A server log may record status codes and timings. It must not record the payload.

## Input

The user does not start from a blank metric form. They pick a situation. The first situation is a recurring-duty rota: a few named people and the hours they took, typed into a short form. A spreadsheet is not required.

## Language

The screen does not say Gini, Palma, or concentration index. It says what happened in ordinary words, for example that one person did about three times their share of the hours. It does not decide that the household is fair or unfair. "Disadvantage-concentrated" stays in the research API. It does not appear in this interface.

Palma is not offered at household scale. The small-sample warning already says that split is meaningless there.

## Scope

One template first: the recurring-duty rota. The other gallery situations wait until that one has been used.

## Relationship to the marketing site

Separate page, same repository. The marketing site explains the library. The rota page is a tool that calls the library. It is not a second product with its own inequality maths.
