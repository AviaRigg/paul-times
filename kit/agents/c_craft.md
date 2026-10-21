# Brief: Craft (rigging, 3D, games, jobs, deals) and the rigging tip

First read `kit/agents/_common.md`. You write: `parts/craft.html` and `parts/tip.html`

8. **craft** (`--a-craft`): 3D animation, rigging (top priority), 3D software (Maya, Blender,
   Houdini, ZBrush, Unreal), video games. Rigging is the heart of this section and gets the most
   space; write it for a strong professional rigger, never beginner material.
   **Tool of the week** (inverted box).
   **Rigging job board**: a real, substantial board, as many current rigging, character TD, CFX
   and creature/vehicle rigging openings as you can find worldwide (aim for 8 or more; Australia and
   Europe first), each with studio, role, location or remote, level, and a direct "Apply" link to
   the studio's own posting or ATS page (Greenhouse, Lever, Workday, the studio careers page;
   aggregators only if there is no direct page). Verify EVERY apply link before it goes in:
   `curl -sL -o /dev/null -m 20 -w '%{http_code}' "<url>"` must return 200, and a WebFetch of the
   page must confirm the role is still open. Drop any listing that fails; never publish an
   unverified link. Markup: `<a class="apply" href="URL">Apply ›</a>` on each listing. If the
   network blocks the check (`000`), confirm with WebFetch instead.
   **Riggers to follow**: notable recent posts and work from the rigging community (LinkedIn
   posts, ArtStation and Vimeo breakdowns, rigging reels, GitHub tools, talks, techniques under
   discussion), 3 to 5 items, each with who, what is technically interesting about it, and a link.
   Only real, findable posts; never invent one.
   (Say so plainly if there are no new openings or posts rather than padding.) **Australia corner**
   (visas, VFX and animation hiring in Australia). Photos: studios, software makers, games.
   **Your games** box: Paul plays GTA 6, Valorant, Fortnite, Cities: Skylines II, the F1 game
   (EA's current edition, any year) and Clash of Clans. Every day check each one for patch notes,
   balance changes, new agents/maps/seasons, events, release or delay news, and leaks only when a
   major outlet reports them (say so). One line per game that has news; skip games with nothing.
   Lead the Craft section with one of them when it is the biggest gaming story (a GTA 6 trailer or
   date news is front-page material). Screenshots or key art via Photos route 2.
   **Deals** box: real, current deals only, with price in €, the discount and the end date:
   his games first, then big sales (Steam, PlayStation Store, Xbox, Nintendo eShop), the Epic
   free game(s) of the week, and 3D tools and plugins (Maya, ZBrush, Substance, Houdini, Blender
   add-ons, rigging tools). Link each deal. Say "no notable deals today" rather than padding.

## Rigging tip

**Rigging tip of the day** (Maya 2026, ADVANCED: assume a strong rigger who knows the basics cold; no "lock and hide attributes" level tips. Think matrix-based rigging, offsetParentMatrix, node-based math, deformer stacks and weights tooling, performance and parallel evaluation, component and modular builds, Maya 2026 features, pipeline and API. Never repeat a tip from the last 60 issues (the do-not-repeat digest is in `issues/<id>/history.txt`); practical, with a short `maya.cmds` snippet that actually works). Write it to `parts/tip.html` as one `.box` block.
