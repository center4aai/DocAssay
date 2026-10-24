repo: ruff
docs=657 claims=16953 referents=2206 evidence=15710
code_verdicts: {'REFUTED': 232, 'NEI': 1746, 'SUPPORTED': 418}  coverage=0.27  resolved=650

PRECISION (stratified measurement): top-K=1000 sample/stratum=5
  review requested: 28 items in 10 strata
    DEPENDENCY       SUPPORTED       neg=0: 5
    DEPENDENCY       TRUE_CANDIDATE  neg=0: 2
    HAS_CI_WORKFLOW  SUPPORTED       neg=0: 1
    LICENSE          SUPPORTED       neg=0: 1
    PATH_EXISTS      SUPPORTED       neg=0: 5
    PATH_EXISTS      SYSTEMATIC      neg=0: 2
    PATH_EXISTS      TRUE_CANDIDATE  neg=0: 5
    PATH_EXISTS      TRUE_CANDIDATE  neg=1: 1
    SYMBOL_EXISTS    SUPPORTED       neg=0: 5
    SYMBOL_EXISTS    TRUE_CANDIDATE  neg=0: 1
  run `docassay consolidate <review.jsonl>` after labelling

FINDINGS (REFUTED, document order, first 232 of 232):
  1. PATH_EXISTS crates/ruff_linter/src/flake8_unused_arguments/settings.rs CONTRIBUTING.md:398-398
     tier: anchored
     raw: `Settings` in `crates/ruff_linter/src/flake8_unused_arguments/settings.rs` coupled with
  2. PATH_EXISTS reverse-changelog.py CONTRIBUTING.md:520-520
     tier: bare
     raw: [`reverse-changelog.py`](https://github.com/astral-sh/uv/blob/main/scripts/reverse-changelog.py)
  3. PATH_EXISTS flamegraph.svg CONTRIBUTING.md:877-877
     tier: bare
     raw: An alternative is to convert the perf data to `flamegraph.svg` using
  4. PATH_EXISTS .ruff.toml CONTRIBUTING.md:1080-1080
     tier: bare
     raw: "Project root": The directory containing the `pyproject.toml`, `ruff.toml`, or `.ruff.toml` file,
     cited by 15 claims
  5. PATH_EXISTS foo.py CONTRIBUTING.md:1180-1180
     tier: bare
     raw: file `foo.py`.
     cited by 10 claims
  6. PATH_EXISTS some_file.py README.md:298-298
     tier: bare
     raw: ruff check --config "lint.per-file-ignores = {'some_file.py' = ['F841']}"
     cited by 2 claims
  7. PATH_EXISTS readme.rst README.md:432-432
     tier: bare
     raw: ...or `README.rst`:
  8. PATH_EXISTS syntax-error.ipynb crates/ruff_linter/resources/mdtest/notebook/cell-boundaries.md:12-12
     tier: bare
     raw: `syntax-error.ipynb`:
  9. PATH_EXISTS no-code-cells.ipynb crates/ruff_linter/resources/mdtest/notebook/cell-boundaries.md:50-50
     tier: bare
     raw: `no-code-cells.ipynb`:
  10. PATH_EXISTS boundary-tokens.ipynb crates/ruff_linter/resources/mdtest/notebook/cell-boundaries.md:90-90
     tier: bare
     raw: `boundary-tokens.ipynb`:
  11. PATH_EXISTS panic.py crates/ruff_linter/resources/mdtest/test-rules/panicy-test-rule.md:11-11
     tier: bare
     raw: `panic.py`:
  12. PATH_EXISTS scratch.pyi crates/ruff_python_formatter/CONTRIBUTING.md:11-11
     tier: bare
     raw: `scratch.py` (or `scratch.pyi`) in the project root and run:
  13. PATH_EXISTS scratch.py crates/ruff_python_formatter/CONTRIBUTING.md:11-11
     tier: bare
     raw: `scratch.py` (or `scratch.pyi`) in the project root and run:
     cited by 5 claims
  14. PATH_EXISTS ty.toml crates/ty/docs/environment.md:7-7
     tier: bare
     raw: Path to a `ty.toml` configuration file to use.
     cited by 6 claims
  15. PATH_EXISTS foo.pyi crates/ty/docs/rules.md:473-473
     tier: bare
     raw: `foo.pyi`:
     cited by 5 claims
  16. PATH_EXISTS third_party_library.py crates/ty/docs/rules.md:931-931
     tier: bare
     raw: `third_party_library.py`:
     cited by 2 claims
  17. PATH_EXISTS first_party.py crates/ty/docs/rules.md:938-938
     tier: bare
     raw: `first_party.py`:
     cited by 2 claims
  18. PATH_EXISTS stubs.pyi crates/ty/docs/rules.md:4567-4567
     tier: bare
     raw: `stubs.pyi`:
     cited by 3 claims
  19. PATH_EXISTS with_def.pyi crates/ty/docs/rules.md:4593-4593
     tier: bare
     raw: `with_def.pyi`:
     cited by 2 claims
  20. PATH_EXISTS with_yield.pyi crates/ty/docs/rules.md:4603-4603
     tier: bare
     raw: `with_yield.pyi`:
     cited by 2 claims
  21. PATH_EXISTS x.py crates/ty/docs/tracing.md:73-73
     tier: bare
     raw: whether one if its children has the file `x.py`.
  22. PATH_EXISTS interface.pyi crates/ty_python_semantic/resources/mdtest/abstract.md:472-472
     tier: bare
     raw: `interface.pyi`:
  23. PATH_EXISTS mod.pyi crates/ty_python_semantic/resources/mdtest/annotations/deferred.md:5-5
     tier: bare
     raw: `mod.pyi`:
     cited by 3 claims
  24. PATH_EXISTS runtime.py crates/ty_python_semantic/resources/mdtest/annotations/invalid.md:211-211
     tier: bare
     raw: `runtime.py`:
     cited by 7 claims
  25. PATH_EXISTS __builtins__.pyi crates/ty_python_semantic/resources/mdtest/annotations/invalid.md:1295-1295
     tier: bare
     raw: A project-level `__builtins__.pyi` can replace `list` while leaving the standard `set` builtin
     cited by 5 claims
  26. PATH_EXISTS member.py crates/ty_python_semantic/resources/mdtest/annotations/invalid.md:1663-1663
     tier: bare
     raw: `member.py`:
  27. PATH_EXISTS mod.py crates/ty_python_semantic/resources/mdtest/annotations/literal.md:141-141
     tier: bare
     raw: `mod.py`:
     cited by 4 claims
  28. PATH_EXISTS other.pyi crates/ty_python_semantic/resources/mdtest/annotations/literal.md:318-318
     tier: bare
     raw: `other.pyi`:
  29. PATH_EXISTS first.py crates/ty_python_semantic/resources/mdtest/assignment/unsound.md:193-193
     tier: bare
     raw: `first.py`:
     cited by 4 claims
  30. PATH_EXISTS second.py crates/ty_python_semantic/resources/mdtest/assignment/unsound.md:199-199
     tier: bare
     raw: `second.py`:
     cited by 4 claims
  31. PATH_EXISTS callable.py crates/ty_python_semantic/resources/mdtest/async.md:321-321
     tier: bare
     raw: `callable.py`:
  32. PATH_EXISTS declarations-script.pyi crates/ty_python_semantic/resources/mdtest/async.md:389-389
     tier: bare
     raw: `declarations-script.pyi`:
  33. PATH_EXISTS override.py crates/ty_python_semantic/resources/mdtest/async.md:581-581
     tier: bare
     raw: `override.py`:
     cited by 2 claims
  34. PATH_EXISTS mod1.py crates/ty_python_semantic/resources/mdtest/attributes.md:4776-4776
     tier: bare
     raw: `mod1.py`:
     cited by 2 claims
  35. PATH_EXISTS mod2.py crates/ty_python_semantic/resources/mdtest/attributes.md:4782-4782
     tier: bare
     raw: `mod2.py`:
     cited by 2 claims
  36. PATH_EXISTS wrong.py crates/ty_python_semantic/resources/mdtest/attributes.md:5541-5541
     tier: bare
     raw: `wrong.py`:
  37. PATH_EXISTS foo_importer.py crates/ty_python_semantic/resources/mdtest/attributes.md:5577-5577
     tier: bare
     raw: `foo_importer.py`:
  38. PATH_EXISTS baz_importer.py crates/ty_python_semantic/resources/mdtest/attributes.md:5595-5595
     tier: bare
     raw: `baz_importer.py`:
  39. PATH_EXISTS typing.py crates/ty_python_semantic/resources/mdtest/call/builtins.md:609-609
     tier: bare
     raw: `typing.py`:
     cited by 5 claims
  40. PATH_EXISTS overloaded.pyi crates/ty_python_semantic/resources/mdtest/call/function.md:2320-2320
     tier: bare
     raw: `overloaded.pyi`:
     cited by 13 claims
  41. PATH_EXISTS module.pyi crates/ty_python_semantic/resources/mdtest/call/overloads.md:1900-1900
     tier: bare
     raw: `module.pyi`:
     cited by 5 claims
  42. PATH_EXISTS entry.py crates/ty_python_semantic/resources/mdtest/cycle/basic.md:588-588
     tier: bare
     raw: `entry.py`:
  43. PATH_EXISTS derived.py crates/ty_python_semantic/resources/mdtest/cycle/basic.md:598-598
     tier: bare
     raw: `derived.py`:
     cited by 3 claims
  44. PATH_EXISTS bases.py crates/ty_python_semantic/resources/mdtest/cycle/basic.md:623-623
     tier: bare
     raw: `bases.py`:
  45. PATH_EXISTS m.py crates/ty_python_semantic/resources/mdtest/cycle/basic.md:664-664
     tier: bare
     raw: `m.py`:
  46. PATH_EXISTS base.py crates/ty_python_semantic/resources/mdtest/cycle/implicit_instance_attributes.md:150-150
     tier: bare
     raw: `base.py`:
     cited by 5 claims
  47. PATH_EXISTS child.py crates/ty_python_semantic/resources/mdtest/cycle/implicit_instance_attributes.md:169-169
     tier: bare
     raw: `child.py`:
     cited by 3 claims
  48. PATH_EXISTS models.pyi crates/ty_python_semantic/resources/mdtest/dataclasses/dataclass_transform.md:1679-1679
     tier: bare
     raw: `models.pyi`:
  49. PATH_EXISTS typed-script.py crates/ty_python_semantic/resources/mdtest/decorators.md:1267-1267
     tier: bare
     raw: when the filename is not a valid Python module name. (`typed-script.py` cannot be resolved to a
     cited by 2 claims
  50. PATH_EXISTS package.py crates/ty_python_semantic/resources/mdtest/diagnostics/invalid_argument_type.md:58-58
     tier: bare
     raw: `package.py`:
  51. PATH_EXISTS lib.pyi crates/ty_python_semantic/resources/mdtest/diagnostics/invalid_match_pattern.md:290-290
     tier: bare
     raw: `lib.pyi`:
  52. PATH_EXISTS test.py crates/ty_python_semantic/resources/mdtest/diagnostics/same_names.md:7-7
     tier: bare
     raw: `test.py`:
     cited by 3 claims
  53. PATH_EXISTS package/foo.pyi crates/ty_python_semantic/resources/mdtest/diagnostics/same_names.md:186-186
     tier: unanchored
     raw: `package/foo.pyi`:
  54. PATH_EXISTS package/foo.py crates/ty_python_semantic/resources/mdtest/diagnostics/same_names.md:192-192
     tier: unanchored
     raw: `package/foo.py`:
     cited by 4 claims
  55. PATH_EXISTS status_a.py crates/ty_python_semantic/resources/mdtest/diagnostics/same_names.md:214-214
     tier: bare
     raw: `status_a.py`:
  56. PATH_EXISTS status_b.py crates/ty_python_semantic/resources/mdtest/diagnostics/same_names.md:224-224
     tier: bare
     raw: `status_b.py`:
  57. PATH_EXISTS cls_a.py crates/ty_python_semantic/resources/mdtest/diagnostics/same_names.md:265-265
     tier: bare
     raw: `cls_a.py`:
  58. PATH_EXISTS cls_b.py crates/ty_python_semantic/resources/mdtest/diagnostics/same_names.md:272-272
     tier: bare
     raw: `cls_b.py`:
  59. PATH_EXISTS generic_a.py crates/ty_python_semantic/resources/mdtest/diagnostics/same_names.md:289-289
     tier: bare
     raw: `generic_a.py`:
  60. PATH_EXISTS generic_b.py crates/ty_python_semantic/resources/mdtest/diagnostics/same_names.md:300-300
     tier: bare
     raw: `generic_b.py`:
  61. PATH_EXISTS bad.py crates/ty_python_semantic/resources/mdtest/diagnostics/same_names.md:315-315
     tier: bare
     raw: `bad.py`:
  62. PATH_EXISTS proto_a.py crates/ty_python_semantic/resources/mdtest/diagnostics/same_names.md:353-353
     tier: bare
     raw: `proto_a.py`:
  63. PATH_EXISTS proto_b.py crates/ty_python_semantic/resources/mdtest/diagnostics/same_names.md:362-362
     tier: bare
     raw: `proto_b.py`:
  64. PATH_EXISTS dict_a.py crates/ty_python_semantic/resources/mdtest/diagnostics/same_names.md:383-383
     tier: bare
     raw: `dict_a.py`:
  65. PATH_EXISTS dict_b.py crates/ty_python_semantic/resources/mdtest/diagnostics/same_names.md:392-392
     tier: bare
     raw: `dict_b.py`:
  66. PATH_EXISTS alias.py crates/ty_python_semantic/resources/mdtest/diagnostics/same_names.md:548-548
     tier: bare
     raw: `alias.py`:
     cited by 2 claims
  67. PATH_EXISTS package/subpackage/subsubpackage/__init__.py crates/ty_python_semantic/resources/mdtest/diagnostics/unresolved_import.md:33-33
     tier: unanchored
     raw: `package/subpackage/subsubpackage/__init__.py`:
  68. PATH_EXISTS stub2.pyi crates/ty_python_semantic/resources/mdtest/directives/cast.md:846-846
     tier: bare
     raw: `stub2.pyi`:
  69. PATH_EXISTS regular_py_file.py crates/ty_python_semantic/resources/mdtest/directives/cast.md:868-868
     tier: bare
     raw: `regular_py_file.py`:
  70. PATH_EXISTS tests/test_app.py crates/ty_python_semantic/resources/mdtest/directives/reveal_type.md:313-313
     tier: unanchored
     raw: `tests/test_app.py`:
     cited by 2 claims
  71. PATH_EXISTS typing_extensions.py crates/ty_python_semantic/resources/mdtest/directives/reveal_type.md:364-364
     tier: bare
     raw: `typing_extensions.py`:
  72. PATH_EXISTS module1.py crates/ty_python_semantic/resources/mdtest/final.md:154-154
     tier: bare
     raw: `module1.py`:
     cited by 2 claims
  73. PATH_EXISTS module2.py crates/ty_python_semantic/resources/mdtest/final.md:164-164
     tier: bare
     raw: `module2.py`:
     cited by 2 claims
  74. PATH_EXISTS library.pyi crates/ty_python_semantic/resources/mdtest/function/return_type_inference.md:872-872
     tier: bare
     raw: `library.pyi`:
  75. PATH_EXISTS base1.py crates/ty_python_semantic/resources/mdtest/generics/legacy/classes.md:575-575
     tier: bare
     raw: `base1.py`:
  76. PATH_EXISTS base2.py crates/ty_python_semantic/resources/mdtest/generics/legacy/classes.md:585-585
     tier: bare
     raw: `base2.py`:
  77. PATH_EXISTS library.py crates/ty_python_semantic/resources/mdtest/generics/legacy/classes.md:1118-1118
     tier: bare
     raw: `library.py`:
     cited by 3 claims
  78. PATH_EXISTS valid.py crates/ty_python_semantic/resources/mdtest/generics/legacy/functions.md:1462-1462
     tier: bare
     raw: `valid.py`:
     cited by 2 claims
  79. PATH_EXISTS invalid.py crates/ty_python_semantic/resources/mdtest/generics/legacy/functions.md:1475-1475
     tier: bare
     raw: `invalid.py`:
     cited by 2 claims
  80. PATH_EXISTS excluded.py crates/ty_python_semantic/resources/mdtest/generics/legacy/variables.md:186-186
     tier: bare
     raw: `excluded.py`:
  81. PATH_EXISTS included.py crates/ty_python_semantic/resources/mdtest/generics/legacy/variables.md:197-197
     tier: bare
     raw: `included.py`:
  82. PATH_EXISTS mapping.pyi crates/ty_python_semantic/resources/mdtest/generics/legacy/variance.md:486-486
     tier: bare
     raw: `mapping.pyi`:
  83. PATH_EXISTS functions.pyi crates/ty_python_semantic/resources/mdtest/generics/pep695/functions.md:2953-2953
     tier: bare
     raw: `functions.pyi`:
  84. PATH_EXISTS covariant.py crates/ty_python_semantic/resources/mdtest/generics/pep695/functions.md:3009-3009
     tier: bare
     raw: `covariant.py`:
  85. PATH_EXISTS contravariant.py crates/ty_python_semantic/resources/mdtest/generics/pep695/functions.md:3020-3020
     tier: bare
     raw: `contravariant.py`:
  86. PATH_EXISTS invariant.py crates/ty_python_semantic/resources/mdtest/generics/pep695/functions.md:3033-3033
     tier: bare
     raw: `invariant.py`:
  87. PATH_EXISTS box.pyi crates/ty_python_semantic/resources/mdtest/generics/pep695/variance.md:796-796
     tier: bare
     raw: `box.pyi`:
  88. PATH_EXISTS pep695.py crates/ty_python_semantic/resources/mdtest/generics/scoping.md:351-351
     tier: bare
     raw: `pep695.py`:
  89. PATH_EXISTS quux.py crates/ty_python_semantic/resources/mdtest/ide_support/all_members.md:641-641
     tier: bare
     raw: `quux.py`:
  90. PATH_EXISTS play.py crates/ty_python_semantic/resources/mdtest/ide_support/all_members.md:671-671
     tier: bare
     raw: `play.py`:
  91. PATH_EXISTS regular_module.py crates/ty_python_semantic/resources/mdtest/ide_support/all_members.md:1124-1124
     tier: bare
     raw: `regular_module.py`:
  92. PATH_EXISTS bar.pyi crates/ty_python_semantic/resources/mdtest/implicit_type_aliases.md:379-379
     tier: bare
     raw: `bar.pyi`:
     cited by 2 claims
  93. PATH_EXISTS left.py crates/ty_python_semantic/resources/mdtest/implicit_type_aliases.md:2145-2145
     tier: bare
     raw: `left.py`:
  94. PATH_EXISTS right.py crates/ty_python_semantic/resources/mdtest/implicit_type_aliases.md:2153-2153
     tier: bare
     raw: `right.py`:
  95. PATH_EXISTS classes.py crates/ty_python_semantic/resources/mdtest/implicit_type_aliases.md:2161-2161
     tier: bare
     raw: `classes.py`:
  96. PATH_EXISTS modern.py crates/ty_python_semantic/resources/mdtest/implicit_type_aliases.md:2167-2167
     tier: bare
     raw: `modern.py`:
  97. PATH_EXISTS aliases.py crates/ty_python_semantic/resources/mdtest/implicit_type_aliases.md:2200-2200
     tier: bare
     raw: `aliases.py`:
  98. PATH_EXISTS forward.py crates/ty_python_semantic/resources/mdtest/implicit_type_aliases.md:2210-2210
     tier: bare
     raw: `forward.py`:
  99. PATH_EXISTS tree.py crates/ty_python_semantic/resources/mdtest/implicit_type_aliases.md:3130-3130
     tier: bare
     raw: `tree.py`:
  100. PATH_EXISTS pkg/a.py crates/ty_python_semantic/resources/mdtest/import/allowed_unresolved_imports.md:241-241
     tier: unanchored
     raw: `pkg/a.py`:
  101. PATH_EXISTS values.py crates/ty_python_semantic/resources/mdtest/import/basic.md:45-45
     tier: bare
     raw: `values.py`:
     cited by 2 claims
  102. PATH_EXISTS db/__init__.py crates/ty_python_semantic/resources/mdtest/import/case_sensitive.md:78-78
     tier: unanchored
     raw: `db/__init__.py`:
  103. PATH_EXISTS db/a.py crates/ty_python_semantic/resources/mdtest/import/case_sensitive.md:83-83
     tier: unanchored
     raw: `db/a.py`:
  104. PATH_EXISTS correctly_cased.py crates/ty_python_semantic/resources/mdtest/import/case_sensitive.md:90-90
     tier: bare
     raw: `correctly_cased.py`:
  105. PATH_EXISTS incorrectly_cased.py crates/ty_python_semantic/resources/mdtest/import/case_sensitive.md:100-100
     tier: bare
     raw: `incorrectly_cased.py`:
  106. PATH_EXISTS maybe_unbound.py crates/ty_python_semantic/resources/mdtest/import/conditional.md:5-5
     tier: bare
     raw: `maybe_unbound.py`:
  107. PATH_EXISTS maybe_unbound_annotated.py crates/ty_python_semantic/resources/mdtest/import/conditional.md:34-34
     tier: bare
     raw: `maybe_unbound_annotated.py`:
  108. PATH_EXISTS maybe_undeclared.py crates/ty_python_semantic/resources/mdtest/import/conditional.md:67-67
     tier: bare
     raw: `maybe_undeclared.py`:
  109. PATH_EXISTS c.pyi crates/ty_python_semantic/resources/mdtest/import/conditional.md:115-115
     tier: bare
     raw: `c.pyi`:
     cited by 3 claims
  110. PATH_EXISTS builtins.pyi crates/ty_python_semantic/resources/mdtest/import/conventions.md:12-12
     tier: bare
     raw: the global scope. The `builtins.pyi` file, that will be used to resolve any symbol in the builtins
     evidence: file:crates/ty_vendored/vendor/typeshed/stdlib/builtins.pyi
  111. PATH_EXISTS b.pyi crates/ty_python_semantic/resources/mdtest/import/conventions.md:61-61
     tier: bare
     raw: `b.pyi`:
     cited by 8 claims
  112. PATH_EXISTS a.pyi crates/ty_python_semantic/resources/mdtest/import/conventions.md:112-112
     tier: bare
     raw: `a.pyi`:
     cited by 2 claims
  113. PATH_EXISTS named_import.py crates/ty_python_semantic/resources/mdtest/import/conventions.md:229-229
     tier: bare
     raw: `named_import.py`:
  114. PATH_EXISTS star_import.py crates/ty_python_semantic/resources/mdtest/import/conventions.md:253-253
     tier: bare
     raw: `star_import.py`:
  115. PATH_EXISTS pkg/outer.py crates/ty_python_semantic/resources/mdtest/import/cyclic.md:44-44
     tier: unanchored
     raw: `pkg/outer.py`:
  116. PATH_EXISTS pkg/sub/__init__.py crates/ty_python_semantic/resources/mdtest/import/cyclic.md:50-50
     tier: unanchored
     raw: `pkg/sub/__init__.py`:
  117. PATH_EXISTS pkg/sub/inner.py crates/ty_python_semantic/resources/mdtest/import/cyclic.md:57-57
     tier: unanchored
     raw: `pkg/sub/inner.py`:
  118. PATH_EXISTS module/sub.py crates/ty_python_semantic/resources/mdtest/import/cyclic.md:115-115
     tier: unanchored
     raw: `module/sub.py`:
  119. PATH_EXISTS reexport.py crates/ty_python_semantic/resources/mdtest/import/cyclic.md:148-148
     tier: bare
     raw: `reexport.py`:
  120. PATH_EXISTS exporter.py crates/ty_python_semantic/resources/mdtest/import/dunder_all.md:12-12
     tier: bare
     raw: `exporter.py`:
     cited by 7 claims
  121. PATH_EXISTS importer.py crates/ty_python_semantic/resources/mdtest/import/dunder_all.md:19-19
     tier: bare
     raw: `importer.py`:
     cited by 6 claims
  122. PATH_EXISTS exporter_annotated.py crates/ty_python_semantic/resources/mdtest/import/dunder_all.md:77-77
     tier: bare
     raw: `exporter_annotated.py`:
  123. PATH_EXISTS subexporter.py crates/ty_python_semantic/resources/mdtest/import/dunder_all.md:222-222
     tier: bare
     raw: `subexporter.py`:
  124. PATH_EXISTS exporter1.py crates/ty_python_semantic/resources/mdtest/import/dunder_all.md:510-510
     tier: bare
     raw: `exporter1.py`:
  125. PATH_EXISTS star.py crates/ty_python_semantic/resources/mdtest/import/missing_direct_dependency.md:111-111
     tier: bare
     raw: `star.py`:
  126. PATH_EXISTS class_first.py crates/ty_python_semantic/resources/mdtest/import/missing_direct_dependency.md:324-324
     tier: bare
     raw: `class_first.py`:
  127. PATH_EXISTS indirect.py crates/ty_python_semantic/resources/mdtest/import/missing_direct_dependency.md:407-407
     tier: bare
     raw: `indirect.py`:
  128. PATH_EXISTS attributes.py crates/ty_python_semantic/resources/mdtest/import/missing_direct_dependency.md:808-808
     tier: bare
     raw: `attributes.py`:
  129. PATH_EXISTS module_with_getattr.py crates/ty_python_semantic/resources/mdtest/import/module_getattr.md:12-12
     tier: bare
     raw: `module_with_getattr.py`:
  130. PATH_EXISTS invalid_getattr_module.py crates/ty_python_semantic/resources/mdtest/import/module_getattr.md:49-49
     tier: bare
     raw: `invalid_getattr_module.py`:
  131. PATH_EXISTS invalid_getattr_name.py crates/ty_python_semantic/resources/mdtest/import/module_getattr.md:69-69
     tier: bare
     raw: `invalid_getattr_name.py`:
  132. PATH_EXISTS mixed_module.py crates/ty_python_semantic/resources/mdtest/import/module_getattr.md:140-140
     tier: bare
     raw: `mixed_module.py`:
  133. PATH_EXISTS test_import_mod.py crates/ty_python_semantic/resources/mdtest/import/module_getattr.md:170-170
     tier: bare
     raw: `test_import_mod.py`:
  134. PATH_EXISTS test_import_mod_sub.py crates/ty_python_semantic/resources/mdtest/import/module_getattr.md:181-181
     tier: bare
     raw: `test_import_mod_sub.py`:
  135. PATH_EXISTS test_from_import.py crates/ty_python_semantic/resources/mdtest/import/module_getattr.md:196-196
     tier: bare
     raw: `test_from_import.py`:
  136. PATH_EXISTS limited_getattr_module.py crates/ty_python_semantic/resources/mdtest/import/module_getattr.md:248-248
     tier: bare
     raw: `limited_getattr_module.py`:
  137. PATH_EXISTS from.py crates/ty_python_semantic/resources/mdtest/import/namespace.md:29-29
     tier: bare
     raw: `from.py`
  138. PATH_EXISTS package/bar.py crates/ty_python_semantic/resources/mdtest/import/relative.md:10-10
     tier: unanchored
     raw: `package/bar.py`:
  139. PATH_EXISTS package/bar.pyi crates/ty_python_semantic/resources/mdtest/import/relative.md:63-63
     tier: unanchored
     raw: `package/bar.pyi`:
  140. PATH_EXISTS package/subpackage/subsubpackage/bar.py crates/ty_python_semantic/resources/mdtest/import/relative.md:157-157
     tier: unanchored
     raw: `package/subpackage/subsubpackage/bar.py`:
  141. PATH_EXISTS parser.py crates/ty_python_semantic/resources/mdtest/import/relative.md:260-260
     tier: bare
     raw: `parser.py`:
  142. PATH_EXISTS pkg/sub.py crates/ty_python_semantic/resources/mdtest/import/replace_imports_with_any.md:40-40
     tier: unanchored
     raw: `pkg/sub.py`:
  143. PATH_EXISTS pkg/keep.py crates/ty_python_semantic/resources/mdtest/import/replace_imports_with_any.md:87-87
     tier: unanchored
     raw: `pkg/keep.py`:
  144. PATH_EXISTS package/main.py crates/ty_python_semantic/resources/mdtest/import/replace_imports_with_any.md:124-124
     tier: unanchored
     raw: `package/main.py`:
  145. PATH_EXISTS real_module.py crates/ty_python_semantic/resources/mdtest/import/replace_imports_with_any.md:142-142
     tier: bare
     raw: `real_module.py`:
  146. PATH_EXISTS pyvenv.cfg crates/ty_python_semantic/resources/mdtest/import/site_packages_discovery.md:5-5
     tier: bare
     raw: The `version`/`version_info` key in a `pyvenv.cfg` file is provided by most virtual-environment
     cited by 6 claims
  147. PATH_EXISTS common.py crates/ty_python_semantic/resources/mdtest/import/star.md:1517-1517
     tier: bare
     raw: `common.py`:
  148. PATH_EXISTS q.py crates/ty_python_semantic/resources/mdtest/import/tracking.md:73-73
     tier: bare
     raw: `q.py`:
  149. PATH_EXISTS a.b.c crates/ty_python_semantic/resources/mdtest/import/workspaces.md:35-35
     tier: bare
     raw: Convert the relative module name `.c` to an absolute one `a.b.c`
     cited by 3 claims
  150. PATH_EXISTS ..c crates/ty_python_semantic/resources/mdtest/import/workspaces.md:51-51
     tier: bare
     raw: (`..c` resolves in `a.b` but not `b`).
  151. PATH_EXISTS my-proj.a.b.c crates/ty_python_semantic/resources/mdtest/import/workspaces.md:53-53
     tier: bare
     raw: and reject the import (`my-proj.a.b.c` is not a valid module name).
  152. PATH_EXISTS tests/my-mod.py crates/ty_python_semantic/resources/mdtest/import/workspaces.md:108-108
     tier: unanchored
     raw: `tests/my-mod.py`:
  153. PATH_EXISTS tests/mod1.py crates/ty_python_semantic/resources/mdtest/import/workspaces.md:125-125
     tier: unanchored
     raw: `tests/mod1.py`:
  154. PATH_EXISTS tests/mod2.py crates/ty_python_semantic/resources/mdtest/import/workspaces.md:131-131
     tier: unanchored
     raw: `tests/mod2.py`:
  155. PATH_EXISTS mod3.py crates/ty_python_semantic/resources/mdtest/import/workspaces.md:137-137
     tier: bare
     raw: `mod3.py`:
  156. PATH_EXISTS constants.py crates/ty_python_semantic/resources/mdtest/known_constants.md:101-101
     tier: bare
     raw: `constants.py`:
     cited by 2 claims
  157. PATH_EXISTS mini_numpy.py crates/ty_python_semantic/resources/mdtest/libraries/numpy.md:14-14
     tier: bare
     raw: `mini_numpy.py`:
  158. PATH_EXISTS left.pyi crates/ty_python_semantic/resources/mdtest/liskov.md:1326-1326
     tier: bare
     raw: `left.pyi`:
  159. PATH_EXISTS right.pyi crates/ty_python_semantic/resources/mdtest/liskov.md:1333-1333
     tier: bare
     raw: `right.pyi`:
  160. PATH_EXISTS other_stub.pyi crates/ty_python_semantic/resources/mdtest/liskov.md:1534-1534
     tier: bare
     raw: `other_stub.pyi`:
  161. PATH_EXISTS object.pyi crates/ty_python_semantic/resources/mdtest/liskov.md:1580-1580
     tier: bare
     raw: `object.pyi`:
  162. PATH_EXISTS one.pyi crates/ty_python_semantic/resources/mdtest/liskov.md:2107-2107
     tier: bare
     raw: `one.pyi`:
  163. PATH_EXISTS two.pyi crates/ty_python_semantic/resources/mdtest/liskov.md:2114-2114
     tier: bare
     raw: `two.pyi`:
  164. PATH_EXISTS class/constructor.md crates/ty_python_semantic/resources/mdtest/metaclass.md:6-6
     tier: unanchored
     raw: `class/constructor.md`). But if the metaclass `__call__` returns a non-instance type, then `__new__`
  165. PATH_EXISTS records.pyi crates/ty_python_semantic/resources/mdtest/named_tuple.md:140-140
     tier: bare
     raw: `records.pyi`:
  166. PATH_EXISTS typing_compat.py crates/ty_python_semantic/resources/mdtest/narrow/callable.md:229-229
     tier: bare
     raw: `typing_compat.py`:
  167. PATH_EXISTS collections_abc_compat.py crates/ty_python_semantic/resources/mdtest/narrow/callable.md:235-235
     tier: bare
     raw: `collections_abc_compat.py`:
  168. PATH_EXISTS widget.pyi crates/ty_python_semantic/resources/mdtest/overloads.md:1578-1578
     tier: bare
     raw: `widget.pyi`:
  169. PATH_EXISTS factory.pyi crates/ty_python_semantic/resources/mdtest/overloads.md:1723-1723
     tier: bare
     raw: `factory.pyi`:
  170. PATH_EXISTS base_property.py crates/ty_python_semantic/resources/mdtest/override.md:845-845
     tier: bare
     raw: `base_property.py`:
  171. PATH_EXISTS property_setter.py crates/ty_python_semantic/resources/mdtest/override.md:923-923
     tier: bare
     raw: `property_setter.py`:
  172. PATH_EXISTS classvars.py crates/ty_python_semantic/resources/mdtest/protocols.md:2303-2303
     tier: bare
     raw: `classvars.py`:
  173. PATH_EXISTS factory.py crates/ty_python_semantic/resources/mdtest/protocols.md:4980-4980
     tier: bare
     raw: `factory.py`:
  174. PATH_EXISTS attribute_aliases.py crates/ty_python_semantic/resources/mdtest/redundant_condition.md:5285-5285
     tier: bare
     raw: `attribute_aliases.py`:
  175. PATH_EXISTS assignment_forms.py crates/ty_python_semantic/resources/mdtest/redundant_condition.md:5324-5324
     tier: bare
     raw: `assignment_forms.py`:
  176. PATH_EXISTS cyclic_aliases.py crates/ty_python_semantic/resources/mdtest/redundant_condition.md:5379-5379
     tier: bare
     raw: `cyclic_aliases.py`:
  177. PATH_EXISTS pkg/config.py crates/ty_python_semantic/resources/mdtest/regression/3208_recursive_protocol_signature.md:13-13
     tier: unanchored
     raw: `pkg/config.py`:
  178. PATH_EXISTS pkg/wrapper.py crates/ty_python_semantic/resources/mdtest/regression/3208_recursive_protocol_signature.md:35-35
     tier: unanchored
     raw: `pkg/wrapper.py`:
  179. PATH_EXISTS cog.py crates/ty_python_semantic/resources/mdtest/regression/3804_bound_typevar_default_cycle.md:5-5
     tier: bare
     raw: `cog.py`:
  180. PATH_EXISTS lazy.py crates/ty_python_semantic/resources/mdtest/regression/3954_recursive_protocol_structural_relation.md:16-16
     tier: bare
     raw: `lazy.py`:
  181. PATH_EXISTS structural.py crates/ty_python_semantic/resources/mdtest/regression/3954_recursive_protocol_structural_relation.md:36-36
     tier: bare
     raw: `structural.py`:
  182. PATH_EXISTS evaluated_later.py crates/ty_python_semantic/resources/mdtest/scopes/eager.md:208-208
     tier: bare
     raw: `evaluated_later.py`:
  183. PATH_EXISTS iterable_evaluated_eagerly.py crates/ty_python_semantic/resources/mdtest/scopes/eager.md:223-223
     tier: bare
     raw: `iterable_evaluated_eagerly.py`:
  184. PATH_EXISTS global1.py crates/ty_python_semantic/resources/mdtest/scopes/global.md:459-459
     tier: bare
     raw: `global1.py`:
  185. PATH_EXISTS global2.py crates/ty_python_semantic/resources/mdtest/scopes/global.md:485-485
     tier: bare
     raw: `global2.py`:
  186. PATH_EXISTS global3.py crates/ty_python_semantic/resources/mdtest/scopes/global.md:518-518
     tier: bare
     raw: `global3.py`:
  187. PATH_EXISTS items.py crates/ty_python_semantic/resources/mdtest/suspicious_conditions.md:972-972
     tier: bare
     raw: `items.py`:
  188. PATH_EXISTS package/sys.py crates/ty_python_semantic/resources/mdtest/sys_version_info.md:94-94
     tier: unanchored
     raw: `package/sys.py`:
  189. PATH_EXISTS package/script.py crates/ty_python_semantic/resources/mdtest/sys_version_info.md:100-100
     tier: unanchored
     raw: `package/script.py`:
  190. PATH_EXISTS main2.py crates/ty_python_semantic/resources/mdtest/type_properties/is_equivalent_to.md:796-796
     tier: bare
     raw: `main2.py`:
  191. PATH_EXISTS many_overloads.pyi crates/ty_python_semantic/resources/mdtest/type_properties/is_subtype_of.md:2843-2843
     tier: bare
     raw: `many_overloads.pyi`:
  192. PATH_EXISTS forwarded.py crates/ty_python_semantic/resources/mdtest/type_qualifiers/final.md:220-220
     tier: bare
     raw: `forwarded.py`:
  193. PATH_EXISTS wildcard.py crates/ty_python_semantic/resources/mdtest/type_qualifiers/final.md:226-226
     tier: bare
     raw: `wildcard.py`:
  194. PATH_EXISTS constant.py crates/ty_python_semantic/resources/mdtest/type_qualifiers/final.md:369-369
     tier: bare
     raw: `constant.py`:
  195. PATH_EXISTS mutable.py crates/ty_python_semantic/resources/mdtest/type_qualifiers/final.md:377-377
     tier: bare
     raw: `mutable.py`:
  196. PATH_EXISTS mutable_first.py crates/ty_python_semantic/resources/mdtest/type_qualifiers/final.md:443-443
     tier: bare
     raw: `mutable_first.py`:
  197. PATH_EXISTS source.pyi crates/ty_python_semantic/resources/mdtest/type_qualifiers/final.md:496-496
     tier: bare
     raw: `source.pyi`:
  198. PATH_EXISTS forwarded.pyi crates/ty_python_semantic/resources/mdtest/type_qualifiers/final.md:504-504
     tier: bare
     raw: `forwarded.pyi`:
  199. PATH_EXISTS module_a.py crates/ty_python_semantic/resources/mdtest/type_qualifiers/final.md:1142-1142
     tier: bare
     raw: `module_a.py`:
  200. PATH_EXISTS module_b.py crates/ty_python_semantic/resources/mdtest/type_qualifiers/final.md:1151-1151
     tier: bare
     raw: `module_b.py`:
  201. PATH_EXISTS test_del.py crates/ty_python_semantic/resources/mdtest/type_qualifiers/final.md:1577-1577
     tier: bare
     raw: `test_del.py`:
  202. PATH_EXISTS mdtest_snippet.py crates/ty_test/README.md:688-688
     tier: bare
     raw: diagnostic assertions for `mdtest_snippet.py` would require specifying new contents for
     cited by 3 claims
  203. PATH_EXISTS crates/ty_vendored/vendor/typeshed/contributing.md crates/ty_vendored/vendor/typeshed/README.md:17-17
     tier: anchored
     raw: contributors can be found in [CONTRIBUTING.md](CONTRIBUTING.md).  **Please read
  204. PATH_EXISTS docs/default-rules.md docs/configuration.md:10-10
     tier: anchored
     raw: For the complete list of enabled rules, see [_Default Rules_](default-rules.md).
     cited by 2 claims
  205. PATH_EXISTS docs/settings.md docs/configuration.md:308-308
     tier: anchored
     raw: When no discovered configuration specifies a [`target-version`](settings.md#target-version), Ruff will attempt to fall back to the minimum version com
     cited by 48 claims
  206. PATH_EXISTS docs/rules/module-import-not-at-top-of-file.md docs/configuration.md:450-450
     tier: anchored
     raw: [`module-import-not-at-top-of-file` (`E402`)](rules/module-import-not-at-top-of-file.md)
  207. SYMBOL_EXISTS ruff.importstrategy docs/editors/settings.md:1078-1078
     tier: -
     raw: [`ruff.importStrategy`](#importstrategy) is set to `fromEnvironment`.
     cited by 2 claims
  208. PATH_EXISTS languages.toml docs/editors/setup.md:296-296
     tier: bare
     raw: language server registered to use with Python, add this to `languages.toml`:
  209. PATH_EXISTS docs/rules/line-too-long.md docs/faq.md:14-14
     tier: anchored
     raw: within comments). Ruff's [`line-too-long`](rules/line-too-long.md) (`E501`) rule checks lines against
     cited by 4 claims
  210. PATH_EXISTS docs/rules/too-many-branches.md docs/faq.md:129-129
     tier: anchored
     raw: example, Ruff's [`too-many-branches`](rules/too-many-branches.md) does not count `try` blocks as
  211. PATH_EXISTS docs/rules/magic-value-comparison.md docs/faq.md:131-131
     tier: anchored
     raw: rules from Pylint _extensions_ (like [`magic-value-comparison`](rules/magic-value-comparison.md)),
  212. PATH_EXISTS docs/contributing.md docs/faq.md:393-393
     tier: anchored
     raw: For a detailed explanation of `src` resolution, see the [contributing guide](contributing.md).
  213. PATH_EXISTS docs/rules/tab-indentation.md docs/formatter.md:426-426
     tier: anchored
     raw: [`tab-indentation`](rules/tab-indentation.md) (`W191`)
  214. PATH_EXISTS docs/rules/indentation-with-invalid-multiple.md docs/formatter.md:427-427
     tier: anchored
     raw: [`indentation-with-invalid-multiple`](rules/indentation-with-invalid-multiple.md) (`E111`)
  215. PATH_EXISTS docs/rules/indentation-with-invalid-multiple-comment.md docs/formatter.md:428-428
     tier: anchored
     raw: [`indentation-with-invalid-multiple-comment`](rules/indentation-with-invalid-multiple-comment.md) (`E114`)
  216. PATH_EXISTS docs/rules/over-indented.md docs/formatter.md:429-429
     tier: anchored
     raw: [`over-indented`](rules/over-indented.md) (`E117`)
  217. PATH_EXISTS docs/rules/incorrect-blank-line-before-class.md docs/formatter.md:430-430
     tier: anchored
     raw: [`incorrect-blank-line-before-class`](rules/incorrect-blank-line-before-class.md) (`D203`)
  218. PATH_EXISTS docs/rules/docstring-tab-indentation.md docs/formatter.md:431-431
     tier: anchored
     raw: [`docstring-tab-indentation`](rules/docstring-tab-indentation.md) (`D206`)
  219. PATH_EXISTS docs/rules/triple-single-quotes.md docs/formatter.md:432-432
     tier: anchored
     raw: [`triple-single-quotes`](rules/triple-single-quotes.md) (`D300`)
  220. PATH_EXISTS docs/rules/bad-quotes-inline-string.md docs/formatter.md:433-433
     tier: anchored
     raw: [`bad-quotes-inline-string`](rules/bad-quotes-inline-string.md) (`Q000`)
  221. PATH_EXISTS docs/rules/bad-quotes-multiline-string.md docs/formatter.md:434-434
     tier: anchored
     raw: [`bad-quotes-multiline-string`](rules/bad-quotes-multiline-string.md) (`Q001`)
  222. PATH_EXISTS docs/rules/bad-quotes-docstring.md docs/formatter.md:435-435
     tier: anchored
     raw: [`bad-quotes-docstring`](rules/bad-quotes-docstring.md) (`Q002`)
  223. PATH_EXISTS docs/rules/avoidable-escaped-quote.md docs/formatter.md:436-436
     tier: anchored
     raw: [`avoidable-escaped-quote`](rules/avoidable-escaped-quote.md) (`Q003`)
  224. PATH_EXISTS docs/rules/unnecessary-escaped-quote.md docs/formatter.md:437-437
     tier: anchored
     raw: [`unnecessary-escaped-quote`](rules/unnecessary-escaped-quote.md) (`Q004`)
  225. PATH_EXISTS docs/rules/missing-trailing-comma.md docs/formatter.md:438-438
     tier: anchored
     raw: [`missing-trailing-comma`](rules/missing-trailing-comma.md) (`COM812`)
  226. PATH_EXISTS docs/rules/prohibited-trailing-comma.md docs/formatter.md:439-439
     tier: anchored
     raw: [`prohibited-trailing-comma`](rules/prohibited-trailing-comma.md) (`COM819`)
  227. PATH_EXISTS docs/rules/multi-line-implicit-string-concatenation.md docs/formatter.md:440-440
     tier: anchored
     raw: [`multi-line-implicit-string-concatenation`](rules/multi-line-implicit-string-concatenation.md) (`ISC002`) if used without `ISC001` and `flake8-implic
  228. DEPENDENCY black docs/formatter/black.md:133-133
     tier: -
     raw: We agree that Ruff's formatting (that matches Black's 23) is hard to read and needs improvement.
     evidence: black:pyproject.toml:>=26.10.0
  229. DEPENDENCY black docs/formatter/black.md:187-187
     tier: -
     raw: Black 24 and newer allows blank lines at the start of a block, where Ruff always removes them:
     evidence: black:pyproject.toml:>=26.10.0
     cited by 2 claims
  230. PATH_EXISTS docs/rules/unused-import.md docs/linter.md:423-423
     tier: anchored
     raw: [`unused-imports`](rules/unused-import.md) (`F401`):
  231. PATH_EXISTS src/numbers/__init__.py docs/tutorial.md:32-32
     tier: unanchored
     raw: We'll then clear out the auto-generated content in `src/numbers/__init__.py`
  232. PATH_EXISTS src/numbers/calculate.py docs/tutorial.md:33-33
     tier: unanchored
     raw: and create `src/numbers/calculate.py` with the following code:

