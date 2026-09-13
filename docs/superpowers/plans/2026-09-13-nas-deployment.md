# Hearth NAS Deployment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publish Hearth's production image and deploy a persistent, browser-accessible Hearth stack to Andrew's NAS without disturbing Olympus or Hermes.

**Architecture:** Build an AMD64 image from `hearth-main` in the public Hearth repository. Deploy it through a manual workflow in the private Hermes deployment repository, using that repository's existing NAS/Tailscale credentials and an isolated Compose project attached to `meg_net`.

**Tech Stack:** Docker Buildx, GitHub Container Registry, GitHub Actions, Docker Compose, Synology NAS, SQLite.

**Spec:** `docs/superpowers/specs/2026-09-13-nas-deployment-design.md`

## Global Constraints

- Use NAS host port `9091`; do not use Olympus port `3010`.
- Keep container port `9000` and persistent data at `/app/data`.
- Deploy only the `hearth` stack; do not modify or restart Hermes, Residence, the Mac worker, or Olympus.
- Use SQLite and `HEARTH_LEGACY_FEATURES=false` initially.
- Store no live credentials in Git or workflow logs.
- Never delete or replace `/volume2/docker/hearth/data` during deployment.

---

### Task 1: Publish the production image

**Files:**
- Create: `.github/workflows/build-nas-image.yml`

- [ ] Add a workflow that builds the production Dockerfile for `linux/amd64`.
- [ ] Publish `ghcr.io/kheeseow/hearth:nas-latest` and an immutable `nas-<commit>` tag.
- [ ] Validate the workflow and push `hearth-main`.
- [ ] Wait for the image build and verify the published image digest.

### Task 2: Add the isolated NAS stack

**Files:**
- Create: `/Users/andrewtay/Engineering/meg-hermes-deploy/integrations/hearth/docker-compose.nas.yml`
- Create: `/Users/andrewtay/Engineering/meg-hermes-deploy/.github/workflows/deploy-hearth.yml`

- [ ] Define the `hearth` service with port `9091:9000`, persistent `./data`, SQLite, the production health check, and external `meg_net`.
- [ ] Add a manual workflow that backs up/stages the Compose file, refuses a conflicting port, pulls an explicit image tag, starts only Hearth, and verifies health.
- [ ] Validate both YAML files and commit them without touching unrelated Hermes test edits.

### Task 3: Deploy and verify

- [ ] Push the private deployment commit and run the manual Hearth workflow with the immutable image tag.
- [ ] Verify the container health, `/api/app/about`, expected port mapping, data mount, network membership, and absence of changes to Hermes/Residence/Olympus.
- [ ] Open `http://jollyroger.lowpew.com:9091` and complete the first administrator password change.
- [ ] Record the live image digest and backup location.

### Task 4: Activate Hermes after token creation

- [ ] Create a dedicated Hearth user and API token without exposing it in logs or chat.
- [ ] Follow `docs/hermes-integration.md` to back up and update the live main Hermes profile.
- [ ] Recreate only the main Hermes gateway and run read, batch-create, update, image, and confirmation-gated delete smoke tests.
