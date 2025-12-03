Integrations Reference
======================

Reference for Hypothesis features with a defined interface, but no code API.

Ghostwriter
-----------

Writing tests with Hypothesis frees you from the tedium of deciding on and writing out specific inputs to test. Now, the `hypothesis.extra.ghostwriter` module can write your test functions for you too!

The idea is to provide an easy way to start property-based testing, and a seamless transition to more complex test code—because ghostwritten tests are source code that you could have written for yourself.

So just pick a function you’d like tested, and feed it to one of the functions below. They follow imports, use but do not require type annotations, and generally do their best to write you a useful test. You can also use our command-line interface:

```console
$ hypothesis write --help
Usage: hypothesis write [OPTIONS] FUNC...

`hypothesis write` writes property-based tests for you!

Type annotations are helpful but not required for our advanced introspection and templating logic. Try running the examples below to see how it works:

hypothesis write gzip
hypothesis write numpy.matmul
hypothesis write pandas.from_dummies
hypothesis write re.compile --except re.error
hypothesis write --equivalent ast.literal_eval eval
hypothesis write --roundtrip json.dumps json.loads
hypothesis write --style=unittest --idempotent sorted
hypothesis write --binary-op operator.add

Options:
  --roundtrip              start by testing write/read or encode/decode!
  --equivalent             very useful when optimising or refactoring code
  --errors-equivalent      --equivalent, but also allows consistent errors
  --idempotent             check that f(x) == f(f(x))
  --binary-op              associativity, commutativity, identity element
  --style [pytest|unittest] pytest-style function, or unittest-style method?
  -e, --except OBJ_NAME    dotted name of exception(s) to ignore
  --annotate / --no-annotate force ghostwritten tests to be type-annotated (or not). By default, match the code to test.
  -h, --help               Show this message and exit.
```

> **Tip**  
> Using a light theme? Hypothesis respects `NO_COLOR` and `DJANGO_COLORS=light`.

> **Note**  
> The ghostwriter requires `black`, but the generated code only requires Hypothesis itself.

> **Note**  
> Legal questions? While the ghostwriter fragments and logic is under the MPL-2.0 license like the rest of Hypothesis, the output from the ghostwriter is made available under the Creative Commons Zero (CC0) public domain dedication, so you can use it without any restrictions.

- `hypothesis.extra.ghostwriter.magic(*modules_or_functions, except_=(), style='pytest', annotate=None)`

  Guess which ghostwriters to use, for a module or collection of functions.

  As for all ghostwriters, the `except_` argument should be an `Exception` or tuple of exceptions, and `style` may be either `"pytest"` to write test functions or `"unittest"` to write test methods and `TestCase`.

  After finding the public functions attached to any modules, the `magic` ghostwriter looks for pairs of functions to pass to `roundtrip()`, then checks for `binary_operation()` and `ufunc()` functions, and any others are passed to `fuzz()`.

  For example, try `hypothesis write gzip` on the command line!

- `hypothesis.extra.ghostwriter.fuzz(func, *, except_=(), style='pytest', annotate=None)[source]`

  Write source code for a property-based test of `func`.

  The resulting test checks that valid input only leads to expected exceptions. For example:

  ```python
  from re import compile, error
  from hypothesis.extra import ghostwriter
  ghostwriter.fuzz(compile, except_=error)
  ```

  Gives:

  ```python
  # This test code was written by the `hypothesis.extra.ghostwriter` module
  # and is provided under the Creative Commons Zero public domain dedication.

  import re
  from hypothesis import given, reject, strategies as st

  # TODO: replace st.nothing() with an appropriate strategy
  @given(pattern=st.nothing(), flags=st.just(0))
  def test_fuzz_compile(pattern, flags):
      try:
          re.compile(pattern=pattern, flags=flags)
      except re.error:
          reject()
  ```

  Note that it includes all the required imports. Because the `pattern` parameter doesn’t have annotations or a default argument, you’ll need to specify a strategy—for example `text()` or `binary()`. After that, you have a test!

- `hypothesis.extra.ghostwriter.idempotent(func, *, except_=(), style='pytest', annotate=None)`

  Write source code for a property-based test of `func`.

  The resulting test checks that if you call `func` on its own output, the result does not change. For example:

  ```python
  from typing import Sequence
  from hypothesis.extra import ghostwriter

  def timsort(seq: Sequence[int]) -> Sequence[int]:
      return sorted(seq)

  ghostwriter.idempotent(timsort)
  ```

  Gives:

  ```python
  # This test code was written by the `hypothesis.extra.ghostwriter` module
  # and is provided under the Creative Commons Zero public domain dedication.

  from hypothesis import given, strategies as st

  @given(seq=st.one_of(st.binary(), st.binary().map(bytearray), st.lists(st.integers())))
  def test_idempotent_timsort(seq):
      result = timsort(seq=seq)
      repeat = timsort(seq=result)
      assert result == repeat, (result, repeat)
  ```

- `hypothesis.extra.ghostwriter.roundtrip(*funcs, except_=(), style='pytest', annotate=None)[source]`

  Write source code for a property-based test of `funcs`.

  The resulting test checks that if you call the first function, pass the result to the second (and so on), the final result is equal to the first input argument.

  This is a very powerful property to test, especially when the config options are varied along with the object to round-trip. For example, try ghostwriting a test for `json.dumps()`—would you have thought of all that?

  ```console
  hypothesis write --roundtrip json.dumps json.loads
  ```

- `hypothesis.extra.ghostwriter.equivalent(*funcs, allow_same_errors=False, except_=(), style='pytest', annotate=None)`

  Write source code for a property-based test of `funcs`.

  The resulting test checks that calling each of the functions returns an equal value. This can be used as a classic ‘oracle’, such as testing a fast sorting algorithm against the `sorted()` builtin, or for differential testing where none of the compared functions are fully trusted but any difference indicates a bug (e.g. running a function on different numbers of threads, or simply multiple times).

  The functions should have reasonably similar signatures, as only the common parameters will be passed the same arguments—any other parameters will be allowed to vary.

  If `allow_same_errors` is True, then the test will pass if calling each of the functions returns an equal value, or if the first function raises an exception and each of the others raises an exception of the same type. This relaxed mode can be useful for code synthesis projects.

- `hypothesis.extra.ghostwriter.binary_operation(func, *, associative=True, commutative=True, identity=Ellipsis, distributes_over=None, except_=(), style='pytest', annotate=None)`

  Write property tests for the binary operation `func`.

  While binary operations are not particularly common, they have such nice properties to test that it seems a shame not to demonstrate them with a ghostwriter. For an operator `f`, test that:

  - if associative, `f(a, f(b, c)) == f(f(a, b), c)`
  - if commutative, `f(a, b) == f(b, a)`
  - if identity is not None, `f(a, identity) == a`
  - if distributes_over is `+`, `f(a, b) + f(a, c) == f(a, b+c)`

  For example:

  ```python
  ghostwriter.binary_operation(
      operator.mul,
      identity=1,
      distributes_over=operator.add,
      style="unittest",
  )
  ```

- `hypothesis.extra.ghostwriter.ufunc(func, *, except_=(), style='pytest', annotate=None)[source]`

  Write a property-based test for the array ufunc `func`.

  The resulting test checks that your ufunc or gufunc has the expected broadcasting and dtype casting behaviour. You will probably want to add extra assertions, but as with the other ghostwriters this gives you a great place to start.

  ```console
  hypothesis write numpy.matmul
  ```

A note for test-generation researchers
--------------------------------------

Ghostwritten tests are intended as a starting point for human authorship, to demonstrate best practice, help novices past blank-page paralysis, and save time for experts. They may be ready-to-run, or include placeholders and `# TODO:` comments to fill in strategies for unknown types. In either case, improving tests for their own code gives users a well-scoped and immediately rewarding context in which to explore property-based testing.

By contrast, most test-generation tools aim to produce ready-to-run test suites… and implicitly assume that the current behavior is the desired behavior. However, the code might contain bugs, and we want our tests to fail if it does! Worse, tools require that the code to be tested is finished and executable, making it impossible to generate tests as part of the development process.

Fraser 2013 found that evolving a high-coverage test suite (e.g. Randoop, EvoSuite, Pynguin) “leads to clear improvements in commonly applied quality metrics such as code coverage [but] no measurable improvement in the number of bugs actually found by developers” and that “generating a set of test cases, even high coverage test cases, does not necessarily improve our ability to test software”. Invariant detection (famously Daikon; in PBT see e.g. Alonso 2022, QuickSpec, Speculate) relies on code execution. Program slicing (e.g. FUDGE, FuzzGen, WINNIE) requires downstream consumers of the code to test.

Ghostwriter inspects the function name, argument names and types, and docstrings. It can be used on buggy or incomplete code, runs in a few seconds, and produces a single semantically-meaningful test per function or group of functions. Rather than detecting regressions, these tests check semantic properties such as encode/decode or save/load round-trips, for commutative, associative, and distributive operations, equivalence between methods, array shapes, and idempotence. Where no property is detected, we simply check for ‘no error on valid input’ and allow the user to supply their own invariants.Evaluations such as the SBFT24 competition measure performance on a task which the Ghostwriter is not intended to perform. I’d love to see qualitative user studies, such as PBT in Practice for test generation, which could check whether the Ghostwriter is onto something or tilting at windmills. If you’re interested in similar questions, drop me an email!

## Observability

:::{note}
The Tyche VSCode extension provides an in-editor UI for observability results generated by Hypothesis. If you want to view observability results, rather than programmatically consume or display them, we recommend using Tyche.
:::

:::{warning}
This feature is experimental, and could have breaking changes or even be removed without notice. Try it out, let us know what you think, but don’t rely on it just yet!
:::

## Motivation

Understanding what your code is doing—for example, why your test failed—is often a frustrating exercise in adding some more instrumentation or logging (or `print()` calls) and running it again. The idea of observability is to let you answer questions you didn’t think of in advance. In slogan form:

> Debugging should be a data analysis problem.

By default, Hypothesis only reports the minimal failing example… but sometimes you might want to know something about all the examples. Printing them to the terminal by increasing [Verbosity](#verbosity) might be nice, but isn’t always enough.

This feature gives you an analysis-ready dataframe with useful columns and one row per test case, with columns from arguments to code coverage to pass/fail status.

This is deliberately a much lighter-weight and task-specific system than e.g. OpenTelemetry. It’s also less detailed than time-travel debuggers such as `rr` or `pytrace`, because there’s no good way to compare multiple traces from these tools and their Python support is relatively immature.

## Configuration

If you set the `HYPOTHESIS_EXPERIMENTAL_OBSERVABILITY` environment variable, Hypothesis will log various observations to jsonlines files in the `.hypothesis/observed/` directory. You can load and explore these with e.g.

```python
pd.read_json(".hypothesis/observed/*_testcases.jsonl", lines=True)
```

or by using the `sqlite-utils` and `datasette` libraries:

```bash
sqlite-utils insert testcases.db testcases .hypothesis/observed/*_testcases.jsonl --nl --flatten
datasette serve testcases.db
```

If you are experiencing a significant slow-down, you can try setting `HYPOTHESIS_EXPERIMENTAL_OBSERVABILITY_NOCOVER` instead; this will disable coverage information collection. This should not be necessary on Python 3.12 or later, where coverage collection is very fast.

## Collecting more information

If you want to record more information about your test cases than the arguments and outcome—for example, was `x` a binary tree? what was the difference between the expected and the actual value? how many queries did it take to find a solution?—Hypothesis makes this easy.

- `event()` accepts a string label, and optionally a string, int, or float observation associated with it. All events are collected and summarized in [Test statistics](#test-statistics), as well as included on a per-test-case basis in our observations.
- `target()` is a special case of numeric-valued events: as well as recording them in observations, Hypothesis will try to maximize the targeted value. Knowing that, you can use this to guide the search for failing inputs.

## Data Format

We dump observations in [json lines](https://jsonlines.org/) format, with each line describing either a test case or an information message. The tables below are derived from this [machine-readable JSON schema](https://github.com/HypothesisWorks/hypothesis/blob/master/hypothesis-python/src/hypothesis/internal/observability/schema.json), to provide both readable and verifiable specifications.

Note that we use `json.dumps()` and can therefore emit non-standard JSON which includes infinities and NaN. This is valid in [JSON5](https://json5.org/), and supported by some JSON parsers including Gson in Java, `JSON.parse()` in Ruby, and of course in Python.

### Information message

Info, alert, and error messages correspond to a group of test cases or the overall run, and are intended for humans rather than machine analysis.

| Property | Description |
|----------|-------------|
| `type` | A tag which labels this observation as general information to show the user. Hypothesis uses info messages to report statistics; alert or error messages can be provided by plugins. <br> **enum**: `info`, `alert`, `error` |
| `title` | The title of this message. <br> **type**: string |
| `body` | The body of the message. Strings are presumed to be human-readable messages in markdown format; dictionaries may contain arbitrary information (as for test-case metadata). <br> **type**: string / object |
| `test_function` | The name or representation of the test function we’re running. For Hypothesis, usually the Pytest nodeid. <br> **type**: string |
| `run_start_time` | Unix timestamp at which we started running this test function, so that later analysis can group test cases by run. <br> **type**: number |

### Test case

Describes the inputs to and result of running some test function on a particular input. The test might have passed, failed, or been abandoned part way through (e.g. because we failed a `@given` condition).

| Property | Description |
|----------|-------------|
| `type` | A tag which labels this observation as data about a specific test case. <br> **const**: `test_case` |
| `status` | Whether the test passed, failed, or was aborted before completion (e.g. due to use of `assume()`). <br> **enum**: `passed`, `failed`, `gave_up` |
| `reason` | If non-empty, the reason for which the test failed or was abandoned. For Hypothesis, this is usually the exception type and location. <br> **type**: string |
| `repr` | The string representation of the input. In Hypothesis, this includes the property name and arguments (like `test_foo(x=1)`). <br> **type**: string |
| `args` | A structured json-encoded representation of the input. Hypothesis provides a dictionary of argument names to json-ified values, including interactive draws from the `data` strategy. <br> **type**: object |
| `generation` | How the input was generated, if known. In Hypothesis this might be an explicit example, generated during a particular phase with some backend, or by replaying the minimal failing example. <br> **type**: string / null |
| `features` | Runtime observations which might help explain what this test case did. Hypothesis includes `coverage` and timing information here. <br> **type**: object |
| `coverage` | Mapping of filename to list of covered line numbers, if coverage information is available, or `null` if not. Hypothesis deliberately omits stdlib and site-packages code. <br> **type**: object / null <br> **items**: array of unique integers ≥ 1 |
| `timings` | The time in seconds taken by non-overlapping parts of this test case. Hypothesis reports e.g. `generate`, `execute`, and `shrink`. <br> **type**: object <br> **values**: number ≥ 0 |
| `metadata` | Arbitrary metadata which might be of interest, but does not semantically fit in ‘features’. For example, Hypothesis includes the traceback for failing tests here. <br> **type**: object |
| `test_function` | The name or representation of the test function we’re running. <br> **type**: string |
| `run_start_time` | Unix timestamp at which we started running this test function, so that later analysis can group test cases by run. <br> **type**: number |

### Hypothesis metadata

While the observability format is agnostic to the property-based testing library which generated it, Hypothesis includes specific values in the `metadata` key for test cases. You may rely on these being present if and only if the observation was generated by Hypothesis.

| Property | Description |
|----------|-------------|
| `traceback` | The traceback for failing tests, if and only if `status == "failed"`. <br> **type**: string / null |
| `phase` | The phase in which this test case was generated (e.g. `reuse`, `generate`, `shrink`). <br> **type**: string / null |
| `conjecture_statistics` | The number of times each predicate was satisfied or not during generation. <br> **type**: object <br> **values**: `{ "satisfied": integer ≥ 0, "unsatisfied": integer ≥ 0 }` |
| `backend_metadata` | Backend-specific observations from `data.conjecture_metadata`. <br> **type**: object |
| `examples` | The result of `data.examples()`. <br> **type**: array of strings |
| `max_depth` | The result of `data.max_depth`. <br> **type**: integer |
| `import_time` | The unix timestamp when Hypothesis was imported. <br> **type**: number |
| `hypothesis_version` | The Hypothesis version string. <br> **type**: string |
| `conjecture_status` | The internal status of the ConjectureData for this test case. The values are as follows: `0 = VALID`, `1 = INVALID`, `2 = OVERRUN`, `3 = DRAW_BITS_OVERFLOW`. <br> **type**: number <br> **enum**: 0, 1, 2, 3 |
| `forced` | The internal `forced` flag. <br> **type**: string / null |

### Choices metadata

These additional metadata elements are included in `metadata` (as e.g. `metadata["choice_nodes"]` or `metadata["choice_spans"]`), if and only if `OBSERVABILITY_CHOICES` is set.

| Property | Description |
|----------|-------------|
| `choice_nodes` | **Warning**: EXPERIMENTAL AND UNSTABLE. This attribute may change format or disappear without warning. The sequence of choices made during this test case. This includes the choice value, as well as its constraints and whether it was forced or not. Only present if `OBSERVABILITY_CHOICES` is set. <br> **Note**: The choice sequence is a relatively low-level implementation detail of Hypothesis, and is exposed in observability for users building tools or research on top of Hypothesis. See [the developer documentation](https://hypothesis.works/articles/choices/) for details. <br> **type**: array / null <br> **items**: object with properties `type` (`integer`, `float`, `string`, `bytes`, `boolean`), `value`, `constraints` (object), `forced` (boolean) |
| `choice_spans` | **Warning**: EXPERIMENTAL AND UNSTABLE. This attribute may change format or disappear without warning. The semantically-meaningful spans of the choice sequence of this test case. Each span has the format `[start_index, end_index, label]`. Only present if `OBSERVABILITY_CHOICES` is set. <br> **Note**: Spans are a relatively low-level implementation detail of Hypothesis, and are exposed in observability for users building tools or research on top of Hypothesis. See [the developer documentation](https://hypothesis.works/articles/choices/) for details. <br> **type**: array <br> **items**: array of `[integer, integer, string]` |The Hypothesis pytest plugin
=============================

Hypothesis includes a tiny plugin to improve integration with pytest, which is activated by default (but does not affect other test runners). It aims to improve the integration between Hypothesis and Pytest by providing extra information and convenient access to config options.

- `pytest --hypothesis-show-statistics` can be used to display test and data generation statistics.
- `pytest --hypothesis-profile=<profile name>` can be used to load a settings profile (as in `load_profile()`).
- `pytest --hypothesis-verbosity=<level name>` can be used to override the current `Verbosity` setting.
- `pytest --hypothesis-seed=<an int>` can be used to reproduce a failure with a particular seed (as in `@seed`).
- `pytest --hypothesis-explain` can be used to temporarily enable `Phase.explain`.

Finally, all tests that are defined with Hypothesis automatically have `@pytest.mark.hypothesis` applied to them. See [here](https://docs.pytest.org/en/stable/how-to/mark.html) for information on working with markers.

> **Note**
>
> Pytest will load the plugin automatically if Hypothesis is installed. You don’t need to do anything at all to use it.
>
> If this causes problems, you can avoid loading the plugin with the `-p no:hypothesis` pytest option.

Test statistics
===============

> **Note**
>
> While test statistics are only available under pytest, you can use the [observability interface](https://hypothesis.readthedocs.io/en/latest/healthchecks.html#observability) to view similar information about your tests.

You can see a number of statistics about executed tests by passing the command line argument `--hypothesis-show-statistics`. This will include some general statistics about the test:

For example, if you ran the following with `--hypothesis-show-statistics`:

```python
from hypothesis import given, strategies as st

@given(st.integers())
def test_integers(i):
    pass
```

You would see:

```
- during generate phase (0.06 seconds):
  - Typical runtimes: < 1ms, ~ 47% in data generation
  - 100 passing examples, 0 failing examples, 0 invalid examples
  - Stopped because settings.max_examples=100
```

The final “Stopped because” line tells you why Hypothesis stopped generating new examples. This is typically because we hit `max_examples`, but occasionally because we exhausted the search space or because shrinking was taking a very long time. This can be useful for understanding the behaviour of your tests.

In some cases (such as filtered and recursive strategies) you will see events mentioned which describe some aspect of the data generation:

```python
from hypothesis import given, strategies as st

@given(st.integers().filter(lambda x: x % 2 == 0))
def test_even_integers(i):
    pass
```

You would see something like:

```
test_even_integers:
- during generate phase (0.08 seconds):
  - Typical runtimes: < 1ms, ~ 57% in data generation
  - 100 passing examples, 0 failing examples, 12 invalid examples
  - Events:
    * 51.79%, Retried draw from integers().filter(lambda x: x % 2 == 0) to satisfy filter
    * 10.71%, Aborted test because unable to satisfy integers().filter(lambda x: x % 2 == 0)
  - Stopped because settings.max_examples=100
```

hypothesis[cli]
===============

> **Note**
>
> This feature requires the `hypothesis[cli]` extra, via `pip install hypothesis[cli]`.

```console
$ hypothesis --help
Usage: hypothesis [OPTIONS] COMMAND [ARGS]...

Options:
  --version   Show the version and exit.
  -h, --help  Show this message and exit.

Commands:
  codemod  `hypothesis codemod` refactors deprecated or inefficient code.
  fuzz     [hypofuzz] runs tests with an adaptive coverage-guided fuzzer.
  write    `hypothesis write` writes property-based tests for you!
```

This module requires the `click` package, and provides Hypothesis’ command-line interface, for e.g. ‘ghostwriting’ tests via the terminal. It’s also where HypoFuzz adds the `hypothesis fuzz` command (learn more about that [here](https://hypofuzz.com/)).

hypothesis[codemods]
====================

> **Note**
>
> This feature requires the `hypothesis[codemods]` extra, via `pip install hypothesis[codemods]`.

This module provides codemods based on the LibCST library, which can both detect and automatically fix issues with code that uses Hypothesis, including upgrading from deprecated features to our recommended style.

You can run the codemods via our CLI:

```console
$ hypothesis codemod --help
Usage: hypothesis codemod [OPTIONS] PATH...

`hypothesis codemod` refactors deprecated or inefficient code.

It adapts `python -m libcst.tool`, removing many features and config
options which are rarely relevant for this purpose. If you need more
control, we encourage you to use the libcst CLI directly; if not this one
is easier.

PATH is the file(s) or directories of files to format in place, or "-" to
read from stdin and write to stdout.

Options:
  -h, --help  Show this message and exit.
```

Alternatively you can use `python -m libcst.tool`, which offers more control at the cost of additional configuration (adding `'hypothesis.extra'` to the `modules` list in `.libcst.codemod.yaml`) and some issues on Windows.

- `hypothesis.extra.codemods.refactor(code)`[[source]](https://github.com/HypothesisWorks/hypothesis/blob/master/hypothesis-python/src/hypothesis/extra/codemods.py)

  Update a source code string from deprecated to modern Hypothesis APIs.

  This may not fix all the deprecation warnings in your code, but we’re confident that it will be easier than doing it all by hand.

  We recommend using the CLI, but if you want a Python function here it is.

hypothesis[dpcontracts]
=======================

> **Note**
>
> This feature requires the `hypothesis[dpcontracts]` extra, via `pip install hypothesis[dpcontracts]`.

> **Tip**
>
> For new projects, we recommend using either [deal](https://github.com/life4/deal) or [icontract](https://github.com/Parquery/icontract) and [icontract-hypothesis](https://github.com/Parquery/icontract-hypothesis) over dpcontracts. They’re generally more powerful tools for design-by-contract programming, and have substantially nicer Hypothesis integration too!

This module provides tools for working with the dpcontracts library, because combining contracts and property-based testing works really well.

It requires `dpcontracts >= 0.4`.

- `hypothesis.extra.dpcontracts.fulfill(contract_func)`[[source]](https://github.com/HypothesisWorks/hypothesis/blob/master/hypothesis-python/src/hypothesis/extra/dpcontracts.py)

  Decorate `contract_func` to reject calls which violate preconditions, and retry them with different arguments.

  This is a convenience function for testing internal code that uses dpcontracts, to automatically filter out arguments that would be rejected by the public interface before triggering a contract error.

  This can be used as `builds(fulfill(func), ...)` or in the body of the test e.g. `assert fulfill(func)(*args)`.