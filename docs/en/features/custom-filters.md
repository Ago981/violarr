# Custom filters

The `custom` preset evaluates bounded structured rules. It does not support
regular expressions or arbitrary scripts.

## Rule fields

| Field      | Operators                            |
| ---------- | ------------------------------------ |
| `title`    | `contains`, `not_contains`, `equals` |
| `provider` | `contains`, `not_contains`, `equals` |
| `size`     | `equals`, `gte`, `lte`               |
| `seeders`  | `equals`, `gte`, `lte`               |

Every rule contains `enabled`, `field`, `operator`, `value`, and `action`.
`action` is either `score` or `exclude`; score rules also require `score`.

## Operator semantics

| Value type     | Matching behavior                                                                                                                                                      |
| -------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Text           | `contains`, `not_contains`, and `equals` compare Unicode case-folded strings. `contains` and `not_contains` are substring tests; `equals` compares the complete value. |
| Missing text   | A null or missing text field matches `not_contains` and does not match `contains` or `equals`.                                                                         |
| Number         | `equals`, `gte`, and `lte` compare finite numeric values directly. Booleans are not numbers.                                                                           |
| Missing number | A null, missing, boolean, NaN, or infinite result value never matches a numeric rule.                                                                                  |

Limits:

- at most 100 rules;
- text values must be non-empty and no longer than 512 characters;
- numeric rule values and scores must be finite numbers, not booleans;
- score magnitude cannot exceed 1000.

Disabled rules have no effect. Any matching enabled exclusion rule removes the
result. Remaining rows are ranked by the sum of matching score rules, with ties
kept stable.

::: danger Visibility

Exclusion is a hard filter. Hidden rows never reach Prowlarr.

:::
