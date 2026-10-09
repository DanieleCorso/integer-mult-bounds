# PR129 frontier: verified bottleneck and +3% target

This branch starts with the exact **PR129 source tree** (eumemic,
`992a442c10d243eee69bbd20f32ba6fa98fb430e`) as a reproducible
research baseline. The original authorship, source pins, license and notices
remain in place. **No improved exponent has been produced yet.**

## Baseline and the binding supplier

PR129's conditional result:

- Final exponent: `κ = 64593102899/500000000000000 = 0.000129186205798`
- Complex supplier: `130696544/10^12 = 0.000130696544`
- Coarse bit supplier: `129310447/10^12 = 0.000129310447`
- Stopped ordinary-bit parameter:
  `(999/1000) * 129310447/10^12 + (1/1000) * 384599/10^10
    = 129219596453/10^15 = 0.000129219596453`.

The supported bit parameter `a` is at most this stopped bit saving,
independent of any improvement on the complex side. Under the retained
assembly, `q=a(1-2η)` and the coupled exponent satisfies
`κ <= a` (strict in the actual positive-margin construction).

Therefore **with the PR129 bit supplier held fixed, even an arbitrarily
better complex supplier cannot yield a 3% gain**.

The next legitimate target is

`κ_target = (103/100) * κ_PR129 = 0.00013306179197194`.

This is already strictly above the current stopped bit saving
(`0.000129219596453`). A new *valid* bit construction is mandatory.
Improving only complex frames, deferred readouts, or birth-cut matching is
insufficient.

## What a meaningful improvement needs

1. A new rational-`H=9I-J` orthogonal projector partition, or
   another proven bit-side operator identity, which improves the paid
   full bit histogram; `F₂`-orthogonality alone is insufficient.
2. Full arbitrary-dirty scalar replay, frame geometry, reflected word
   and adapter charges, including a fixed generic rational basis.
3. Exact stopped wrapper and bit/complex moment checks, then the full
   47 strict assembly constraints and seven margins.
4. A complete manifest and CI. Until then, no updated `κ` in a PR title.

## Files and reproduction

`research/frontier-plus3/frontier_bounds.py` checks the rational
inequalities **using only integer arithmetic and Fraction**. It does not
pretend to validate any unconstructed bit supplier. Run:

```bash
python3 research/frontier-plus3/frontier_bounds.py
python3 research/cyclic-deferred/verify.py
```

PR129 is an inherited conditional finite witness with additional
assumptions explicitly stated in its original `SHARING.md` and
`BITSHARING.md`. This file records a rigorous *necessary condition*,
not a new multiplication theorem or record.

Credits: eumemic and the PR129 predecessor authors, an664 (PR128),
James Chang, Zhang–Ge, and the original notices. This frontier
analysis was prepared with OpenAI assistance.
