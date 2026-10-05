# Result-processing pipeline

Processing sits between SQL results and Torznab XML generation.

## Unfiltered path

`unfiltered` passes the requested `limit` and `offset` directly to SQL,
preserving the v1.0 query order.

## Processed path

For any other preset, the requested page is mapped to fixed, non-overlapping
1000-row database windows. Each required window is queried and processed
independently, then the requested local slice is returned.

This design bounds memory and supports arbitrary offsets, including pages that
cross a window boundary. It also means ranking and filtering are
**window-local**, not global across the complete result set.

## Ordering guarantees

- Italian ranking uses token-aware title scores.
- Custom ranking sums all matching score rules.
- Python's stable sort preserves original database order for equal scores.
- Exclusion runs before custom scoring.

Hard filters can make a page contain fewer items because pagination slices the
processed database window; hidden rows are not backfilled from later windows.
