# Contributing a plugin

Thanks for sharing! The whole thing can be done in your browser, with no tools to install.

## The simplest path (browser only)

1. **Fork** this repo (the *Fork* button, top right).
2. In your fork, open `templates/hello-plugin`. For each file (`plugin.toml`, `main.rhai`, `README.md`), open it, copy its contents, then use **Add file → Create new file** and name it `plugins/<your-id>/<same file name>`.
   *Your id is lowercase letters, digits and dashes, such as `neon-tunnel`.*
3. **Edit** `plugins/<your-id>/plugin.toml`: set `id` to the folder name, then set `name`, `author`, `description` and only the `permissions` you need. Optionally set an `accent = "#rrggbb"` colour for your card in the app.
4. Edit `main.rhai` (see the [Plugin Guide](https://github.com/postmanpat-303/BigWaveRadio/blob/main/docs/PLUGIN_GUIDE.md)) and describe the plugin in `README.md`. A `preview.png` screenshot (≤ 300 KB) is welcome: **Add file → Upload files**.
5. **Open a pull request**. The *Validate plugins* check runs automatically. If it fails, click **Details** to see why, fix it, and commit again.

To test locally, zip the folder and use **Plugins → Import .zip** in BigWave Radio, or run `bwr-plugin-check plugins/<your-id>` (download it from the [BigWave Radio releases](https://github.com/postmanpat-303/BigWaveRadio/releases/latest)).

## Rules the checker enforces

- The folder name equals `id`, and the id is unique in this repo.
- `plugin.toml`, `main.rhai` and `README.md` are present; `name`, `version` and `description` are set.
- Only known permissions: `audio`, `now_playing`, `player_control`, `overlay`, `fullscreen`, `hotkeys`, `panel`, `page` and `storage`.
- The script compiles, and the hooks match the permissions.
- No binaries: only `.toml .rhai .md .txt .json .png .jpg .jpeg .gif`. Each text file is at most 256 KB, each image at most 300 KB, and the whole plugin at most 512 KB.
- Flashing plugins must not set `flashing = false`. The app caps flashes at the user's limit (3 per second by default) and shows a warning.

Updating your plugin? Bump `version` in the same PR.

## Build it with an AI assistant

Paste this into ChatGPT, Claude, Grok or similar, then replace the last line:

```text
You are writing a plugin for BigWave Radio, a Windows internet radio app.
Plugins are Rhai scripts (main.rhai) plus a manifest (plugin.toml), using plugin API v1.
Read the full API here first:
https://raw.githubusercontent.com/postmanpat-303/BigWaveRadio/main/docs/PLUGIN_GUIDE.md
And this working example:
https://raw.githubusercontent.com/postmanpat-303/BigWaveRadio-Plugins/main/templates/hello-plugin/main.rhai

Rules: request only the permissions you use; no network or file access exists;
keep per-frame work light; if it flashes, leave flashing enabled in the manifest.
Output three files: plugin.toml, main.rhai and README.md, with the folder name equal to the id.

My plugin idea: <describe it here>
```

## License

By opening a pull request you agree that your contribution is released under the [MIT license](LICENSE).
