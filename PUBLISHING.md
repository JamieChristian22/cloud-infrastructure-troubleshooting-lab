# Publish this project to GitHub

**Target:** `https://github.com/JamieChristian22/cloud-infrastructure-troubleshooting-lab`

This source archive was prepared as an original Git repository with a local initial commit. Creating a *new GitHub repository* requires an account action that is not exposed by the connected integration in this ChatGPT session.

## Step 1 — Create the destination repository

1. Sign in as `JamieChristian22` and open https://github.com/new.
2. Repository name: `cloud-infrastructure-troubleshooting-lab`.
3. Description: `Hands-on cloud operations incident-response lab with fault injection, observability, Linux/network diagnostics, automated tests, and recovery evidence.`
4. Choose **Public** for recruiter visibility, if you want it publicly viewable.
5. **Do not initialize** with README, .gitignore, or license if you plan to push the supplied Git bundle; these files are already included.
6. Click **Create repository**.

## Step 2 — Push from the supplied Git bundle (best: retains initial Git commit)

The downloadable `.bundle` file is saved separately alongside the project ZIP. With Git installed on your computer, run:

```bash
git clone cloud-infrastructure-troubleshooting-lab.bundle cloud-infrastructure-troubleshooting-lab
cd cloud-infrastructure-troubleshooting-lab
git remote remove origin
git remote add origin https://github.com/JamieChristian22/cloud-infrastructure-troubleshooting-lab.git
git push -u origin main
```

GitHub will require authentication (typically credential manager or browser-based Git authentication). **Never paste a GitHub access token into ChatGPT.**

## Alternative — upload source using GitHub's website

If you do not use Git: unzip the project, create a **public** repository with the README option as needed, then open **Add file → Upload files** and drag the *contents* of the unzipped project folder to GitHub. Verify nested folders are preserved. Note that files inside `.github/` and other dot-prefixed files may be hidden by your computer's file browser, so **the Git bundle workflow is safer for a complete upload**.

## Step 3 — Verify publication

1. Check that `src/`, `tests/`, `.github/workflows/`, `docs/`, `infra/`, and `evidence/` exist online.
2. Open **Actions → Test and incident replay**; confirm the three Python-version jobs complete.
3. Confirm no `.lab/`, `.env`, tokens, or account credentials are in the repository.
4. Run the commands in the root `README.md` on your local machine.
5. Put the new project link in your GitHub profile recruiter navigation and selectively feature it when applying for cloud, platform, support, and DevOps jobs.