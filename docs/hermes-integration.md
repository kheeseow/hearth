# Hermes integration

Hermes uses Hearth's authenticated Guide API through the standalone
`meg-hearth` plugin. Hearth remains the source of truth for Guide validation,
household boundaries, media processing, and events; Hermes does not need an
MCP server or a separate database.

## What it can do

The plugin provides `hearth_search_guides`, `hearth_get_guide`,
`hearth_create_guides`, `hearth_update_guide`, and `hearth_delete_guide`.
Creation accepts batches of 1 to 50 Guides. By default, it skips an exact
normalized title match; pass the plugin's `duplicatePolicy: "create"` only
when a second copy is intentional. Delete is a two-step flow: Hermes first
shows the matching Guide, then sends the deletion only with `confirm: true`.

Cover and step images are optional post-write attachments. A successfully
created Guide remains created if an image cannot be attached, and the result
reports the media error. Image URLs must be public `http` or `https` images;
the plugin rejects private, local, oversized, and non-image downloads.

## One-time Hearth setup

1. Create a dedicated Hearth user for Hermes and place it in the household
   whose Guides Hermes should manage. Do not reuse a personal administrator
   account.
2. In that user's profile, open **API Tokens** (`/user/profile/api-tokens`) and
   create a long-lived token. Copy it only into the Hermes secret environment;
   it is shown once.
3. When creating a token through the API, set `integrationId` to `hermes`.
   This is event attribution context for changes made through that token, not a
   permission scope. The profile UI may use Hearth's default value when it
   does not expose that field.

Tokens inherit the user's group, household, and permissions. Hearth has no
per-token scopes. The dedicated user is therefore the security boundary: it
must belong to the target household, and it can modify or delete only Guides
owned by that household. Reading remains group-scoped. Revoke this token from
the same API Tokens screen if it is exposed or no longer needed.

## Hermes configuration

The following is a future activation runbook for the existing NAS. It has not
been run as part of this repository change. Use a reviewed Hermes checkout and
replace labels such as `YYYYMMDDTHHMMSSZ` and
`/path/to/verified/hermes-checkout` with operator-approved values. Do not put a
token on a command line or in a shell history.

The checked-in `config/config.yaml.example` is only a seed for a new install.
The Hermes deployment copies it to `data/config.yaml` only when that live file
does not exist. Deploying a changed seed therefore **does not update an
existing NAS**; the live `/volume2/docker/hermes/data/config.yaml` must be
updated explicitly as described below.

### Existing-NAS activation, backup first

1. Verify the exact Hermes revision on a trusted workstation before copying
   anything. From `/path/to/verified/hermes-checkout`, run the complete
   `python3 tests/test_meg_hearth.py` suite, compile-check
   `plugins/meg-hearth/__init__.py`, parse `plugin.yaml` and
   `config/config.yaml.example` with a trusted YAML parser, and record SHA-256
   hashes for both files in `plugins/meg-hearth`. Stop if any check fails.

2. Before changing the NAS, create a private timestamped backup. On the NAS,
   replace the timestamp once, confirm the resulting path is beneath the exact
   Hermes root, and then run:

   ```sh
   cd /volume2/docker/hermes
   ACTIVATION_ID="YYYYMMDDTHHMMSSZ"
   BACKUP_DIR="/volume2/docker/hermes/data/.backups/hearth-${ACTIVATION_ID}"
   install -d -m 700 "$BACKUP_DIR"
   cp -p /volume2/docker/hermes/data/config.yaml "$BACKUP_DIR/config.yaml"
   cp -p /volume2/docker/hermes/.env "$BACKUP_DIR/hermes.env"
   if [ -e /volume2/docker/hermes/data/plugins/meg-hearth ]; then
     cp -a /volume2/docker/hermes/data/plugins/meg-hearth "$BACKUP_DIR/meg-hearth"
   fi
   chmod 600 "$BACKUP_DIR/config.yaml" "$BACKUP_DIR/hermes.env"
   stat -c '%u:%g %a %n' \
     /volume2/docker/hermes/data/config.yaml \
     /volume2/docker/hermes/.env \
     /volume2/docker/hermes/data/plugins > "$BACKUP_DIR/before.stat"
   if [ -e /volume2/docker/hermes/data/plugins/meg-hearth ]; then
     find /volume2/docker/hermes/data/plugins/meg-hearth -exec \
       stat -c '%u:%g %a %n' {} + >> "$BACKUP_DIR/before.stat"
   fi
   find /volume2/docker/hermes/data/profiles/residence -type f -print0 \
     | sort -z | xargs -0 sha256sum > "$BACKUP_DIR/residence.sha256"
   ```

   The root `.env` is the relevant environment file for the main gateway and
   contains secrets, so the backup must remain private. If this deployment uses
   another environment file in addition to `/volume2/docker/hermes/.env`, back
   up that file in the same private directory before proceeding. Do not copy or
   modify Residence profile secrets.

3. Stage, but do not yet promote, the already-verified plugin. Copy
   `plugins/meg-hearth/__init__.py` and `plugin.yaml` from the verified checkout
   into
   `/volume2/docker/hermes/data/.staging/hearth-YYYYMMDDTHHMMSSZ/meg-hearth/`.
   On the NAS, calculate SHA-256 hashes for the staged files and compare them
   byte-for-byte with the workstation hashes from step 1. Also record their
   owner and mode with `stat -c '%u:%g %a %n'`. A mismatch is a stop condition;
   do not repair it by weakening permissions.

4. Make a proposed configuration from the **live** file, not from the seed:

   ```sh
   cp -p /volume2/docker/hermes/data/config.yaml \
     /volume2/docker/hermes/data/.staging/hearth-YYYYMMDDTHHMMSSZ/config.yaml.proposed
   ```

   Edit only that proposed copy. Add `hearth` once to each of these main/root
   lists, and add `meg-hearth` once to enabled plugins:

   ```yaml
   toolsets:
     - hearth
   plugins:
     enabled:
       - meg-hearth
   platform_toolsets:
     cli:
       - hearth
   known_plugin_toolsets:
     cli:
       - hearth
   ```

   These are additions to the existing lists, not replacements. Parse the
   proposed YAML and inspect a diff against the live file. The diff must contain
   only these four main-profile additions. In particular, it must not change
   `data/profiles/residence`, any Residence service/profile setting, or the
   repository's `config/mac-worker` files. The Mac worker is a separate machine
   and receives no copy or restart during this activation.

5. Edit `/volume2/docker/hermes/.env` without printing it and set the two main
   gateway values:

```dotenv
HEARTH_URL=
HEARTH_TOKEN=
```

`HEARTH_URL` is the base address Hermes can reach, with no trailing slash or
`/api` suffix. `HEARTH_TOKEN` is the dedicated user's token. Never commit,
paste into chat, include in a hash manifest, or put a real token in
`config.yaml`. Keep the live `.env` owner and mode identical to the values
recorded in `before.stat`.

For an internal deployment, the gateway container must be able to resolve and
connect to the chosen Hearth address. A public URL is acceptable only if its
network and TLS policy permit the NAS gateway to reach it. Check that route
from the gateway before activating the plugin; a browser check from another
machine is not sufficient.

6. Before promotion, run a no-credential reachability check from the existing
   gateway container to the configured Hearth origin. A successful HTTP
   response from Hearth's public app-information endpoint proves DNS, routing,
   and TLS reachability; a timeout, name failure, non-200 status, or TLS error
   is a stop condition:

   ```sh
   cd /volume2/docker/hermes
   HEARTH_ORIGIN="https://hearth.example"
   sudo -n docker compose exec -T -e HEARTH_ORIGIN="$HEARTH_ORIGIN" gateway \
     python -c 'import os, urllib.request; response = urllib.request.urlopen(os.environ["HEARTH_ORIGIN"] + "/api/app/about", timeout=10); print(response.status); raise SystemExit(0 if response.status == 200 else 1)'
   ```

   Replace the example origin with the exact `HEARTH_URL`, but do not echo the
   token or enable shell tracing. Then promote the staged plugin directory and
   proposed `config.yaml` using a copy method that preserves the intended
   owners and modes.

7. Before recreating anything, verify all gates again:

   - promoted plugin hashes exactly match the verified workstation hashes;
   - live `data/config.yaml` parses and contains all four entries above;
   - live `config.yaml` and `.env` retain their pre-change owners and modes;
   - `data/plugins/meg-hearth` and its files match the owner/mode pattern of the
     other repository-managed `meg-*` plugins;
   - the Residence hash manifest still matches; and
   - no Mac worker file or process was touched.

   Any mismatch means restore from the backup and stop before restart.
   Recheck Residence without exposing its contents by running
   `sha256sum -c "$BACKUP_DIR/residence.sha256"` from the same NAS shell.

8. Recreate only the main `gateway` Compose service so Docker reloads the new
   `.env`; a plain restart does not reload `env_file` values:

   ```sh
   cd /volume2/docker/hermes
   sudo -n docker compose up -d --force-recreate --no-deps gateway
   ```

   Follow the Hermes deployment's current post-recreate dependency assertions,
   including the Mnemosyne reinstall that protects Residence recall. Do not
   recreate a Residence-specific service and do not connect to or restart the
   Mac worker. Confirm the `gateway` service is up and inspect recent main
   gateway logs for plugin import, authentication, or permission errors before
   starting the tool smoke test. At minimum, run `sudo -n docker compose ps
   gateway` and inspect `sudo -n docker compose logs --since 5m gateway`.

## Smoke test

After the gateway is running with reachable Hearth credentials:

1. Ask Hermes to search Guides, for example: “Search Hearth for smoke alarm.”
2. Ask it to fetch a returned Guide by slug.
3. Create a harmless test Guide, then patch it and attach a small public test
   image if media is in scope.
4. Ask Hermes to delete the test Guide and verify that it requests
   confirmation before the second call.
5. In Hearth, confirm the test Guide has the expected patched fields and any
   attached image, then delete it if it is no longer useful.

`integrationId` is neither a permission scope nor a standard notification or
actor field. Hearth adds it only as custom metadata for supported custom
Apprise notification URLs; ordinary notifications and the API-token screen do
not display it. It is not part of this normal smoke test.

Typical failures are direct: 401 means the token is wrong or revoked; 403
means the dedicated user lacks the necessary household access; and connection
errors mean the gateway cannot reach `HEARTH_URL`.

## Rollback

To stop access immediately, remove `HEARTH_URL` or `HEARTH_TOKEN` from the
gateway environment and recreate the gateway. For a stronger cutoff, revoke
the Hearth API token. To fully remove the integration, remove `hearth` from
the main profile toolsets and `meg-hearth` from enabled plugins, then recreate
the gateway. These steps do not delete Guides already created in Hearth.

For a failed first activation, restore `data/config.yaml`, the root `.env`, and
the prior `data/plugins/meg-hearth` state from the private timestamped backup.
If no plugin existed before activation, remove only the newly promoted
`data/plugins/meg-hearth` directory after verifying that exact path. Restore the
recorded owners and modes, recreate only the main gateway service, and repeat
the health checks. The backup contains credentials and must remain mode 700/600
or be securely removed under the operator's retention policy after rollback is
no longer needed.
