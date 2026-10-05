# Custom rules

Use **Custom** to score results or exclude them.

1. Open **Result processing** and choose **Custom**.
2. Select **Add rule**.
3. Choose the field, operator, value, and action.
4. Select **Save result processing**.

## Rule fields

- **Title** and **Provider**: contains, does not contain, equals.
- **Size** and **Seeders**: equals, at least, at most.

**Adjust score** reorders results; a higher value promotes them. **Exclude**
removes them. Rules run in order; disabled rules stay saved but are ignored.

::: danger Visibility

Exclusion is a hard filter. Hidden rows never reach Prowlarr.

:::
