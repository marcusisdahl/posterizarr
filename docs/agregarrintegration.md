# Agregarr integration

Posterizarr can notify Agregarr after an Arr-triggered movie or show poster has
been successfully uploaded to Plex. Agregarr then checks that single Plex item,
adds it to matching collections, and applies its configured overlays.

Add these environment variables to the Posterizarr service:

```yaml
environment:
  - AGREGARR_TRIGGER_ENABLED=true
  - AGREGARR_URL=http://agregarr:7171
  - AGREGARR_API_KEY=replace-with-the-agregarr-api-key
```

`AGREGARR_URL` must be reachable from the Posterizarr container. The service-name
URL above works when both containers share a Docker network. Otherwise, use the
Agregarr server's reachable IP address and port.

The callback is sent only when all of these conditions are met:

- Posterizarr is running in Arr trigger mode.
- Plex integration is enabled.
- A root movie or show poster was successfully uploaded to Plex.

Background, season, episode, and title-card uploads do not trigger Agregarr. A
callback failure is logged as a warning and does not make the completed
Posterizarr run fail.

The target Agregarr build must provide `POST /api/v1/posterizarr/trigger`. The
callback authenticates with the normal Agregarr API key through the
`X-Api-Key` header.
