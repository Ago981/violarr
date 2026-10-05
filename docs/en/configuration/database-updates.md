# Database updates

Open **Database updates** in the WebUI to keep the data used for searches up to
date.

1. Keep **Automatic snapshot updates** enabled for most installations.
2. Set the interval in hours: `24` is the default; accepted values range from 1
   minute to 7 days.
3. Select **Save update settings** and wait for confirmation.

The **Database snapshot** card on the **Dashboard** shows the installed and
latest detected versions and the last and next checks. **Updating** or active
**Maintenance** are temporary states; **Error** means you should read the
message and container logs.

For technical details, see [safe updates](../how-it-works/safe-updates).
