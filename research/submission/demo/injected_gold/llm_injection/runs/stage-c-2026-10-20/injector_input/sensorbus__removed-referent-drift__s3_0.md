# Injection task

corpus repository: `sensorbus`

# Injector — natural documentation defects

You are given one documentation-drift type, a clean repository, and a few real
incident excerpts. Propose **one** concrete inconsistency between the
documentation and the repository, of exactly the requested type.

## Rules

1. **One drift type only.** Use the type named by the per-class task. Do not
   combine types or invent a new one.
2. **Choose a natural current-state statement.** Pick a statement in the
   documentation that a maintainer would treat as a current, checkable fact
   about the project — something a reader could rely on. Prefer ordinary
   present-tense statements. Avoid historical notes, examples, conditionals,
   proposals, and statements that are already ambiguous.
3. **Name a real artifact.** The statement must refer to something that actually
   exists in this repository: a file or directory, a class or function, or a
   dependency the project manifest lists. Do not invent anything.
4. **Make the smallest concrete change.** Change the artifact (or, only where
   the class says so, the document) in a way that makes the chosen statement
   false. The change must be a concrete edit to a named artifact: rename or move
   a file, rename or delete a class/function definition, or change/remove a
   dependency in the project manifest.
5. **Do not optimize for a checker.** Choose the target and the change the way a
   maintainer would, from the documentation and the repository. Do not reason
   about any analysis or verification tool, and do not avoid a natural target
   because you think some tool might miss it.
6. **If nothing fits, decline.** If the repository has no natural current-state
   statement of the requested type, return
   `{"injectable": false, "reason": "<short reason>"}`.
7. **Output exactly one JSON object.** No Markdown fence, no commentary, no
   text outside the object. The `rationale` field is a single short field, not
   prose around the object.

## Process

1. Read the per-class task.
2. Read the repository inventory and document excerpts.
3. Choose one statement and one artifact.
4. Check that the artifact exists and the document line is copied exactly.
5. Run the self-check, then emit the JSON object.

## Self-check

- [ ] The drift type is exactly the requested one.
- [ ] The chosen statement is a current-state statement, not historical,
      illustrative, conditional, or already ambiguous.
- [ ] The artifact exists in the repository under the name used.
- [ ] `doc_path` and `doc_line_text` are copied verbatim from the document.
- [ ] The change is minimal and makes exactly that statement false.
- [ ] The named file still parses after the change.
- [ ] No other kind of defect is introduced as a side effect.
- [ ] `exemplar_ids` lists the exemplar ids that informed target selection.


---

# Injector — removed-referent drift

**Defect.** A document names a class or function as current API, but that
definition is deleted from the code. The document is left unchanged, so it names
something that no longer exists.

- **Artifact:** a class or function defined in the repository.
- **Direction:** change the code; leave the document unchanged.

## What to look for

Choose a statement that presents a class or function as current, available API.
Do not choose a name that is already described as deprecated, historical, or
illustrative.

The mutation removes a **definition** (a top-level class or function), not a
method or an attribute. Prefer a definition that is not imported or called
elsewhere, so the rest of the tree still parses after the removal.

## The change

Delete the definition as a whole block. The old name must be absent after the
change and the file must still parse. The document line must still name the
**deleted** symbol.

## Output

Emit one JSON object:

```json
{
  "injectable": true,
  "drift_type": "removed-referent-drift",
  "direction": "code_side",
  "file": "<source file that defines the symbol>",
  "old": "<the name as the document writes it>",
  "new": null,
  "symbol": "<bare symbol name>",
  "target": "<the exact name text as written on the document line>",
  "doc_path": "<document file, relative to the repository>",
  "doc_line_text": "<the exact current document line>",
  "target_claim": "<the statement the document makes that the removal falsifies>",
  "exemplar_ids": ["..."],
  "rationale": "<one sentence: why this is a natural current-API statement>"
}
```

If no natural current-API statement exists, emit:

```json
{"injectable": false, "reason": "<short reason>"}
```

## Repository inventory

files:
  README.md, docs/concepts.md, docs/usage.md, examples/curve_nitrate.csv, pyproject.toml, sensorbus/__init__.py, sensorbus/bus.py, sensorbus/calibration.py, sensorbus/devices.py, sensorbus/readings.py, sensorbus/units.py, spec.json
symbols:
  sensorbus.bus.Bus, sensorbus.bus.collect, sensorbus.calibration.CalibrationCurve, sensorbus.calibration.fit_curve, sensorbus.devices.SerialDevice, sensorbus.devices.list_devices, sensorbus.readings.Reading, sensorbus.readings.ReadingBatch, sensorbus.readings.parse_line, sensorbus.units.canonical_unit, sensorbus.units.convert
dependencies:
  numpy>=1.24, pint>=0.23, pyserial>=3.5
string literals:
  0.4.1, Module sensorbus/bus.py., Module sensorbus/calibration.py., Module sensorbus/devices.py., Module sensorbus/readings.py., Module sensorbus/units.py., Package sensorbus., Project class., Project function., default_order, default_window, registry

## Document excerpts

### README.md
   1: # sensorbus
   2: 
   3: `sensorbus` is a small library for getting numbers out of lab instruments and
   4: into a shape you can reason about. It has four jobs: talk to a serial port, turn
   5: what comes off the wire into a timestamped `Reading` tagged with a unit, correct
   6: that reading against a stored calibration curve, and convert the result into
   7: whatever unit the person downstream asked for.
   8: 
   9: It is aimed at people who have a bench full of probes — a nitrate electrode, a
  10: pH meter, a flow sensor — each with its own calibration sheet and its own idea
  11: of what unit it reports in, and who would rather keep that bookkeeping in one
  12: place than in a folder of ad-hoc scripts.
  13: 
  14: The package is version 0.4.1 and requires Python 3.11 or newer.
  15: 
  16: ## Status
  17: 
  18: The 0.4.1 tree publishes the module layout and the public names described
  19: below, but the pipeline is not wired up yet. The transform functions —
  20: `parse_line`, `fit_curve`, `convert`, `canonical_unit`, `collect`, and
  21: `list_devices` — are declared and currently return `None`, and the module
  22: constants hold placeholder strings (`"default_order"`, `"registry"`,
  23: `"default_window"`). The data classes are real classes with their attributes
  24: initialised to `None`, so you can construct and populate them today; the
  25: arithmetic that would make them useful is still to be written.
  26: 
  27: ## Installation
  28: 
  29: From a checkout of the repository:
  30: 
  31: ```console
  32: pip install .
  33: ```
  34: 
  35: For development, install the package in place so edits take effect without
  36: reinstalling:
  37: 
  38: ```console
  39: pip install -e .
  40: ```
  41: 
  42: Dependencies are declared in `pyproject.toml`: `pyserial>=3.5`, `numpy>=1.24`,
  43: and `pint>=0.23`.
  44: 
  45: ## Quick start
  46: 
  47: The objects are the stable part of the API, so the shortest useful thing you can
  48: do is build the values you would eventually hand to the pipeline.
  49: 
  50: ```python
  51: from sensorbus import __version__
  52: from sensorbus.readings import Reading, ReadingBatch
  53: from sensorbus.calibration import CalibrationCurve
  54: 
  55: reading = Reading()
  56: reading.sensor_id = "nitrate-01"
  57: reading.value = 4.91
  58: reading.unit = "mg/L"
  59: 
  60: batch = ReadingBatch()
  61: batch.sensor_id = "nitrate-01"
  62: batch.readings = [reading]
  63: 
  64: curve = CalibrationCurve()
  65: curve.sensor_id = "nitrate-01"
  66: curve.reference_unit = "mg/L"
  67: curve.coefficients = [0.03, 0.998]
  68: 
  69: print(__version__, batch.sensor_id, len(batch.readings))
  70: ```
  71: 
  72: There is a worked calibration file in the repository, `examples/curve_nitrate.csv`,
  73: which pairs reference values for the `nitrate-01` channel with the response the
  74: instrument actually produced:
  75: 
  76: ```csv
  77: sensor_id,reference,observed
  78: nitrate-01,0.00,0.03
  79: nitrate-01,1.00,1.05
  80: nitrate-01,5.00,4.91
  81: nitrate-01,10.00,10.12
  82: nitrate-01,25.00,24.78
  83: ```
  84: 
  85: That file is the input `fit_curve` is meant to consume: one row per calibration
  86: point, grouped by `sensor_id`, giving you a `CalibrationCurve` with fitted
  87: `coefficients` and the `reference_unit` the fit is expressed in.
  88: 
  89: ## Main concepts
  90: 
  91: **Readings.** A `Reading` is one number from one sensor at one time: `sensor_id`,
  92: `value`, `unit`, `timestamp`. It is deliberately unopinionated — the unit is a
  93: string carried alongside the value, not baked into it. A `ReadingBatch` groups
  94: readings from a single channel (`sensor_id`, `readings`), which is what a single
  95: collection pass returns.
  96: 
  97: **Calibration curves.** A `CalibrationCurve` holds the per-sensor correction:
  98: `sensor_id`, `coefficients` (an ordered list, so the polynomial order is implied
  99: by its length), and `reference_unit`. `DEFAULT_ORDER` is the module-level
 100: setting for the order used when you do not choose one.
 101: 
 102: **Units.** `convert` maps a value from one unit to another; `canonical_unit`
 103: answers what unit a given quantity should be stored in. `REGISTRY` is the
 104: module-level unit registry both of them consult, so unit names are resolved in
 105: one place instead of being parsed ad hoc at every call site.
 106: 
 107: **The bus.** A `Bus` is the collection point. It carries a `registry` (the unit
 108: registry in use), `curves` (the calibration curves available, keyed by sensor),
 109: and `window` (how much time a single collection pass covers). `collect` runs a
 110: pass over the devices and returns a `ReadingBatch`; `DEFAULT_WINDOW` is the
 111: window used when you do not set one.
 112: 
 113: **Devices.** `SerialDevice` describes a port you can read from — `port`,
 114: `baudrate`, `name` — and `list_devices` enumerates the serial ports the host
 115: presents.
 116: 
 117: ## Documentation
 118: 
 119: - [`docs/usage.md`](docs/usage.md) — a worked how-to for a bench with more than
 120:   one channel, mixed units, and per-sensor calibration.
 121: - [`docs/concepts.md`](docs/concepts.md) — why the library is split into these
 122:   layers, and what each layer owns.
### docs/concepts.md
   1: # Concepts
   2: 
   3: This document explains how `sensorbus` is put together and why it is split the
   4: way it is. It is about the design, not about calling the API; if you want the
   5: procedure, read [`usage.md`](usage.md).
   6: 
   7: The library has five modules, and they form a pipeline in one direction:
   8: 
   9: ```
  10: devices.py     ->  readings.py  ->  calibration.py  ->  units.py
  11:  (a port)           (a number)       (a correction)      (a name for it)
  12: 
  13:                         bus.py
  14:               (holds registry + curves + window,
  15:                runs one pass, returns a batch)
  16: ```
  17: 
  18: `bus.py` is the odd one out: it does not add a new data type so much as hold the
  19: other four together for the length of a collection pass. In 0.4.1 the modules
  20: publish their names and data shapes but the functions that would move data
  21: between them are stubs — `parse_line`, `fit_curve`, `convert`, `canonical_unit`,
  22: `collect`, and `list_devices` all return `None`. The layering described here is
  23: the structure those functions are meant to fill in.
  24: 
  25: ## Why a reading is a value plus a unit, not a quantity
  26: 
  27: `Reading` has four attributes: `sensor_id`, `value`, `unit`, `timestamp`. There
  28: is no arithmetic on a `Reading` and no normalisation inside it. The unit is
  29: carried as a string next to the number.
  30: 
  31: That is a deliberate refusal to guess. An instrument hands you a number in
  32: whatever unit its firmware was configured for, and that configuration changes
  33: between probes and sometimes between firmware versions. If `Reading` tried to be
  34: a physically meaningful quantity, it would have to decide *when* the unit is
  35: known, and the only moment it is reliably known is at the wire. So the rule is:
  36: `Reading.unit` is whatever the device said, and conversion happens later, at a
  37: boundary, exactly once.
  38: 
  39: `ReadingBatch` follows from the same reasoning. It has `sensor_id` and
  40: `readings`, and only one `sensor_id` — a batch is a single channel's worth of
  41: data. It would be convenient to return everything from a pass in one object, but
  42: then the batch-level `sensor_id` could only be one of several values, and every
  43: consumer would have to re-group. One batch per channel keeps that field honest
  44: and makes a consumer that only knows about one probe trivially possible.
  45: 
  46: ## Why calibration is a stored object rather than a function argument
  47: 
  48: `CalibrationCurve` carries `sensor_id`, `coefficients`, and `reference_unit`.
  49: The point of making it an object is that a curve is a *fact about a sensor* that
  50: outlives any single collection pass. You fit it when the probe is installed,
  51: store it, and reuse it until the next calibration event.
  52: 
  53: `coefficients` is an ordered list, so the order of the polynomial is implicit in
  54: its length; `DEFAULT_ORDER` names the order used when nobody asks for a specific
  55: one. `fit_curve` is the constructor for the whole object: it takes calibration
  56: points and produces a curve. The example file in the repository,
  57: `examples/curve_nitrate.csv`, shows the shape of those points — `sensor_id`,
  58: `reference`, `observed`, five rows for `nitrate-01`. `reference` is the value the
  59: sensor *should* have read; `observed` is what it did read. Fitting those pairs
  60: against each other is what makes a correction possible at all.
  61: 
  62: `reference_unit` deserves its own note. A curve maps raw response onto a
  63: reference scale, and that scale has a unit. Putting it on the curve rather than
  64: on the reading means the unit travels with the coefficients that produce it, so
  65: the two can never drift apart.
  66: 
  67: The obvious alternative — pass coefficients into every conversion call — is what
  68: this design is avoiding. It works fine for one probe and becomes unmanageable at
  69: five, because the mapping from sensor to coefficients ends up duplicated in
  70: every call site.
  71: 
  72: ## Why there is a registry, and why units are converted in one place
  73: 
  74: `units.py` exposes `convert`, `canonical_unit`, and `REGISTRY`. The registry is
  75: the single authority on what unit names mean; `convert` turns a value in one
  76: unit into a `float` in another; `canonical_unit` answers what unit a quantity
  77: should be stored in.
  78: 
  79: Two separate problems are being solved here. The first is mechanical: converting
  80: between units is arithmetic you should not reimplement, and the dependency on
  81: `pint` exists precisely so that it is not reimplemented. The second is social: on
  82: a bench, "the" unit for a measurement is a convention, not a fact. One lab
  83: reports nitrate in `mg/L`, another in `µmol/L`, and both are correct. Having a
  84: named canonical unit gives the convention a place to live, so that a batch can be
  85: normalised on the way out without every downstream script inventing its own
  86: answer.
  87: 
  88: The distinction between the two functions matters. `convert` is per-value and
  89: lossless in intent; `canonical_unit` is a policy decision. Keeping the policy in
  90: one function means changing lab conventions is a one-line change rather than a
  91: search across the codebase.
  92: 
  93: ## Why the bus holds a window
  94: 
  95: `Bus` has exactly three attributes: `registry`, `curves`, `window`. Two of them
  96: are collections of things already described — the unit registry in use, and the
  97: curves keyed by sensor. `window` is different: it describes the *pass*, not the
  98: data. `DEFAULT_WINDOW` is the value used when you do not choose one.
  99: 
 100: A collection pass needs a notion of scope. Without one, "collect" is ambiguous:
 101: does it return what is buffered right now, or everything since the last call? The
 102: window is the answer, and holding it on the bus rather than passing it to
 103: `collect` keeps every channel on the same horizon. That is what makes two
 104: channels comparable — a window set per sensor would produce batches that cover
 105: different spans and quietly cannot be plotted on one axis.
 106: 
 107: `collect` returns a `ReadingBatch`. It is the only function in the pipeline that
 108: touches every layer: it needs a device to read from, `parse_line` to make
 109: readings, the curve for that `sensor_id` to correct them, and the registry to
 110: express the result.
 111: 
 112: ## Why the device layer is so thin
 113: 
 114: `SerialDevice` is three attributes — `port`, `baudrate`, `name` — and
 115: `list_devices` is declared to return a `list[str]`. Nothing here tries to
 116: abstract over transport types.
 117: 
 118: That is on purpose. The interesting work in this library happens after bytes have
 119: become numbers, and a device abstraction deep enough to cover every instrument
 120: would be a project of its own. Keeping the device layer to "which port, at what
 121: speed, under what name" means the rest of the pipeline can be tested by
 122: constructing `Reading` objects directly, with no hardware and no serial port.
 123: 
 124: `name` is the one field that is not about the transport. It is the identity the
 125: device is known by downstream, which is why it is the field that has to agree
 126: with `Reading.sensor_id` and `CalibrationCurve.sensor_id`. The string is the only
 127: join key in the whole design; nothing enforces it at runtime, so it is the first
 128: thing to check when a reading comes back uncorrected.
 129: 
 130: ## Where the boundaries are
 131: 
 132: Summing up, the design puts each decision in exactly one place:
 133: 
 134: | Decision | Lives in |
 135: | --- | --- |
 136: | Which port, at what speed | `SerialDevice` |
 137: | What the device said, and in what unit | `Reading` |
 138: | Which readings belong together | `ReadingBatch` |
 139: | How this sensor is off, and against what scale | `CalibrationCurve` |
 140: | What a unit name means, and how to move between them | `REGISTRY`, `convert` |
 141: | Which unit to standardise on | `canonical_unit` |
 142: | How much time a pass covers | `Bus.window`, `DEFAULT_WINDOW` |
 143: 
 144: When something goes wrong, that table is the shortest route to the module that
 145: owns the problem.
### docs/usage.md
   1: # Usage
   2: 
   3: This guide assumes you have read the README and know what a `Reading`, a
   4: `CalibrationCurve`, and a `Bus` are. It walks through one concrete situation:
   5: you already have the `nitrate-01` channel working, and now a second nitrate
   6: probe is going on the bench. It reports in a different unit, it needs its own
   7: calibration, and both channels have to come back from a collection pass as one
   8: coherent set of numbers.
   9: 
  10: A note before the steps: in 0.4.1 the pieces that do arithmetic are still
  11: placeholders. `collect`, `convert`, `canonical_unit`, `fit_curve`,
  12: `parse_line`, and `list_devices` are declared but return `None`, and
  13: `REGISTRY`, `DEFAULT_ORDER`, and `DEFAULT_WINDOW` hold placeholder strings. The
  14: data classes work normally. So the procedure below is the sequence of objects
  15: you assemble, and where a step would call into the pipeline it says what that
  16: call is expected to produce.
  17: 
  18: ## 1. Find and describe the port
  19: 
  20: `SerialDevice` is a plain record of where to read from. Set the fields yourself
  21: if you already know the port name from your OS, or call `list_devices`, which is
  22: declared to return a `list[str]` of the serial ports the host presents.
  23: 
  24: ```python
  25: from sensorbus.devices import SerialDevice, list_devices
  26: 
  27: print(list_devices())          # currently returns None; see the status note
  28: 
  29: second = SerialDevice()
  30: second.name = "nitrate-02"
  31: second.port = "/dev/ttyUSB1"
  32: second.baudrate = 9600
  33: ```
  34: 
  35: Use the `name` you want to see in the data, not necessarily the one the OS
  36: assigned: `name` is what ties a device to a sensor id in the rest of the
  37: pipeline.
  38: 
  39: ## 2. Give the new channel its own curve
  40: 
  41: The new probe does not share `nitrate-01`'s calibration, even though both
  42: measure the same analyte. `fit_curve` takes calibration points and returns a
  43: `CalibrationCurve`; `DEFAULT_ORDER` is the module-level setting for the order
  44: used when you do not choose one. The points come from the same three-column
  45: layout as `examples/curve_nitrate.csv` — `sensor_id`, `reference`, `observed` —
  46: with the probe's own sheet supplying the values and its own id in the first
  47: column.
  48: 
  49: ```python
  50: import csv
  51: from sensorbus.calibration import CalibrationCurve, DEFAULT_ORDER, fit_curve
  52: 
  53: points = []
  54: with open("examples/curve_nitrate.csv", newline="") as handle:
  55:     for row in csv.DictReader(handle):
  56:         points.append(row)
  57: # in practice the file would be the second probe's own sheet; the columns are
  58: # the same either way
  59: 
  60: # The intended call: fit_curve(points) -> CalibrationCurve
  61: curve = fit_curve()
  62: if curve is None:
  63:     # 0.4.1 fallback: build the record by hand so downstream code has a shape
  64:     # to work with.
  65:     curve = CalibrationCurve()
  66:     curve.sensor_id = "nitrate-02"
  67:     curve.reference_unit = "mg/L"
  68:     curve.coefficients = [0.03, 0.998]
  69: 
  70: first_curve = CalibrationCurve()
  71: first_curve.sensor_id = "nitrate-01"
  72: first_curve.reference_unit = "mg/L"
  73: first_curve.coefficients = [0.03, 0.998]
  74: 
  75: print(DEFAULT_ORDER)  # placeholder string in 0.4.1
  76: ```
  77: 
  78: Two things are worth getting right here even while the fit is unimplemented:
  79: 
  80: - **`reference_unit` is part of the curve, not of the reading.** The curve
  81:   converts "what this probe said" into "the reference scale", and that scale has
  82:   a unit. Record it once on the curve instead of repeating it at every call
  83:   site.
  84: - **`sensor_id` on the curve must match the readings' `sensor_id`.** That
  85:   string is the only link between a batch of numbers and the correction that
  86:   applies to it.
  87: 
  88: ## 3. Register the curve on the bus
  89: 
  90: `Bus` exists to hold the things a collection pass needs, so you give it a
  91: dictionary of curves keyed by sensor id rather than passing a curve to each
  92: call.
  93: 
  94: ```python
  95: from sensorbus.bus import Bus, DEFAULT_WINDOW
  96: 
  97: bus = Bus()
  98: bus.registry = None            # starts as None; set it to the registry to use
  99: bus.curves = {"nitrate-01": first_curve, "nitrate-02": curve}
 100: bus.window = DEFAULT_WINDOW    # or your own window
 101: ```
 102: 
 103: `window` is a property of the collection pass, not of a sensor: it answers "how
 104: much time does one `collect` call cover". Setting it on the bus keeps every
 105: channel on the same sampling horizon, which matters as soon as you want to
 106: compare two channels or average them together.
 107: 
 108: ## 4. Collect and get one batch back
 109: 
 110: ```python
 111: from sensorbus.bus import collect
 112: 
 113: batch = collect()   # intended: a ReadingBatch covering one channel
 114: ```
 115: 
 116: `collect` is declared to return a `ReadingBatch`, and a batch belongs to exactly
 117: one channel — it has a single `sensor_id` and a list of `readings`. Collecting
 118: two channels therefore means two batches, which is deliberate: it keeps the
 119: `sensor_id` on the batch from being a lie, and lets you hand a single channel's
 120: data to a consumer that knows nothing about the rest of the bench.
 121: 
 122: If you are assembling the batch yourself while the pipeline is incomplete, fill
 123: in both fields:
 124: 
 125: ```python
 126: from sensorbus.readings import Reading, ReadingBatch
 127: 
 128: raw = Reading()
 129: raw.sensor_id = "nitrate-02"
 130: raw.value = 5.08
 131: raw.unit = "mg/L"
 132: raw.timestamp = "2026-10-20T09:14:03"
 133: 
  … (truncated)

## Examples (few-shot)

Real incidents of this kind, rendered as bare `before → after` excerpts under a
`<file> (doc|code)` header. Use them to understand what kind of artifact tends to
drift; do not copy their wording or content.

### example 1
Documentation/dev-tools/kasan.rst (doc)
  - For slab, both software KASAN modes support SLUB and SLAB allocators, while
  - Hardware Tag-Based KASAN only supports SLUB.
  - 

### example 2
cmd/tui/tui.go (code)
  - 	"github.com/ollama/ollama/internal/modelref"
  - 	if name == "" {
  - 		return false
  - 	}
  - 	if modelref.HasExplicitCloudSource(name) {
  - 		return true
  - 	}
  - 	if m.availableModels == nil {
  + 	if m.availableModels == nil || name == "" {
  + 	return strings.HasSuffix(name, ":cloud") || strings.HasSuffix(name, "-cloud")
server/create.go (code)
  - 			fromRef, err := parseAndValidateModelRef(r.From)
  - 			if err != nil {
  - 
  - 			fromName := fromRef.Name
  - 			remoteHost := r.RemoteHost
  - 			if fromRef.Source == modelSourceCloud && remoteHost == "" {
  - 				remoteHost = cloudProxyBaseURL
  - 			}
  + 			fromName := model.ParseName(r.From)
  + 			if !fromName.IsValid() {
  + 			if r.RemoteHost != "" {
  + 				ru, err := remoteURL(r.RemoteHost)
  + 				config.RemoteModel = r.From

### example 3
third_party/xla/xla/backends/gpu/tests/bitcast-convert.hlo (code)
  - // RUN: hlo-opt %s --platform=gpu --xla_gpu_target_config_filename=%S/../../../backends/gpu/target_config/specs/%{GPU}.txtpb | FileCheck  %s
  + // RUN: hlo-opt %s --platform=gpu --xla_gpu_target_config_filename=%S/../target_config/specs/%{GPU}.txtpb | FileCheck  %s

### example 4
Documentation/admin-guide/mm/kho.rst (doc)
  - First, before you perform a KHO kexec, you need to move the system into
  - the :ref:`KHO finalization phase <kho-finalization-phase>` ::
  - 
  -   $ echo 1 > /sys/kernel/debug/kho/out/finalize
  - 
  - After this command, the KHO FDT is available in
  - ``/sys/kernel/debug/kho/out/fdt``. Other subsystems may also register
  - their own preserved sub FDTs under
  + To perform a KHO kexec, load the target payload and kexec into it. It
  + is important that you use the ``-s`` parameter to use the in-kernel
  + kexec file loader, as user space kexec tooling currently has no
  + support for KHO with the user space based file loader ::
  + These debugfs interfaces are available when the kernel is compiled with
  + ``CONFIG_KEXEC_HANDOVER_DEBUGFS`` enabled.
  + 
  +     The kernel exposes the flattened device tree blob that carries its

