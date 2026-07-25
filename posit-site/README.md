# VizAdvisor Posit Connect Cloud site

Quarto documentation website for [VizAdvisor](https://github.com/Exios66/vizadvisor), designed in the same fashion as the Jack J. Burleson PSYCH 755 Posit site (UW Badger red navbar, floating sidebar, cosmo + custom SCSS, manuscript-style overview).

## Live URLs

| | |
|---|---|
| **Public share** | https://019f9a69-7c76-3f0a-e2b1-c586d1b61682.share.connect.posit.cloud/ |
| **Dashboard** | https://connect.posit.cloud/jackjburleson/content/019f9a69-7c76-3f0a-e2b1-c586d1b61682 |

This is a **new** content instance. Do **not** publish to `019f9a10-ebb9-d1d5-839f-97e794bfd0ca` (PSYCH 755).

## Render & publish

```bash
cd posit-site
quarto render
python3 scripts/publish_posit_new.py --content-id 019f9a69-7c76-3f0a-e2b1-c586d1b61682
```

Auth: set `POSIT_CONNECT_CLOUD_ACCESS_TOKEN` (+ refresh + account id), or use the script’s device-code flow.

## Layout

Kept under `posit-site/` so Quarto does not collide with the Vite React app’s root `index.html`.
