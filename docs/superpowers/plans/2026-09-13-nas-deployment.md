# Hearth NAS Deployment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publish Hearth's production image and deploy a persistent, browser-accessible Hearth stack to Andrew's NAS without disturbing Olympus or Hermes.

**Architecture:** Hearth owns its AMD64 image build, NAS Compose file, deployment workflow, and credentials. The Hearth workflow connects to the NAS, updates a dedicated Hearth checkout through Git, and starts the matching immutable image on Hearth's own Docker network.

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

### Task 2: Add the isolated NAS stack inside Hearth

**Files:**
- Create: `deploy/nas/compose.yml`
- Create: `.github/workflows/deploy-nas.yml`

- [ ] Define the `hearth` service with port `9091:9000`, persistent Hearth-owned data, SQLite, and the production health check.
- [ ] Add a manual Hearth workflow that refuses a conflicting port, pulls the requested Hearth commit with Git, starts its matching image, and verifies health.
- [ ] Validate both YAML files and commit them only in Hearth.

### Task 3: Deploy and verify

- [ ] Push the Hearth deployment commit and run its manual workflow with that full commit SHA.
- [ ] Verify the container health, `/api/app/about`, expected port mapping, data mount, network membership, and absence of changes to Hermes/Residence/Olympus.
- [ ] Open `http://jollyroger.lowpew.com:9091` and complete the first administrator password change.
- [ ] Record the live image digest and backup location.

### Task 4: Configure clients separately after token creation

- [ ] Create a dedicated Hearth user and API token without exposing it in logs or chat.
- [ ] Configure any client only in that client's own repository or runtime.
- [ ] Keep Hearth deployment ownership entirely within Hearth.
