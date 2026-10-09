# Restricted PR128 bit groups: exact negative control (NOT a new κ)

**Status: disproved candidate.** The restricted h=23 partition **does not
implement valid completed-core bit sharing** under the rational
`H = 9I - J` projector geometry of PR #129. The apparent 10.83% increase
in stopped-bit saving is **only a hypothetical arithmetic screen** of an
unrealizable child histogram; it is not a verified algorithm, bit supplier,
or multiplication exponent.

## Source and reproducibility

- Based on [PR #128](https://github.com/CrocSwap/integer-mult-bounds/pull/128),
  commit `530588a019b4a74f09180680c9e3961bf649ec89`.
- Compared against [PR #129](https://github.com/CrocSwap/integer-mult-bounds/pull/129),
  commit `992a442c10d243eee69bbd20f32ba6fa98fb430e`.
- `pr128-bit-profile.json` pins PR128's existing bit-word histogram,
  exterior histogram, source and blob SHA.
- `restricted-groups.json` retains the 87 signed PR128 complex groups,
  deletes triples containing coordinate 23 and reindexes the 1,771
  surviving triples.
- Run `python3 research/pr128-zero-frame-sharing-screen/verify_screen.py`
  on standard Python without `-O`. Standard library only.

This is a **negative experiment**, not a physical witness.

## What passes

The restricted partition has 83 groups of 21 and four groups of 7;
every h=23 triple appears exactly once. Each triple indicator has norm
one mod 2, and each distinct within-group pair has overlap zero mod 2.
This makes the binary Gram matrix the identity and produces 36,799
successful ordered Gram tests. The h=23 quadratic phase tests on 277
weight-0, weight-1 and weight-2 inputs per group are also exact:
24,099 checks pass. The orthogonal complements have nondegenerate binary
forms; their Gauss sums are -2 for the 83 rank-two complements and
-256i for the four rank-16 complements.

A hypothetical paid rank-mass screen would remove the 17,597 zero-start
roles' old exteriors and insert a rank-46/368 complement for each shared
role and each of the 87 groups. This yields formal W=49,249,558 and the
same rank deficit of 1,344,189. The approximate stopped bit moment
suggests a 10.8253% gain over PR128's bit supplier **if this grouping
were legally implementable**. It is not.

## Decisive failure: incompatible rational geometry

PR #129 uses the rational inner product `H=9I-J`, not the standard
binary dot product. For any two triple incidence vectors T,U, its
Gram entry is

    T^T H U = 9*(|T intersect U| - 1).

The group construction for PR128's **complex** operation requires binary
intersection parity zero. After restriction to 23 coordinates, distinct
triples in each group intersect in **zero or two** points. Those intersections
yield rational Gram entries -9 or +9, respectively, **never zero**.

The exhaustive witness has:
- 15,012 within-group unordered pairs meeting in zero points;
- 2,502 within-group unordered pairs meeting in two points;
- **0 / 17,514 pairs are rational-H-orthogonal.**

For example, `T={0,6,12}` and `U={0,6,18}` are in the first
group, with intersection size 2 and `T^T H U=9`.

Consequently their rational projectors do **not** annihilate one another.
The identity `D_A D_B = D_(A+B)` used by completed-core sharing
requires `AB=BA=0` and cannot be invoked for these blocks.
**The 87-group allocation, its W, and its improved bit moment cannot
be certified as a legal bit supplier.**

PR #129 already constructs a different valid rational-H-orthogonal
161-group sunflower partition, each group having eleven triples.
Future physical work must start from that valid geometry (or independently
prove another valid operator composition), not from this restricted
F2-only complex partition.

## Record and remaining work

PR #129 claims a conditional coupled exponent
`κ=0.000129186205798`. Beating it by 3% would require
`κ >= 0.00013306179197194`, with improvements to **both** limiting
suppliers and a new exact coupled certificate.

No new `κ` is claimed by this repository branch. The experiment is
preserved as a corruption/negative control to prevent rational-vs-binary
orthogonality mistakes.

The source construction is by an664 / PR128 contributors, with
original partition credits to Zhang and Ge. The PR129 rational bit
construction and its contributors are credited. This negative audit
was prepared with OpenAI assistance. Retained upstream licenses apply.
