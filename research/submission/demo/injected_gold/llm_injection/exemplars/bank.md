# Few-shot exemplar bank (generated)

Generated from `research/submission/demo/injected_gold/llm_injection/exemplars/rules.json` (sha256 `26c32fb758fd747a…`).
Do not edit by hand; regenerate with `scripts/build_exemplar_bank.py`.

## Counts

- triaged (primary): 40 (40 with before/after evidence)
- raw (separate pool): 713
- controls (negatives): 81
- triaged by source: {'readu': 36, 'curated': 4}

| canonical_class | artifact | predicate | triaged | raw | total |
|---|---|---|---:|---:|---:|
| `path-location-drift` | `path` | `PATH_EXISTS` | 12 | 58 | 70 |
| `external-dependency-drift` | `dependency` | `DEPENDENCY` | 11 | 336 | 347 |
| `removed-referent-drift` | `referent` | `SYMBOL_EXISTS` | 9 | 294 | 303 |
| `identifier-drift` | `identifier` | `SYMBOL_EXISTS` | 8 | 25 | 33 |

Gaps (no exemplar): none

## `path-location-drift` — path (PATH_EXISTS)

**Triaged (primary)**
- `triaged:alert-11b43e8e022f032c` — The FAQ still references the old 'Ollama Turbo' terminology and describes it as an App mode, while cloud.md has been renamed from 'Turbo' to 'Cloud' and describes cloud models as dedicated model tags.  
  https://github.com/ollama/ollama/commit/af060eb2508e8bed25241163243bdd7471cb7fd6
  before/after (real commit):
  - `docs/cloud.md` (doc, matched)
    - # Turbo
    - > ⚠️ Turbo is preview
    - Ollama’s [Turbo](https://ollama.com/turbo) is a new way to run open-source models with acceleration from datacenter-grade hardware.
    - Currently, the following models are available in Turbo:
    - - `gpt-oss:20b`
    - - `gpt-oss:120b`
    + # Cloud
    + | Ollama's cloud is currently in preview. For full documentation, see [Ollama's documentation](https://docs.ollama.com/cloud).
    + ## Cloud Models
    + [Cloud models](https://ollama.com/cloud) are a new kind of model in Ollama that can run without a powerful GPU. Instead, cloud models are automatically offloaded to Ollama's cloud while offering the same capabilities as local models, making it possible to keep using your local tools while running larger models that wouldn’t fit on a personal computer.
    + Ollama currently supports the following cloud models, with more coming soon:
    + - `gpt-oss:20b-cloud`
- `triaged:alert-20bd5530abe7bd74` — ARCHITECTURE_FLOW_EDITOR.md references ARCHITECTURE_INPUT_RENDERER.md and the old input-renderer/fields path, but the entire input-renderer/ directory was deleted and replaced by InputRenderer/ in this commit.  
  https://github.com/Significant-Gravitas/AutoGPT/commit/e5031261706f7d3aefe78d4918b3b061bd1a4824
  before/after (real commit):
  - `autogpt_platform/frontend/src/components/renderers/InputRenderer/docs/HEIRARCHY.md` (doc, matched)
    + # Input Renderer 2 - Hierarchy
    + 
    + ## Flow Overview
    + 
    + ```
    + FormRenderer2 → Form (RJSF) → ObjectFieldTemplate → FieldTemplate → Widget/Field
- `triaged:alert-3268c8f275480e9b` — Flow.tsx is listed at the root of FlowEditor in docs but was moved to Flow/Flow.tsx.  
  https://github.com/Significant-Gravitas/AutoGPT/commit/cf6e724e99ef288f743e63aa3b092576a6940911
  before/after (real commit):
  - `autogpt_platform/frontend/src/app/(platform)/build/components/FlowEditor/Flow/Flow.tsx` (code, matched)
    - import { useNodeStore } from "../../stores/nodeStore";
    - 
    - import NewControlPanel from "../NewBlockMenu/NewControlPanel/NewControlPanel";
    - import { CustomNode } from "./nodes/CustomNode";
    - import { useCustomEdge } from "./edges/useCustomEdge";
    - import CustomEdge from "./edges/CustomEdge";
    + import NewControlPanel from "../../NewBlockMenu/NewControlPanel/NewControlPanel";
    + import CustomEdge from "../edges/CustomEdge";
    + import { useFlow } from "./useFlow";
    + import { useNodeStore } from "../../../stores/nodeStore";
    + import { CustomNode } from "../nodes/CustomNode";
    + import { useCustomEdge } from "../edges/useCustomEdge";
- `triaged:alert-350586bc1ca4547a` — The Uninstall section in docs/windows.md links to a #changing-model-location anchor that no longer exists because the section was removed.  
  https://github.com/ollama/ollama/commit/66fb8575ced090a969c9529c88ee57a8df1259c2
  before/after (real commit):
  - `docs/windows.md` (doc, matched)
    - ### Changing Model Location
    - 
    - To change where Ollama stores the downloaded models instead of using your home directory, set the environment variable `OLLAMA_MODELS` in your user account.
    - 
    - 1. Start the Settings (Windows 11) or Control Panel (Windows 10) application and search for _environment variables_.
    - 
- `triaged:alert-3d74e717cf488ed1` — x/imagegen/README.md instructs using 'ollama create' without '--experimental' for imagegen model creation, but the commit removed auto-detection of tensor model directories, now requiring '--experimental' for the safetensors/imagegen creation path.  
  https://github.com/ollama/ollama/commit/30fdd229a434cfae409cc07456684315bf95a561
  before/after (real commit):
  - `cmd/cmd.go` (code, matched)
    - 	"github.com/ollama/ollama/x/create"
    - 			// No Modelfile found - check if current directory is an image gen model
    - 			if create.IsTensorModelDir(".") {
    - 				if !isLocalhost() {
    - 					return errors.New("remote safetensor model creation not yet supported")
    - 				}
    + 	// This gates both safetensors LLM and imagegen model creation
    + 
    + 	// Standard Modelfile + API path
- `triaged:alert-51d4fae83da0648b` — README.md documents MLX build instructions but the required x/ml/backend/mlx/ directory was removed by this commit.  
  https://github.com/ollama/ollama/commit/f1373193dc95c72207658aa705831102535000c7
  before/after (real commit):
  - `x/ml/backend/mlx/CMakeLists.txt` (doc, matched)
    - include(FetchContent)
    - 
    - # Read MLX version from top-level file (shared with Dockerfile)
    - file(READ "${CMAKE_SOURCE_DIR}/MLX_VERSION" MLX_C_GIT_TAG)
    - string(STRIP "${MLX_C_GIT_TAG}" MLX_C_GIT_TAG)
    - 
- `triaged:alert-527fdf20b19b2497` — Documentation/admin-guide/devices.txt lists /dev/pc110pad as an active device entry, but the pc110pad driver has been removed and its minor number is marked unused in the source header.  
  https://github.com/torvalds/linux/commit/6f468ea360f0a6a1e45854afbc3019842ed891a8
  before/after (real commit):
  - `drivers/input/mouse/Kconfig` (code, fallback)
    - config MOUSE_PC110PAD
    - 	tristate "IBM PC110 touchpad"
    - 	depends on ISA
    - 	help
    - 	  Say Y if you have the IBM PC-110 micro-notebook and want its
    - 	  touchpad supported.
  - `drivers/input/mouse/Makefile` (code, fallback)
    - obj-$(CONFIG_MOUSE_PC110PAD)		+= pc110pad.o
  - `drivers/input/mouse/pc110pad.c` (code, fallback)
    - // SPDX-License-Identifier: GPL-2.0-or-later
    - /*
    -  *  Copyright (c) 2000-2001 Vojtech Pavlik
    -  *
    -  *  Based on the work of:
    -  *	Alan Cox	Robin O'Leary
- `triaged:alert-60fec720fe85f3eb` — README Troubleshooting section references run-tests.js which was deleted in this commit.  
  https://github.com/Significant-Gravitas/AutoGPT/commit/91dd9364bbda351fdd7627df05cd7fbf9aa16120
  before/after (real commit):
  - `autogpt_platform/backend/load-tests/README.md` (doc, matched)
    - # 4. Verify setup and run quick test
    - node run-tests.js verify
    - # 5. Run tests locally (development/debugging)
    - node run-tests.js run all DEV
    - 
    - # 6. Run tests in k6 cloud (performance testing)
    + # 4. Run orchestrated load tests locally
    + node orchestrator/orchestrator.js DEV local
    + # 5. Run orchestrated load tests in k6 cloud (recommended)
    + node orchestrator/orchestrator.js DEV cloud
    + ## 📋 Load Test Orchestrator
    + The AutoGPT Platform uses a comprehensive load test orchestrator (`orchestrator/orchestrator.js`) that runs 12 optimized tests with maximum VU counts:
  - `autogpt_platform/backend/load-tests/orchestrator/orchestrator.js` (code, matched)
    + #!/usr/bin/env node
    + 
    + /**
    +  * AutoGPT Platform Load Test Orchestrator
    +  * 
    +  * Optimized test suite with only the highest VU count for each unique test type.
- `triaged:alert-66f6f6b671d4597f` — README.md links to ./docs/api.md but the file was renamed to docs/api-reference.md  
  https://github.com/ollama/ollama/commit/2d5e066c8cb2f54f398243dcb922e615ac94a509
  before/after (real commit):
  - `docs/api-reference.md` (doc, matched)
- `triaged:alert-76cbc1311ef22f89` — README example uses Flag.AGENT_ACTIVITY which was removed from the Flag enum in use-get-flag.ts  
  https://github.com/Significant-Gravitas/AutoGPT/commit/59d242f69c6538f4df03f4f001d741e12607db0d
  before/after (real commit):
  - `autogpt_platform/frontend/src/services/feature-flags/use-get-flag.ts` (code, matched)
    -   AGENT_ACTIVITY = "agent-activity",
    -   [Flag.AGENT_ACTIVITY]: boolean;
    -   [Flag.AGENT_ACTIVITY]: true,
- `triaged:alert-aa7a043237abb063` — Documentation references a test file that was deleted in this commit.  
  https://github.com/Significant-Gravitas/AutoGPT/commit/0a1591fce23fca4936686e4172fd46e8c6d0470c
  before/after (real commit):
  - `autogpt_platform/frontend/src/app/(platform)/build/components/NewControlPanel/NewControlPanel.tsx` (code, fallback)
    - // import { Separator } from "@/components/__legacy__/ui/separator";
    - // import { NewSaveControl } from "../SaveControl/NewSaveControl";
    - import { GraphExecutionID } from "@/lib/autogpt-server-api";
    - // import { ControlPanelButton } from "../ControlPanelButton";
    - // import { GraphSearchMenu } from "../GraphMenu/GraphMenu";
    - import { Flag, useGetFlag } from "@/services/feature-flags/use-get-flag";
    + export const NewControlPanel = memo(() => {
    +   useNewControlPanel({});
    +   return (
    +     <section
    +       className={cn(
    +         "absolute left-4 top-10 z-10 overflow-hidden rounded-[1rem] border-none bg-white p-0 shadow-[0_1px_5px_0_rgba(0,0,0,0.1)]",
  - `autogpt_platform/frontend/src/app/(platform)/build/components/NewControlPanel/NewSearchGraph/GraphMenu/GraphMenu.tsx` (code, fallback)
    - import { CustomNode } from "@/app/(platform)/build/components/legacy-builder/CustomNode/CustomNode";
    + import { CustomNode } from "../../../FlowEditor/nodes/CustomNode/CustomNode";
  - `autogpt_platform/frontend/src/app/(platform)/build/components/NewControlPanel/NewSearchGraph/GraphMenu/useGraphMenu.ts` (code, fallback)
    - import { CustomNode } from "@/app/(platform)/build/components/legacy-builder/CustomNode/CustomNode";
    + import { CustomNode } from "../../../FlowEditor/nodes/CustomNode/CustomNode";
  - `autogpt_platform/frontend/src/app/(platform)/build/components/NewControlPanel/NewSearchGraph/GraphMenuContent/GraphContent.tsx` (code, fallback)
    - import { beautifyString, getPrimaryCategoryColor } from "@/lib/utils";
    -                 node.data?.metadata?.customized_name ||
    -                 beautifyString(node.data?.blockType || "").replace(
    -                   / Block$/,
    -                   "",
    -                 );
    + import { beautifyString, categoryColorMap } from "@/lib/utils";
    +                 (node.data?.metadata?.customized_name as string) ||
    +                 beautifyString(node.data?.title || "").replace(/ Block$/, "");
    +               const nodeType = beautifyString(node.data?.title || "").replace(
    +                 / Block$/,
    +                 "",
  - `autogpt_platform/frontend/src/app/(platform)/build/components/NewControlPanel/NewSearchGraph/GraphMenuSearchBar/useGraphMenuSearchBar.tsx` (code, fallback)
    - import { CustomNode } from "@/app/(platform)/build/components/legacy-builder/CustomNode/CustomNode";
    -   const blockType = (node.data?.blockType || "").toLowerCase();
    -   const customizedName = (
    -     node.data?.metadata?.customized_name || ""
    + import { CustomNode } from "../../../FlowEditor/nodes/CustomNode/CustomNode";
    +   const blockType = (node.data?.title || "").toLowerCase();
    +   const customizedName = String(
    +     node.data?.metadata?.customized_name || "",
- `triaged:alert-b117db28c12cddac` — docs/content/index.md links to platform/new_blocks.md which no longer exists at that path after files were moved to docs/platform/.  
  https://github.com/Significant-Gravitas/AutoGPT/commit/a318832414b7015f4597d3ee4e394cd69f9ec7e9
  before/after (real commit):
  - `docs/platform/new_blocks.md` (doc, matched)

**Raw (separate pool)**
- `raw:Significant-Gravitas/AutoGPT:0a1591fce23fca4936686e4172fd46e8c6d0470c:2` — README shows code snippets or import paths that now point to deleted or moved modules (e.g., from legacy-builder to FlowEditor).
- `raw:Significant-Gravitas/AutoGPT:27d94e395cc8d191a1b284dda2b42572ed9d4796:2` — README references the old location of BLOCKED_TOOLS or other constants moved to tool_adapter.py.
- `raw:Significant-Gravitas/AutoGPT:29895c290f306c1b6525e4e18321242a5deb8276:0` — README references the removed generic_webhook module path, causing import errors or missing documentation.
- `raw:Significant-Gravitas/AutoGPT:3b1b2fe30cc4428f3ebf595c301a3193ef5edaa7:0` — README references the old system prompt file path (prompts/chat_system.md) which no longer exists; prompts are now fetched from Langfuse.
- `raw:Significant-Gravitas/AutoGPT:3d0ede9f34ea6deec0158846535025ecaf14b642:0` — README describes that Claude can view inline images from workspace file tool results; this is no longer true as the image embedding from tool results was removed.
- `raw:Significant-Gravitas/AutoGPT:4c0dd27157f86e9fd2acfb70f39185832ca5f8a7:0` — If README documents deployment steps or references the workflow file 'platform-autgpt-deploy-prod.yml', the renamed file would cause a broken link or missing file reference.
- `raw:Significant-Gravitas/AutoGPT:4db13837b972e3fc9516abb632a14f551bafdf4e:1` — The README might mention import paths for components like CredentialsInput, RunAgentInputs, or OutputRenderers that have been moved to new locations.
- `raw:Significant-Gravitas/AutoGPT:4db13837b972e3fc9516abb632a14f551bafdf4e:3` — The README might refer to the old chat session management hooks (useChatSession, useChatStream) that have been moved to a different directory.
- `raw:Significant-Gravitas/AutoGPT:4db3be2d6113f5318305898445b62a23e520abaf:2` — README references asset files (e.g., archer-attack.png) that are deleted.
- `raw:Significant-Gravitas/AutoGPT:634f826d82e8b93af293cee4966efa00adaa00e7:0` — README or user guide references the old workflow file path `.github/workflows/platform-autgpt-deploy-prod.yml` for deployment instructions, but the file is now renamed to `.github/workflows/platform-autogpt-deploy-prod.yml`, causing broken links or incorrect instructions.
- `raw:Significant-Gravitas/AutoGPT:7d4c020a9bd6b25dc4e25c2934e4ae6656af6257:5` — README mentions file paths under 'src/components/contextual/Chat/' that have been moved or deleted.
- `raw:Significant-Gravitas/AutoGPT:8cfabcf4fdafa91f3bc9da45d32c0aa49448e074:1` — README describes the inline tool notes or environment-specific supplements that were moved to prompting.py, now outdated.
- `raw:Significant-Gravitas/AutoGPT:943a1df815f3cdce05a0684444d1f01cc8a5a84d:0` — README instructions for locating Playwright report or test results point to old paths (playwright-report, test-results) instead of new paths (autogpt_platform/frontend/playwright-report, autogpt_platform/frontend/test-results).
- `raw:Significant-Gravitas/AutoGPT:9c3f679f30e4ffdd30ef2c50abc8c6f40b86e370:1` — README describes a return URL parameter for login; that functionality is removed.
- `raw:Significant-Gravitas/AutoGPT:a056d9e71a1459cac3711e03bb0cfa4423c86bb5:3` — README references a debug log file chunks.log, which was removed.
- … 43 more in `bank.json`

## `external-dependency-drift` — dependency (DEPENDENCY)

**Triaged (primary)**
- `triaged:alert-1ccd5743d77a06ff` — Italian translation of changes.rst states minimum Rust version 1.78.0, but actual minimum required version is 1.85.0.  
  https://github.com/torvalds/linux/commit/b28711ac98e8b43bfbf5c918022018a54dcedd45
  before/after (real commit):
  - `arch/Kconfig` (code, fallback)
    - 	depends on RUSTC_VERSION >= 107900
    - 	depends on (RUSTC_LLVM_VERSION >= 190103 && RUSTC_VERSION >= 108200) || \
    + 	depends on RUSTC_LLVM_VERSION >= 190103 || \
  - `arch/arm64/Kconfig` (code, fallback)
    - 	# Shadow call stack is only supported on certain rustc versions.
    - 	#
    - 	# When using the UNWIND_PATCH_PAC_INTO_SCS option, rustc version 1.80+ is
    - 	# required due to use of the -Zfixed-x18 flag.
    - 	#
    - 	# Otherwise, rustc version 1.82+ is required due to use of the
  - `arch/riscv/Kconfig` (code, fallback)
    - 	# Shadow call stack requires rustc version 1.82+ due to use of the
    - 	# -Zsanitizer=shadow-call-stack flag.
    - 	depends on !SHADOW_CALL_STACK || RUSTC_VERSION >= 108200
  - `init/Kconfig` (code, fallback)
    - 	depends on !CALL_PADDING || RUSTC_VERSION >= 108100
    - 	depends on !(MITIGATION_RETHUNK && KASAN) || RUSTC_VERSION >= 108300
- `triaged:alert-2daea4b18ad37cf7` — README documents package.json and npm scripts (npm run verify, npm test, npm run cloud) but no package.json exists in the load-tests directory, causing npm to fail.  
  https://github.com/Significant-Gravitas/AutoGPT/commit/4c000086e6d5d9eab187986e3eeec40476d341c4
  before/after (real commit):
  - `autogpt_platform/backend/load-tests/README.md` (doc, matched)
    - # AutoGPT Platform Load Testing Infrastructure
    - Production-ready k6 load testing suite for the AutoGPT Platform API with Grafana Cloud integration.
    - ## 🎯 **Current Working Configuration (Sept 2025)**
    - 
    - **✅ RATE LIMIT OPTIMIZED:** All tests now use 5 VUs with `REQUESTS_PER_VU` parameter to avoid Supabase rate limits while maximizing load.
    - **Quick Start Commands:**
    + # AutoGPT Platform Load Tests
    + Clean, streamlined load testing infrastructure for the AutoGPT Platform using k6.
    + ## 🚀 Quick Start
    + # 1. Set up Supabase service key (required for token generation)
    + export SUPABASE_SERVICE_KEY="your-supabase-service-key"
    + # 2. Generate pre-authenticated tokens (first time setup - creates 150+ tokens with 24-hour expiry)
- `triaged:alert-39d71642fff1897d` — Install command references deprecated npm package @mariozechner/pi-coding-agent instead of current @earendil-works/pi-coding-agent.  
  https://github.com/ollama/ollama/commit/8a257ec00a76d3dd90f0106fba1e56215588efae
  before/after (real commit):
  - `docs/integrations/pi.mdx` (doc, matched)
    + ---
    + title: Pi
    + ---
    + 
    + Pi is a minimal AI agent toolkit with plugin support.
    + 
- `triaged:alert-3f0b25c9b7c723d7` — README documentation claims Node.js 16.10+/16.x is sufficient, but the package.json now requires Node.js 22.x (enforced by engine-strict=true in .npmrc).  
  https://github.com/Significant-Gravitas/AutoGPT/commit/4744675ef95a0ad1d1124dbd6197b4c793434468
  before/after (real commit):
  - `.github/workflows/platform-frontend-ci.yml` (code, fallback)
    -           node-version: "21"
    -           node-version: "21"
    -           node-version: "21"
    -           node-version: "21"
    +           node-version: "22.18.0"
    +           node-version: "22.18.0"
    +           node-version: "22.18.0"
    +           node-version: "22.18.0"
  - `.github/workflows/platform-fullstack-ci.yml` (code, fallback)
    -           node-version: "21"
    -           node-version: "21"
    +           node-version: "22.18.0"
    +           node-version: "22.18.0"
  - `autogpt_platform/frontend/.npmrc` (code, fallback)
    - save-exact=true 
    + save-exact=true
    + engine-strict=true
  - `autogpt_platform/frontend/package.json` (code, fallback)
    -     "@hookform/resolvers": "5.2.1",
    -     "@sentry/nextjs": "10.15.0",
    -     "@supabase/ssr": "0.6.1",
    -     "@supabase/supabase-js": "2.55.0",
    -     "@tanstack/react-query": "5.87.1",
    -     "@xyflow/react": "12.8.3",
    +   "engines": {
    +     "node": "22.x"
    +   },
    +     "@hookform/resolvers": "5.2.2",
    +     "@sentry/nextjs": "10.22.0",
    +     "@supabase/ssr": "0.7.0",
  - `autogpt_platform/frontend/pnpm-lock.yaml` (code, fallback)
    -         specifier: 5.2.1
    -         version: 5.2.1(react-hook-form@7.62.0(react@18.3.1))
    -         version: 15.4.6(next@15.4.7(@babel/core@7.28.4)(@opentelemetry/api@1.9.0)(@playwright/test@1.55.0)(react-dom@18.3.1(react@18.3.1))(react@18.3.1))(react@18.3.1)
    -         specifier: 10.15.0
    -         version: 10.15.0(@opentelemetry/context-async-hooks@2.1.0(@opentelemetry/api@1.9.0))(@opentelemetry/core@2.1.0(@opentelemetry/api@1.9.0))(@opentelemetry/sdk-trace-base@2.1.0(@opentelemetry/api@1.9.0))(next@15.4.7(@babel/core@7.28.4)(@opentelemetry/api@1.9.0)(@playwright/test@1.55.0)(react-dom@18.3.1(react@18.3.1))(react@18.3.1))(react@18.3.1)(webpack@5.101.3(esbuild@0.25.9))
    -         specifier: 0.6.1
    +         specifier: 5.2.2
    +         version: 5.2.2(react-hook-form@7.66.0(react@18.3.1))
    +         version: 15.4.6(next@15.4.7(@babel/core@7.28.4)(@opentelemetry/api@1.9.0)(@playwright/test@1.56.1)(react-dom@18.3.1(react@18.3.1))(react@18.3.1))(react@18.3.1)
    +         specifier: 10.22.0
    +         version: 10.22.0(@opentelemetry/context-async-hooks@2.1.0(@opentelemetry/api@1.9.0))(@opentelemetry/core@2.1.0(@opentelemetry/api@1.9.0))(@opentelemetry/sdk-trace-base@2.1.0(@opentelemetry/api@1.9.0))(next@15.4.7(@babel/core@7.28.4)(@opentelemetry/api@1.9.0)(@playwright/test@1.56.1)(react-dom@18.3.1(react@18.3.1))(react@18.3.1))(react@18.3.1)(webpack@5.101.3(esbuild@0.25.9))
    +         specifier: 0.7.0
- `triaged:alert-5a292f75418b8682` — The package name 'vulkan-sdk' does not exist in Ubuntu/Debian or Fedora/CentOS repositories; the correct development package is 'libvulkan-dev' (Ubuntu/Debian) and 'vulkan-loader-devel' (Fedora/CentOS).  
  https://github.com/ollama/ollama/commit/20aee967067ae4a57a29405e89300f879d209972
  before/after (real commit):
  - `docs/development.md` (doc, matched)
    - 
    + - (Optional) VULKAN GPU support
    +     - [VULKAN SDK](https://vulkan.lunarg.com/sdk/home) - useful for AMD/Intel GPUs
    + > Building for Vulkan requires VULKAN_SDK environment variable:
    + > 
    + > PowerShell
    + > ```powershell
- `triaged:alert-618f0307eb26882e` — Integrations card in docs/README.md describes 'Learn more about hosting the developer platform' but the redirect mappings show Integrations is about block-level third-party service integrations, not hosting.  
  https://github.com/Significant-Gravitas/AutoGPT/commit/7ee28197a3ab3268a55582651ba30bde31c3c4f0
  before/after (real commit):
  - `autogpt_platform/cloudflare_worker.js` (code, matched)
    + /**
    +  * Cloudflare Workers Script for docs.agpt.co → agpt.co/docs migration
    +  * 
    +  * Deploy this script to handle all redirects with a single JavaScript file.
    +  * No rule limits, easy to maintain, handles all edge cases.
    +  */
  - `docs/README.md` (doc, matched)
    + ---
    + description: Welcome to your team’s developer platform
    + cover: .gitbook/assets/Banner_image.png
    + coverY: 56.53835084561286
    + layout:
    +   width: wide
- `triaged:alert-d31b5ec93fbc2072` — Italian translation still lists Rust minimum version as 1.78.0 while the English documentation and the build script have been updated to 1.85.0.  
  https://github.com/torvalds/linux/commit/f32fb9c58a5bd436f082dfa12639177b9da87680
  before/after (real commit):
  - `Documentation/process/changes.rst` (doc, matched)
    - Rust (optional)        1.78.0           rustc --version
    + Rust (optional)        1.85.0           rustc --version
- `triaged:alert-e0fb492470f8068d` — Documentation states Node.js 20+ but NemoClaw requires Node.js >=22.16.0.  
  https://github.com/ollama/ollama/commit/22c2bdbd8add79c6fca2eb2538ab36fcd4a9ca48
  before/after (real commit):
  - `docs/integrations/nemoclaw.mdx` (doc, matched)
    + ---
    + title: NemoClaw
    + ---
    + 
    + NemoClaw is NVIDIA's open source security stack for [OpenClaw](/integrations/openclaw). It wraps OpenClaw with the NVIDIA OpenShell runtime to provide kernel-level sandboxing, network policy controls, and audit trails for AI agents. 
    + 
- `triaged:alert-f2c043ee40dcc2b0` — JavaScript SDK examples show passing a plain string to client.webSearch() and client.webFetch(), but the published ollama npm package (v0.6.3) requires an object argument.  
  https://github.com/ollama/ollama/commit/7d411a468671ae59c1e5a32701f6ad1d735b12c0
  before/after (real commit):
  - `docs/capabilities/web-search.mdx` (doc, matched)
    - const results = await client.webSearch({ query: "what is ollama?" });
    - const fetchResult = await client.webFetch({ url: "https://ollama.com" });
    + const results = await client.webSearch("what is ollama?");
    + const fetchResult = await client.webFetch("https://ollama.com");
- `triaged:alert-f6a52da81652ebc9` — README files claim Node.js 16.x/16.10+ is sufficient, but this commit introduces a dependency on agent-browser (npm install -g agent-browser) which requires Node.js >=24.0.0, and the project's own frontend package.json requires node 22.x.  
  https://github.com/Significant-Gravitas/AutoGPT/commit/b504cf9854b84c1612b84d271dbc7b9c9bd64d8a
  before/after (real commit):
  - `autogpt_platform/backend/backend/copilot/tools/agent_browser.py` (code, matched)
    + """Agent-browser tools — multi-step browser automation for the Copilot.
    + 
    + Uses the agent-browser CLI (https://github.com/vercel-labs/agent-browser)
    + which runs a local Chromium instance managed by a persistent daemon.
    + 
    + - Runs locally — no cloud account required
- `triaged:alert-fed7183254dcae14` — Documentation references bindgen 0.65.x which is below the newly required minimum version 0.71.1  
  https://github.com/torvalds/linux/commit/c3a00a3f31fffc7adcd81b66de3fb2c2f0b11558
  before/after (real commit):
  - `Documentation/process/changes.rst` (doc, fallback)
    - bindgen (optional)     0.65.1           bindgen --version
    + bindgen (optional)     0.71.1           bindgen --version
  - `scripts/min-tool-version.sh` (code, fallback)
    - 	echo 0.65.1
    + 	echo 0.71.1

**Raw (separate pool)**
- `raw:Significant-Gravitas/AutoGPT:02645732b8cf88875de028a81b640a3e7a283295:2` — README specifies an e2b version constraint that is no longer accurate after the upgrade to 2.15.2.
- `raw:Significant-Gravitas/AutoGPT:0728f3bd49fd9466c283bd406bb2764f29390f46:2` — Documentation on authentication requirements for Google services in AutoGPT blocks becomes inaccurate.
- `raw:Significant-Gravitas/AutoGPT:0c435c4afab4afb2b294b1aa1c78acf732616918:0` — README states 'Requires Node.js 21' but CI now uses Node.js 22, causing confusion for users following README instructions.
- `raw:Significant-Gravitas/AutoGPT:1750c833ee0cd85ca1db3e45f28163a63a57cf6d:1` — The README might list system requirements or version prerequisites that become outdated due to this version bump.
- `raw:Significant-Gravitas/AutoGPT:18002cb8f0a1120d1c3e45b634c9945a6a93ffdb:0` — README states 'requires Node.js >=10.14' but cross-env now needs >=20, causing installation errors.
- `raw:Significant-Gravitas/AutoGPT:1851264a6acd938d35380bf7b80eecb285c6611b:0` — README installation instructions that pin @sentry/nextjs version may reference the old version, leading users to install an outdated package.
- `raw:Significant-Gravitas/AutoGPT:1d9dd782a8ca7e66d1034a455f3c2cbc60dd3038:2` — README's authentication section describes only single-permission checks, mismatching the new multi-permission requirement.
- `raw:Significant-Gravitas/AutoGPT:1fdc02467b299513092792db7c483967aa19438f:1` — README installation guide does not mention the new prometheus-fastapi-instrumentator dependency
- `raw:Significant-Gravitas/AutoGPT:350ad3591b1e7a9f5ebf5a2d3053339c0f8b57e2:0` — README describes credential matching criteria but omits scope requirements, causing users to expect credentials without required scopes to work.
- `raw:Significant-Gravitas/AutoGPT:3b822cdaf7141cd0900644b927b104d4ec185c0b:0` — README instructs users to run `pip install -r docs/requirements.txt` but it's no longer part of the automated setup.
- `raw:Significant-Gravitas/AutoGPT:4744675ef95a0ad1d1124dbd6197b4c793434468:1` — README lists pnpm 10.11.1 as the package manager, but commit changes to 10.20.0.
- `raw:Significant-Gravitas/AutoGPT:4744675ef95a0ad1d1124dbd6197b4c793434468:2` — README includes installation instructions that rely on specific dependency versions that are now updated.
- `raw:Significant-Gravitas/AutoGPT:4744675ef95a0ad1d1124dbd6197b4c793434468:3` — README mentions build/run commands that may behave differently with the updated dependency versions.
- `raw:Significant-Gravitas/AutoGPT:4c474417bc942b41f80531bd6e6aef57f254f7ce:1` — If the README describes a specific instrumentation or middleware setup that uses this package, the documented steps could be broken.
- `raw:Significant-Gravitas/AutoGPT:52b3aebf7187386514f4b4de3eb52e06bd8dfd76:2` — README lists system dependencies (e.g., for Docker) but omits bubblewrap, jq, ripgrep, tree.
- … 321 more in `bank.json`

## `removed-referent-drift` — referent (SYMBOL_EXISTS)

**Triaged (primary)**
- `triaged:alert-2bfdc6ac8403e47a` — English KASAN documentation removed the paragraph about SLUB and SLAB allocator support, but Chinese (zh_TW) translation still contains the outdated statement that software KASAN modes support both SLUB and SLAB allocators.  
  https://github.com/torvalds/linux/commit/9de209c183de3a52220b37262e2a0e0d52719de5
  before/after (real commit):
  - `Documentation/dev-tools/kasan.rst` (doc, matched)
    - For slab, both software KASAN modes support SLUB and SLAB allocators, while
    - Hardware Tag-Based KASAN only supports SLUB.
    - 
- `triaged:alert-58d9824e5aed2a9b` — Documentation recommends llama3-70b-8192 as a Groq model but the code has removed it from the GroqModelName enum.  
  https://github.com/Significant-Gravitas/AutoGPT/commit/dcecb17bd1b527904fe7399463541eddb280cadd
  before/after (real commit):
  - `classic/forge/forge/llm/providers/groq.py` (code, matched)
    -     LLAMA3_8B = "llama3-8b-8192"
    -     LLAMA3_70B = "llama3-70b-8192"
    -         ChatModelInfo(
    -             name=GroqModelName.LLAMA3_8B,
    -             provider_name=ModelProviderName.GROQ,
    -             prompt_token_cost=0.05 / 1e6,
- `triaged:alert-790cabcef1be9244` — Documentation references 'swap_map' which no longer exists in the code after this commit removed the field from swap_info_struct.  
  https://github.com/torvalds/linux/commit/0d6af9bcf383bcdf601e670bb605861b01e318e7
  before/after (real commit):
  - `include/linux/swap.h` (code, fallback)
    - 	SWP_CONTINUED	= (1 << 5),	/* swap_map has count continuation */
    - /* Bit flag in swap_map */
    - #define COUNT_CONTINUED	0x80	/* Flag swap_map continuation for full count */
    - 
    - /* Special value in first swap_map */
    - #define SWAP_MAP_MAX	0x3e	/* Max count */
    + 	unsigned int	max;		/* size of this swap device */
    + 					 * inuse_pages and all cluster lists.
    + 					 * Other fields are only changed
  - `mm/memory.c` (code, fallback)
    - 		if (add_swap_count_continuation(entry, GFP_KERNEL) < 0) {
    + 		if (swap_retry_table_alloc(entry, GFP_KERNEL) < 0) {
  - `mm/swap.h` (code, fallback)
    - extern void swap_entries_free(struct swap_info_struct *si,
    - 			      struct swap_cluster_info *ci,
    - 			      unsigned long offset, unsigned int nr_pages);
    + 	unsigned int *extend_table;	/* For large swap count, protected by ci->lock */
    + extern int swap_retry_table_alloc(swp_entry_t entry, gfp_t gfp);
    + 
    + extern void __swap_cluster_free_entries(struct swap_info_struct *si,
    + 					struct swap_cluster_info *ci,
    + 					unsigned int ci_off, unsigned int nr_pages);
  - `mm/swap_state.c` (code, fallback)
    - 	unsigned long new_tb;
    - 	unsigned int ci_start, ci_off, ci_end;
    - 	new_tb = folio_to_swp_tb(folio, 0);
    - 	ci_start = swp_cluster_offset(entry);
    - 	ci_off = ci_start;
    - 	ci_end = ci_start + nr_pages;
    + 	unsigned int ci_off = swp_cluster_offset(entry), ci_end;
    + 	unsigned long pfn = folio_pfn(folio);
    + 	unsigned long old_tb;
    + 	ci_end = ci_off + nr_pages;
    + 		old_tb = __swap_table_get(ci, ci_off);
    + 		VM_WARN_ON_ONCE(swp_tb_is_folio(old_tb));
  - `mm/swap_table.h` (code, fallback)
    + static inline unsigned long __swp_tb_mk_count(unsigned long swp_tb, int count)
    + {
    + 	return ((swp_tb & ~SWP_TB_COUNT_MASK) | __count_to_swp_tb(count));
    + }
    + 
- `triaged:alert-ac78fb17df858a0b` — Documentation lists models with ':cloud' suffix (e.g. glm-4.7:cloud, kimi-k2.5:cloud) as cloud models available without pulling, but the server code removed all ':cloud' suffix routing, cloud proxy passthrough middleware, and cloud model name normalization, so these models are no longer handled as cloud models by the server.  
  https://github.com/ollama/ollama/commit/97d2f05a6d74e843eb8c49ec537394b12bb80be9
  before/after (real commit):
  - `cmd/tui/tui.go` (code, matched)
    - 	"github.com/ollama/ollama/internal/modelref"
    - 	if name == "" {
    - 		return false
    - 	}
    - 	if modelref.HasExplicitCloudSource(name) {
    - 		return true
    + 	if m.availableModels == nil || name == "" {
    + 	return strings.HasSuffix(name, ":cloud") || strings.HasSuffix(name, "-cloud")
  - `server/create.go` (code, matched)
    - 			fromRef, err := parseAndValidateModelRef(r.From)
    - 			if err != nil {
    - 
    - 			fromName := fromRef.Name
    - 			remoteHost := r.RemoteHost
    - 			if fromRef.Source == modelSourceCloud && remoteHost == "" {
    + 			fromName := model.ParseName(r.From)
    + 			if !fromName.IsValid() {
    + 			if r.RemoteHost != "" {
    + 				ru, err := remoteURL(r.RemoteHost)
    + 				config.RemoteModel = r.From
  - `server/routes.go` (code, matched)
    - func writeModelRefParseError(c *gin.Context, err error, fallbackStatus int, fallbackMessage string) {
    - 	switch {
    - 	case errors.Is(err, errConflictingModelSource):
    - 		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
    - 	case errors.Is(err, model.ErrUnqualifiedName):
    - 		c.JSON(http.StatusBadRequest, gin.H{"error": errtypes.InvalidModelNameErrMsg})
    + 	name := model.ParseName(req.Model)
    + 	if !name.IsValid() {
    + 		// Ideally this is "invalid model name" but we're keeping with
    + 		// what the API currently returns until we can change it.
    + 		c.JSON(http.StatusNotFound, gin.H{"error": fmt.Sprintf("model '%s' not found", req.Model)})
    + 	name, err := getExistingName(model.ParseName(req.Model))
  - `x/cmd/run.go` (code, matched)
    - 	"github.com/ollama/ollama/internal/modelref"
    - 	return !modelref.HasExplicitCloudSource(modelName)
    + 	return !strings.HasSuffix(modelName, "-cloud")
- `triaged:alert-afab96e198ea0897` — English KASAN documentation removed the paragraph about SLUB and SLAB allocator support, but Chinese (zh_CN) translation still contains the outdated statement that software KASAN modes support both SLUB and SLAB allocators.  
  https://github.com/torvalds/linux/commit/9de209c183de3a52220b37262e2a0e0d52719de5
  before/after (real commit):
  - `Documentation/dev-tools/kasan.rst` (doc, matched)
    - For slab, both software KASAN modes support SLUB and SLAB allocators, while
    - Hardware Tag-Based KASAN only supports SLUB.
    - 
- `triaged:alert-e1e71cc1ff2a6985` — Documentation references xla/service/gpu/tests which no longer exists after rename to xla/backends/gpu/tests.  
  https://github.com/tensorflow/tensorflow/commit/0d5d53b93cecfc3c11f62704608055e8e8be0ba6
  before/after (real commit):
  - `third_party/xla/xla/backends/gpu/tests/bitcast-convert.hlo` (code, matched)
    - // RUN: hlo-opt %s --platform=gpu --xla_gpu_target_config_filename=%S/../../../backends/gpu/target_config/specs/%{GPU}.txtpb | FileCheck  %s
    + // RUN: hlo-opt %s --platform=gpu --xla_gpu_target_config_filename=%S/../target_config/specs/%{GPU}.txtpb | FileCheck  %s
- `triaged:alert-f05c17f47af4d5e0` — GDB/Binutils Rust symbol demangling advice was removed from English docs but remains in Chinese translation.  
  https://github.com/torvalds/linux/commit/a4392ed1c8b985e0a3dbad2739445e52c1c5543c
  before/after (real commit):
  - `Documentation/rust/quick-start.rst` (doc, fallback)
    - 
    - If GDB/Binutils is used and Rust symbols are not getting demangled, the reason
    - is the toolchain does not support Rust's new v0 mangling scheme yet.
    - There are a few ways out:
    - 
    - - Install a newer release (GDB >= 10.2, Binutils >= 2.36).
- `triaged:alert-f16567688f5ba11f` — Kconfig help text for CONFIG_KEXEC_HANDOVER_DEBUGFS still says the debugfs interface allows finalizing the state or aborting the finalization, but the finalization interface has been removed from the code and is no longer listed in the debugfs interfaces documentation.  
  https://github.com/torvalds/linux/commit/6b0dd42d7681af148e13df3806f251bc3dc7c36e
  before/after (real commit):
  - `Documentation/admin-guide/mm/kho.rst` (doc, matched)
    - First, before you perform a KHO kexec, you need to move the system into
    - the :ref:`KHO finalization phase <kho-finalization-phase>` ::
    - 
    -   $ echo 1 > /sys/kernel/debug/kho/out/finalize
    - 
    - After this command, the KHO FDT is available in
    + To perform a KHO kexec, load the target payload and kexec into it. It
    + is important that you use the ``-s`` parameter to use the in-kernel
    + kexec file loader, as user space kexec tooling currently has no
    + support for KHO with the user space based file loader ::
    + These debugfs interfaces are available when the kernel is compiled with
    + ``CONFIG_KEXEC_HANDOVER_DEBUGFS`` enabled.
- `triaged:alert-f496c550f01827a6` — Documentation references acenic driver which was removed by this commit.  
  https://github.com/torvalds/linux/commit/e6b7e1a10cba354e9fd5b10e3a83359f84ad8535
  before/after (real commit):
  - `MAINTAINERS` (code, fallback)
    - ACENIC DRIVER
    - M:	Jes Sorensen <jes@trained-monkey.org>
    - L:	linux-acenic@sunsite.dk
    - S:	Maintained
    - F:	drivers/net/ethernet/alteon/acenic*
    - 
  - `arch/loongarch/configs/loongson32_defconfig` (code, fallback)
    - # CONFIG_NET_VENDOR_ALTEON is not set
  - `arch/loongarch/configs/loongson64_defconfig` (code, fallback)
    - # CONFIG_NET_VENDOR_ALTEON is not set
  - `arch/mips/configs/cavium_octeon_defconfig` (code, fallback)
    - # CONFIG_NET_VENDOR_ALTEON is not set
  - `arch/mips/configs/loongson2k_defconfig` (code, fallback)
    - # CONFIG_NET_VENDOR_ALTEON is not set

**Raw (separate pool)**
- `raw:Significant-Gravitas/AutoGPT:0215332386b59f684ef2042945a550260b7f34ea:0` — README references `stream_chat_completion` function which no longer exists; users trying to call it will get import errors.
- `raw:Significant-Gravitas/AutoGPT:0215332386b59f684ef2042945a550260b7f34ea:1` — README mentions `max_retries` or `thinking_enabled` config options that were removed; users configuring these will see no effect or errors.
- `raw:Significant-Gravitas/AutoGPT:0215332386b59f684ef2042945a550260b7f34ea:4` — README documents the streaming chat completion flow using the old service, but the new baseline service has different behavior or parameters (e.g., `context` param removed).
- `raw:Significant-Gravitas/AutoGPT:0728f3bd49fd9466c283bd406bb2764f29390f46:1` — README instructs users to configure scopes for Google Drive integration, but the scopes for documents and spreadsheets have been removed.
- `raw:Significant-Gravitas/AutoGPT:0a1591fce23fca4936686e4172fd46e8c6d0470c:0` — README describes how to use the legacy builder (e.g., BlocksControl, SaveControl, CustomNode) but those components are deleted.
- `raw:Significant-Gravitas/AutoGPT:0a1591fce23fca4936686e4172fd46e8c6d0470c:1` — README references the monitoring page for viewing agent runs, but the monitoring page and its routes are removed.
- `raw:Significant-Gravitas/AutoGPT:0a1591fce23fca4936686e4172fd46e8c6d0470c:3` — README mentions export/import functionality for agents, which is implemented in deleted monitoring components.
- `raw:Significant-Gravitas/AutoGPT:0b267f573e6d4b7806654d38abb3fbe61913c81b:0` — README references `json_format` parameter in API usage; it has been removed.
- `raw:Significant-Gravitas/AutoGPT:0e72e1f5e7bf8ce48c3c6b2e724c6cc6ba6396a0:0` — README documents the endpoint GET /api/chat/tasks/{task_id}/stream for reconnection, but that endpoint is removed in this commit.
- `raw:Significant-Gravitas/AutoGPT:0e72e1f5e7bf8ce48c3c6b2e724c6cc6ba6396a0:1` — README documents the endpoint POST /api/chat/operations/{operation_id}/complete for external webhook, but that endpoint is removed.
- `raw:Significant-Gravitas/AutoGPT:0e72e1f5e7bf8ce48c3c6b2e724c6cc6ba6396a0:3` — README mentions `check_operation_status` tool, which is deleted.
- `raw:Significant-Gravitas/AutoGPT:0e72e1f5e7bf8ce48c3c6b2e724c6cc6ba6396a0:4` — README documents `is_long_running` property or `OperationStartedResponse`/`OperationPendingResponse` models, which are removed.
- `raw:Significant-Gravitas/AutoGPT:0e72e1f5e7bf8ce48c3c6b2e724c6cc6ba6396a0:5` — README references the frontend route `/chat/tasks/[taskId]/stream` which is deleted.
- `raw:Significant-Gravitas/AutoGPT:113df689dc587a90fd4a9e8aadcc28d6a1f7f997:0` — README documents how to use `GoogleDrivePickerField` which no longer exists, causing users to encounter import errors.
- `raw:Significant-Gravitas/AutoGPT:113df689dc587a90fd4a9e8aadcc28d6a1f7f997:3` — README references `GoogleDriveAttachmentField` which has been removed, leading to confusion.
- … 279 more in `bank.json`

## `identifier-drift` — identifier (SYMBOL_EXISTS)

**Triaged (primary)**
- `triaged:alert-4a2f8a3f229f0f7f` — FORM_CREATOR.md FieldTemplate code example destructures id but actual code renames it to id: fieldId.  
  https://github.com/Significant-Gravitas/AutoGPT/commit/cf6e724e99ef288f743e63aa3b092576a6940911
  before/after (real commit):
  - `autogpt_platform/frontend/src/app/(platform)/build/components/FlowEditor/nodes/templates/FieldTemplate.tsx` (code, matched)
    -   id,
    -   const {
    -     isArrayItem,
    -     fieldKey: arrayFieldKey,
    -     isConnected: isArrayItemConnected,
    -   } = useContext(ArrayEditorContext);
    +   id: fieldId,
    +   const { isArrayItem, arrayFieldHandleId } = useContext(ArrayEditorContext);
    +   let handleId = null;
    +   if (!isArrayItem) {
    +     handleId = generateHandleId(fieldId);
    +   } else {
- `triaged:alert-4e6ffd8b9ad6347e` — FORM_CREATOR.md ArrayEditorContext uses fieldKey but actual code renamed it to arrayFieldHandleId.  
  https://github.com/Significant-Gravitas/AutoGPT/commit/cf6e724e99ef288f743e63aa3b092576a6940911
  before/after (real commit):
  - `autogpt_platform/frontend/src/app/(platform)/build/components/FlowEditor/components/ArrayEditor/ArrayEditorContext.tsx` (code, matched)
    -   fieldKey: string;
    -   fieldKey: "",
    +   arrayFieldHandleId: string;
    +   arrayFieldHandleId: "",
- `triaged:alert-90c9797475f8f79a` — Documentation references 'spring-boot-starter-amqp' starter which was renamed to 'spring-boot-starter-rabbitmq' in this commit.  
  https://github.com/spring-projects/spring-boot/commit/72b8a6ca057ea9bfb9260f46f59e08e560d99600
  before/after (real commit):
  - `starter/spring-boot-starter-rabbitmq/build.gradle` (code, matched)
    - 	api(project(":module:spring-boot-amqp"))
    + 	api(project(":module:spring-boot-rabbitmq"))
- `triaged:alert-e4613ce0dc642fdc` — Documentation describes struct uio_info field as 'mmap' with signature (struct uio_info*, struct vm_area_struct*), but code has renamed it to 'mmap_prepare' with signature (struct uio_info*, struct vm_area_desc*).  
  https://github.com/torvalds/linux/commit/933f05f58ac6014eaac387d22a76ace8606891d1
  before/after (real commit):
  - `include/linux/uio_driver.h` (code, matched)
    -  * @mmap:		mmap operation for this uio device
    - 	int (*mmap)(struct uio_info *info, struct vm_area_struct *vma);
    +  * @mmap_prepare:	mmap_prepare operation for this uio device
    + 	int (*mmap_prepare)(struct uio_info *info, struct vm_area_desc *desc);
- `triaged:ident-casehub-incident-summary` — Documentation references `IncidentSummaryDto`, but the identifier was renamed to `IncidentSummaryResponse`.  
  https://github.com/casehubio/soc/commit/a38e2e1ad72ede05fa819efd9f8f6c4bde8f05d4
  before/after (real commit):
  - `docs/specs/issue-32-incident-summary-createdat/2026-08-18-incident-summary-createdat-design.md` (doc, matched)
    - `SocIncidentResource.toSummary()` passes `Instant.now()` to the `createdAt` field of `IncidentSummaryDto`. The timestamp changes on every API call instead of reflecting when the incident was actually created.
    - The `import java.time.Instant` can be removed since `IncidentSummaryDto` already imports it and `toSummary()` no longer references `Instant` directly.
    + `SocIncidentResource.toSummary()` passes `Instant.now()` to the `createdAt` field of `IncidentSummaryResponse`. The timestamp changes on every API call instead of reflecting when the incident was actually created.
    + The `import java.time.Instant` can be removed since `IncidentSummaryResponse` already imports it and `toSummary()` no longer references `Instant` directly.
- `triaged:ident-immosquare-my-ip` — Documentation references `get_my_ip_from_aws`, but the identifier was renamed to `my_ip_from_aws`.  
  https://github.com/immosquare/immosquare-constants/commit/92ab4acea6a497ddcbd53641fcbbcb655379eff5
  before/after (real commit):
  - `CLAUDE.md` (doc, matched)
    - | Module     | Fichier                              | Description                                                                                                                                                                                                                         |
    - | ---------- | ------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
    - | **Ip**     | `lib/immosquare-constants/ip.rb`     | Détection IP (local, public, client) via `get_ips`, IP publique via `get_my_ip_from_aws`, résolution DNS du host (CDN/reverse proxy) via `get_front_ip`. `IpResult` expose les formats JSON/hash/array et `each`/`each_with_index`. |
    - | **Locale** | `lib/immosquare-constants/locale.rb` | Mapping codes locales → noms natifs (`:fr`, `:"fr-CA"`). Constante `LOCALES`, méthodes `native_name_for_locale`, `languages_with_native_names`.                                                                                     |
    - | **Color**  | `lib/immosquare-constants/color.rb`  | Mapping noms CSS → hex. Constante `COLORS`, lookup case-insensitive.                                                                                                                                                                |
    - | **Regex**  | `lib/immosquare-constants/regex.rb`  | Validation email : `email_raw`, `email`, `email_in_string`.                                                                                                                                                                         |
    + | Module     | Fichier                              | Description                                                                                                                                                                                                                                                                                                                                    |
    + | ---------- | ------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
    + | **Ip**     | `lib/immosquare-constants/ip.rb`     | Détection IP (local, public, client) via `get_ips`, IP publique via `my_ip_from_aws` (alias déprécié `get_my_ip_from_aws`, retrait à partir de 2027-01, timeouts de connexion et de lecture de 2 s), résolution DNS du host (CDN/reverse proxy) via `get_front_ip`. `IpResult` expose les formats JSON/hash/array et `each`/`each_with_index`. |
    + | **Locale** | `lib/immosquare-constants/locale.rb` | Mapping codes locales → noms natifs (`:fr`, `:"fr-CA"`). Constante `LOCALES`, méthodes `native_name_for_locale`, `languages_with_native_names`.                                                                                                                                                                                                |
    + | **Color**  | `lib/immosquare-constants/color.rb`  | Mapping noms CSS → hex. Constante `COLORS`, lookup case-insensitive.                                                                                                                                                                                                                                                                           |
    + | **Regex**  | `lib/immosquare-constants/regex.rb`  | Validation email : `email_raw`, `email`, `email_in_string`.                                                                                                                                                                                                                                                                                    |
- `triaged:ident-nseindia-list-sme` — Documentation references `listSme`, but the identifier was renamed to `list_sme`.  
  https://github.com/BennyThadikaran/NseIndiaApi/commit/0e0a77bb98eac005fdabcaca51b6e14f8da59e79
  before/after (real commit):
  - `src/nse/NSE.py` (code, matched)
    -         :param data: Output of one of :meth:`listSme` or
    -             :meth:`listEquityStocksByIndex`.
    -         :param data: Output of one of :meth:`listSme` or
    -             :meth:`listEquityStocksByIndex`.
    +         :param data: Output of one of :meth:`list_sme` or
    +             :meth:`list_equity_stocks_by_index`.
    +         :param data: Output of one of :meth:`list_sme` or
    +             :meth:`list_equity_stocks_by_index`.
- `triaged:ident-silo-refresh-devices` — Documentation references `refreshComputers`, but the identifier was renamed to `refreshDevices`.  
  https://github.com/amontlabs/silo/commit/d70ae0855e53f10ad0d754d9511a8264bc54472e
  before/after (real commit):
  - `docs/SiloUI-CHECKPOINTS-PLAN.md` (doc, matched)
    - [`refreshComputers`](../app/SiloUI/src/desktop/production-source.ts) and
    + [`refreshDevices`](../app/SiloUI/src/desktop/production-source.ts) and

**Raw (separate pool)**
- `raw:Significant-Gravitas/AutoGPT:05aaf7a85e3d266d61750528afba48a29d6d7992:1` — Setup documentation lists linear_api_key as a configuration option, but it has been renamed to copilot_linear_api_key.
- `raw:Significant-Gravitas/AutoGPT:08a60dcb9b33dfe486d1be0cf6bfe1c792dbd63b:1` — If the README references any of the renamed variables or refactored hooks, those references could be stale, but unlikely.
- `raw:Significant-Gravitas/AutoGPT:1ddf92eed4e933fdb19457c341600a0570a3b395:0` — If the README describes the 'RunDetails' component, it has been renamed to 'SelectedRunView'.
- `raw:Significant-Gravitas/AutoGPT:27b72062f2768fb59a6dd609374220f04c9fff0c:1` — README references the deprecated shouldShowOnboarding function; it has been renamed to getOnboardingStatus.
- `raw:Significant-Gravitas/AutoGPT:3b1b2fe30cc4428f3ebf595c301a3193ef5edaa7:3` — README documents SSE response types (e.g., text_chunk, tool_call) that have been renamed to AI SDK protocol types (text-delta, tool-input-available, etc.).
- `raw:Significant-Gravitas/AutoGPT:50622333d1f086576cbd262a7c0e9fad42f18203:0` — README mentions _SDK_PROJECTS_DIR constant; it is now renamed to SDK_PROJECTS_DIR.
- `raw:Significant-Gravitas/AutoGPT:7d2ab61546812613e098da65efb7e836aeb3a770:2` — README references 'FlowContext' in code examples or context descriptions, but it is now renamed to 'BuilderContext'.
- `raw:Significant-Gravitas/AutoGPT:8fddc9d71fa4c8d37f55a6124858ecb1ef43db20:1` — README references BaseGraph class – now renamed to GraphBaseMeta.
- `raw:Significant-Gravitas/AutoGPT:acb946801b40f8dd36f1d806d988c8fde762612c:0` — If the README or a developer guide mentions the exact path autogpt_platform/frontend/src/app/(platform)/build/components/FlowEditor/Flow/GraphLoadingBox.tsx, that reference would be broken after the rename to .../Flow/components/GraphLoadingBox.tsx. However, such detailed file paths are not typically documented in the README.
- `raw:Significant-Gravitas/AutoGPT:bc75d70e7d4e5603d362987ed4e24682d71a43c6:0` — README documents the tool 'agent_output' for chat; after rename to 'view_agent_output', users following README will encounter errors when using that tool.
- `raw:Significant-Gravitas/AutoGPT:dd84fb5c66883c4f7a4306a258b01ea3315c4f0c:4` — README references the old index names (e.g., `APIKey_key_key`) that were renamed in the migration, though this is less likely to be documented.
- `raw:facebook/react:71b3a03cc936c8eb30a6e6108abf5550f5037f71:1` — README documents option 'numRequiredArgs' which is renamed to 'autodepsIndex'.
- `raw:facebook/react:72848027a5525d7beebeccb0a485f4f211a1a101:1` — README may describe error categories that have been renamed
- `raw:facebook/react:7513996f20e34070141aa605fe282ca6986915a0:1` — README references `stackToComponentSources` function, which is renamed to `stackToComponentLocations`.
- `raw:facebook/react:78992521a83325edec17a0dc0bb47092cc5accaa:1` — README references `isError()` method which now has different semantics and is renamed to `hasErrors()`
- … 10 more in `bank.json`
