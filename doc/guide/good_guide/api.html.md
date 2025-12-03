# API Reference

Reference for non-strategy objects that are part of the Hypothesis API. For documentation on strategies, see the strategies reference.

## `@given`

- `hypothesis.given(*_given_arguments, **_given_kwargs)` [source]

The `@given` decorator turns a function into a Hypothesis test. This is the main entry point to Hypothesis.

See also the [Introduction to Hypothesis tutorial](#), which introduces defining Hypothesis tests with `@given`.

### Arguments to `@given`

Arguments to `@given` may be either positional or keyword arguments:

```python
@given(st.integers(), st.floats())
def test_one(x, y):
    pass

@given(x=st.integers(), y=st.floats())
def test_two(x, y):
    pass
```

If using keyword arguments, the arguments may appear in any order, as with standard Python functions:

```python
# different order, but still equivalent to before
@given(y=st.floats(), x=st.integers())
def test(x, y):
    assert isinstance(x, int)
    assert isinstance(y, float)
```

If `@given` is provided fewer positional arguments than the decorated test, the test arguments are filled in on the right side, leaving the leftmost positional arguments unfilled:

```python
@given(st.integers(), st.floats())
def test(manual_string, y, z):
    assert manual_string == "x"
    assert isinstance(y, int)
    assert isinstance(z, float)

# `test` is now a callable which takes one argument `manual_string`
test("x")  # or equivalently: test(manual_string="x")
```

The reason for this “from the right” behavior is to support using `@given` with instance methods, by automatically passing through `self`:

```python
class MyTest(TestCase):
    @given(st.integers())
    def test(self, x):
        assert isinstance(self, MyTest)
        assert isinstance(x, int)
```

If (and only if) using keyword arguments, `@given` may be combined with `**kwargs` or `*args`.

It is an error to:
- Mix positional and keyword arguments to `@given`.
- Use `@given` with a function that has a default value for an argument.
- Use `@given` with positional arguments with a function that uses `*args`, `**kwargs`, or keyword-only arguments.

The function returned by `given` has all the same arguments as the original test, minus those that are filled in by `@given`. See the notes on framework compatibility for how this interacts with features of other testing libraries, such as pytest fixtures.

## `hypothesis.infer`

An alias for `...` (`Ellipsis`). `infer` can be passed to `@given` or `builds()` to indicate that a strategy for that parameter should be inferred from its type annotations.

In all cases, using `infer` is equivalent to using `...`.

### Inferred strategies

In some cases, Hypothesis can work out what to do when you omit arguments. This is based on introspection, not magic, and therefore has well-defined limits.

`builds()` will check the signature of the target (using `inspect.signature()`). If there are required arguments with type annotations and no strategy was passed to `builds()`, `from_type()` is used to fill them in. You can also pass the value `...` (`Ellipsis`) as a keyword argument, to force this inference for arguments with a default value.

`@given` does not perform any implicit inference for required arguments, as this would break compatibility with pytest fixtures. `...` (`Ellipsis`), can be used as a keyword argument to explicitly fill in an argument from its type annotation. You can also use the `infer` alias if writing a literal `...` seems too weird.

`@given(...)` can also be specified to fill all arguments from their type annotations.

### Limitations

Hypothesis does not inspect PEP 484 type comments at runtime. While `from_type()` will work as usual, inference in `builds()` and `@given` will only work if you manually create the `__annotations__` attribute (e.g. by using `@annotations(...)` and `@returns(...)` decorators).

The `typing` module changes between different Python releases, including at minor versions. These are all supported on a best-effort basis, but you may encounter problems. Please report them to us, and consider updating to a newer version of Python as a workaround.

## Explicit inputs

See also the [Replaying failed tests tutorial](#), which discusses using explicit inputs to reproduce failures.

### `class hypothesis.example(*args, **kwargs)` [source]

Add an explicit input to a Hypothesis test, which Hypothesis will always try before generating random inputs. This combines the randomized nature of Hypothesis generation with a traditional parametrized test.

For example:

```python
@example("Hello World")
@example("some string with special significance")
@given(st.text())
def test_strings(s):
    ...
```

will call `test_strings("Hello World")` and `test_strings("some string with special significance")` before generating any random inputs.

`@example` may be placed in any order relative to `@given` and `@settings`.

Explicit inputs from `@example` are run in the `Phase.explicit` phase. Explicit inputs do not count towards `settings.max_examples`. Note that explicit inputs added by `@example` do not shrink. If an explicit input fails, Hypothesis will stop and report the failure without generating any random inputs.

`@example` can also be used to easily reproduce a failure. For instance, if Hypothesis reports that `f(n=[0, math.nan])` fails, you can add `@example(n=[0, math.nan])` to your test to quickly reproduce that failure.

### Arguments to `@example`

Arguments to `@example` have the same behavior and restrictions as arguments to `@given`. This means they may be either positional or keyword arguments (but not both in the same `@example`):

```python
@example(1, 2)
@example(x=1, y=2)
@given(st.integers(), st.integers())
def test(x, y):
    pass
```

Noting that while arguments to `@given` are strategies (like `integers()`), arguments to `@example` are values instead (like `1`).

See the Arguments to `@given` section for full details.

### `example.xfail(condition=True, *, reason='', raises=<class 'BaseException'>)`

Mark this example as an expected failure, similarly to `pytest.mark.xfail(strict=True)`.

Expected-failing examples allow you to check that your test does fail on some examples, and therefore build confidence that passing tests are because your code is working, not because the test is missing something.

**Note**: Expected-failing examples are handled separately from those generated by strategies, so you should usually ensure that there is no overlap.

```python
@example(x=1, y=0).xfail(raises=ZeroDivisionError)
@given(x=st.just(1), y=st.integers())  # Missing `.filter(bool)`!
def test_fraction(x, y):
    # This test will try the explicit example and see it fail as
    # expected, then go on to generate more examples from the
    # strategy. If we happen to generate y=0, the test will fail
    # because only the explicit example is treated as xfailing.
    x / y
```

### `example.via(whence, /)` [source]

Attach a machine-readable label noting what the origin of this example was.

`example.via` is completely optional and does not change runtime behavior. `example.via` is intended to support self-documenting behavior, as well as tooling which might add (or remove) `@example` decorators automatically. For example:

**Note**: HypoFuzz uses `example.via` to tag examples in the patch of its high-coverage set of explicit inputs, on the patches page.

## Reproducing inputs

See also the [Replaying failed tests tutorial](#).

### `hypothesis.reproduce_failure(version, blob)` [source]

Run the example corresponding to the binary `blob` in order to reproduce a failure. `blob` is a serialized version of the internal input representation of Hypothesis.

A test decorated with `@reproduce_failure` always runs exactly one example, which is expected to cause a failure. If the provided `blob` does not cause a failure, Hypothesis will raise `DidNotReproduce`.

Hypothesis will print an `@reproduce_failure` decorator if `settings.print_blob` is `True` (which is the default in CI).

`@reproduce_failure` is intended to be temporarily added to your test suite in order to reproduce a failure. It is not intended to be a permanent addition to your test suite. Because of this, no compatibility guarantees are made across Hypothesis versions, and `@reproduce_failure` will error if used on a different Hypothesis version than it was created for.

See also the [Replaying failed tests tutorial](#).

### `hypothesis.seed(seed)` [source]

Seed the randomness for this test.

`seed` may be any hashable object. No exact meaning for `seed` is provided other than that for a fixed seed value Hypothesis will produce the same examples (assuming that there are no other sources of nondeterminism, such as timing, hash randomization, or external state).

For example, the following test function and `RuleBasedStateMachine` will each generate the same series of examples each time they are executed:

```python
@seed(1234)
@given(st.integers())
def test(n):
    ...

@seed(6789)
class MyMachine(RuleBasedStateMachine):
    ...
```

If using pytest, you can alternatively pass `--hypothesis-seed` on the command line.

Setting a seed overrides `settings.derandomize`, which is designed to enable deterministic CI tests rather than reproducing observed failures.

Hypothesis will only print the seed which would reproduce a failure if a test fails in an unexpected way, for instance inside Hypothesis internals.

## Control

Functions that can be called from anywhere inside a test, to either modify how Hypothesis treats the current test case, or to give Hypothesis more information about the current test case.

### `hypothesis.assume(condition)` [source]

Calling `assume` is like an assert that marks the example as bad, rather than failing the test.

This allows you to specify properties that you assume will be true, and let Hypothesis try to avoid similar examples in future.

### `hypothesis.event(value, payload='')` [source]

Record an event that occurred during this test. Statistics on the number of test runs with each event will be reported at the end if you run Hypothesis in statistics reporting mode.

Event values should be strings or convertible to them. If an optional payload is given, it will be included in the string for Test statistics.

You can mark custom events in a test using `event()`:

```python
from hypothesis import event, given, strategies as st

@given(st.integers().filter(lambda x: x % 2 == 0))
def test_even_integers(i):
    event(f"i mod 3 = {i%3}")
```

These events appear in observability output, as well as the output of our pytest plugin when run with `--hypothesis-show-statistics`.For instance, in the latter case, you would see output like:

```
test_even_integers:
- during generate phase (0.09 seconds):
  - Typical runtimes: < 1ms, ~ 59% in data generation
  - 100 passing examples, 0 failing examples, 32 invalid examples
  - Events:
    * 54.55%, Retried draw from integers().filter(lambda x: x % 2 == 0) to satisfy filter
    * 31.06%, i mod 3 = 2
    * 28.79%, i mod 3 = 0
    * 24.24%, Aborted test because unable to satisfy integers().filter(lambda x: x % 2 == 0)
    * 15.91%, i mod 3 = 1
- Stopped because settings.max_examples=100
```

Arguments to event can be any hashable type, but two events will be considered the same if they are the same when converted to a string with `str`.

## Targeted property-based testing

Targeted property-based testing combines the advantages of both search-based and property-based testing. Instead of being completely random, targeted PBT uses a search-based component to guide the input generation towards values that have a higher probability of falsifying a property. This explores the input space more effectively and requires fewer tests to find a bug or achieve a high confidence in the system being tested than random PBT. (Löscher and Sagonas)

This is not always a good idea - for example calculating the search metric might take time better spent running more uniformly-random test cases, or your target metric might accidentally lead Hypothesis away from bugs - but if there is a natural metric like “floating-point error”, “load factor” or “queue length”, we encourage you to experiment with targeted testing.

We recommend that users also skim the papers introducing targeted PBT; from ISSTA 2017 and ICST 2018. For the curious, the initial implementation in Hypothesis uses hill-climbing search via a mutating fuzzer, with some tactics inspired by simulated annealing to avoid getting stuck and endlessly mutating a local maximum.

```python
from hypothesis import given, strategies as st, target

@given(st.floats(0, 1e100), st.floats(0, 1e100), st.floats(0, 1e100))
def test_associativity_with_target(a, b, c):
    ab_c = (a + b) + c
    a_bc = a + (b + c)
    difference = abs(ab_c - a_bc)
    target(difference)  # Without this, the test almost always passes
    assert difference < 2.0
```

- `hypothesis.target(observation, *, label='')`[source]

Calling this function with an `int` or `float` observation gives it feedback with which to guide our search for inputs that will cause an error, in addition to all the usual heuristics. Observations must always be finite. Hypothesis will try to maximize the observed value over several examples; almost any metric will work so long as it makes sense to increase it. For example, `-abs(error)` is a metric that increases as `error` approaches zero.

Example metrics:
- Number of elements in a collection, or tasks in a queue
- Mean or maximum runtime of a task (or both, if you use `label`)
- Compression ratio for data (perhaps per-algorithm or per-level)
- Number of steps taken by a state machine

The optional `label` argument can be used to distinguish between and therefore separately optimise distinct observations, such as the mean and standard deviation of a dataset. It is an error to call `target()` with any label more than once per test case.

**Note**

The more examples you run, the better this technique works. As a rule of thumb, the targeting effect is noticeable above `max_examples=1000`, and immediately obvious by around ten thousand examples per label used by your test. Test statistics include the best score seen for each label, which can help avoid the threshold problem when the minimal example shrinks right down to the threshold of failure (issue #2180).

## Settings

See also the tutorial for settings.

- `class hypothesis.settings(parent=None, *, max_examples=not_set, derandomize=not_set, database=not_set, verbosity=not_set, phases=not_set, stateful_step_count=not_set, report_multiple_bugs=not_set, suppress_health_check=not_set, deadline=not_set, print_blob=not_set, backend=not_set)`

A settings object controls the following aspects of test behavior: `max_examples`, `derandomize`, `database`, `verbosity`, `phases`, `stateful_step_count`, `report_multiple_bugs`, `suppress_health_check`, `deadline`, `print_blob`, and `backend`.

A settings object can be applied as a decorator to a test function, in which case that test function will use those settings. A test may only have one settings object applied to it. A settings object can also be passed to `register_profile()` or as a parent to another `settings`.

### Attribute inheritance

Settings objects are immutable once created. When a settings object is created, it uses the value specified for each attribute. Any attribute which is not specified will inherit from its value in the `parent` settings object. If `parent` is not passed, any attributes which are not specified will inherit from the current settings profile instead.

For instance, `settings(max_examples=10)` will have a `max_examples` of `10`, and the value of all other attributes will be equal to its value in the current settings profile.

Changes made from activating a new settings profile with `load_profile()` will be reflected in settings objects created after the profile was loaded, but not in existing settings objects.

### Built-in profiles

While you can register additional profiles with `register_profile()`, Hypothesis comes with two built-in profiles: `default` and `ci`.

By default, the `default` profile is active. If the `CI` environment variable is set to any value, the `ci` profile is active by default. Hypothesis also automatically detects various vendor-specific CI environment variables.

The attributes of the currently active settings profile can be retrieved with `settings()` (so `settings().max_examples` is the currently active default for `settings.max_examples`).

The settings attributes for the built-in profiles are as follows:

```python
default = settings.register_profile(
    "default",
    max_examples=100,
    derandomize=False,
    database=not_set,  # see settings.database for the default database
    verbosity=Verbosity.normal,
    phases=tuple(Phase),
    stateful_step_count=50,
    report_multiple_bugs=True,
    suppress_health_check=(),
    deadline=duration(milliseconds=200),
    print_blob=False,
    backend="hypothesis",
)

ci = settings.register_profile(
    "ci",
    parent=default,
    derandomize=True,
    deadline=None,
    database=None,
    print_blob=True,
    suppress_health_check=[HealthCheck.too_slow],
)
```

You can replace either of the built-in profiles with `register_profile()`:

```python
# run more examples in CI
settings.register_profile(
    "ci",
    settings.get_profile("ci"),
    max_examples=1000,
)
```

- **property max_examples**

Once this many satisfying examples have been considered without finding any counter-example, Hypothesis will stop looking.

Note that we might call your test function fewer times if we find a bug early or can tell that we’ve exhausted the search space; or more if we discard some examples due to use of `.filter()`, `assume()`, or a few other things that can prevent the test case from completing successfully.

The default value is chosen to suit a workflow where the test will be part of a suite that is regularly executed locally or on a CI server, balancing total running time against the chance of missing a bug.

If you are writing one-off tests, running tens of thousands of examples is quite reasonable as Hypothesis may miss uncommon bugs with default settings. For very complex code, we have observed Hypothesis finding novel bugs after several million examples while testing SymPy. If you are running more than 100k examples for a test, consider using our integration for coverage-guided fuzzing - it really shines when given minutes or hours to run.

The default max examples is `100`.

- **property derandomize**

If True, seed Hypothesis’ random number generator using a hash of the test function, so that every run will test the same set of examples until you update Hypothesis, Python, or the test function.

This allows you to check for regressions and look for bugs using separate settings profiles - for example running quick deterministic tests on every commit, and a longer non-deterministic nightly testing run.

The default is `False`. If running on CI, the default is `True` instead.

- **property database**

An instance of `ExampleDatabase` that will be used to save examples to and load previous examples from.

If not set, a `DirectoryBasedExampleDatabase` is created in the current working directory under `.hypothesis/examples`. If this location is unusable, e.g. due to the lack of read or write permissions, Hypothesis will emit a warning and fall back to an `InMemoryExampleDatabase`.

If `None`, no storage will be used.

See the database documentation for a list of database classes, and how to define custom database classes.

- **property verbosity**

Control the verbosity level of Hypothesis messages.

To see what’s going on while Hypothesis runs your tests, you can turn up the verbosity setting.

```python
>>> from hypothesis import settings, Verbosity
>>> from hypothesis.strategies import lists, integers
>>> @given(lists(integers()))
... @settings(verbosity=Verbosity.verbose)
... def f(x):
...     assert not any(x)
...
>>> f()
Trying example: []
Falsifying example: [-1198601713, -67, 116, -29578]
Shrunk example to [-1198601713]
Shrunk example to [-128]
Shrunk example to [32]
Shrunk example to [1]
[1]
```

The four levels are `Verbosity.quiet`, `Verbosity.normal`, `Verbosity.verbose`, and `Verbosity.debug`. `Verbosity.normal` is the default. For `Verbosity.quiet`, Hypothesis will not print anything out, not even the final falsifying example. `Verbosity.debug` is basically `Verbosity.verbose` but a bit more so. You probably don’t want it.

Verbosity can be passed either as a `Verbosity` enum value, or as the corresponding string value, or as the corresponding integer value. For example:

If you are using pytest, you may also need to disable output capturing for passing tests to see verbose output as tests run.

- **property phases**

Control which phases should be run.

Hypothesis divides tests into logically distinct phases.

- `Phase.explicit`: Running explicit examples from `@example`.
- `Phase.reuse`: Running examples from the database which previously failed.
Phase.generate: Generating new random examples.
Phase.target: Mutating examples for targeted property-based testing. Requires Phase.generate.
Phase.shrink: Shrinking failing examples.
Phase.explain: Attempting to explain why a failure occurred. Requires Phase.shrink.

The phases argument accepts a collection with any subset of these. E.g.
`settings(phases=[Phase.generate, Phase.shrink])`
will generate new examples and shrink them, but will not run explicit examples or reuse previous failures, while `settings(phases=[Phase.explicit])`
will only run explicit examples from `@example`.

Phases can be passed either as a `Phase` enum value, or as the corresponding string value. For example:

Following the first failure, Hypothesis will (usually, depending on which `Phase` is enabled) track which lines of code are always run on failing but never on passing inputs. On 3.12+, this uses `sys.monitoring`, while 3.11 and earlier use `sys.settrace()`. For python 3.11 and earlier, we therefore automatically disable the explain phase on PyPy, or if you are using coverage or a debugger. If there are no clearly suspicious lines of code, we refuse the temptation to guess.

After shrinking to a minimal failing example, Hypothesis will try to find parts of the example – e.g. separate args to `@given` – which can vary freely without changing the result of that minimal failing example. If the automated experiments run without finding a passing variation, we leave a comment in the final report:
```python
test_x_divided_by_y(
    x=0,  # or any other generated value
    y=0,
)
```
Just remember that the lack of an explanation sometimes just means that Hypothesis couldn’t efficiently find one, not that no explanation (or simpler failing example) exists.

- **property stateful_step_count**  
  The maximum number of times to call an additional `@rule` method in stateful testing before we give up on finding a bug. Note that this setting is effectively multiplicative with max_examples, as each example will run for a maximum of `stateful_step_count` steps. The default stateful step count is `50`.

- **property report_multiple_bugs**  
  Because Hypothesis runs the test many times, it can sometimes find multiple bugs in a single run. Reporting all of them at once is usually very useful, but replacing the exceptions can occasionally clash with debuggers. If disabled, only the exception with the smallest minimal example is raised. The default value is `True`.

- **property suppress_health_check**  
  Suppress the given `HealthCheck` exceptions. Those health checks will not be raised by Hypothesis. To suppress all health checks, you can pass `suppress_health_check=list(HealthCheck)`. Health checks can be passed either as a `HealthCheck` enum value, or as the corresponding string value. For example: Health checks are proactive warnings, not correctness errors, so we encourage suppressing health checks where you have evaluated they will not pose a problem, or where you have evaluated that fixing the underlying issue is not worthwhile.  
  See also: [Suppress a health check everywhere how-to](#).

- **property deadline**  
  The maximum allowed duration of an individual test case, in milliseconds. You can pass an integer, float, or timedelta. If `None`, the deadline is disabled entirely. We treat the deadline as a soft limit in some cases, where that would avoid flakiness due to timing variability. The default deadline is 200 milliseconds. If running on CI, the default is `None` instead.

- **property print_blob**  
  If set to `True`, Hypothesis will print code for failing examples that can be used with `@reproduce_failure` to reproduce the failing example. The default value is `False`. If running on CI, the default is `True` instead.

- **property backend**  
  **Warning**: EXPERIMENTAL AND UNSTABLE - see Alternative backends for Hypothesis.  
  The importable name of a backend which Hypothesis should use to generate primitive types. We support heuristic-random, solver-based, and fuzzing-based backends.

- **static register_profile(name, parent=None, \*\*kwargs)[source]**  
  Register a settings object as a settings profile, under the name `name`. The `parent` and `kwargs` arguments to this method are as for `settings`. If a settings profile already exists under `name`, it will be overwritten. Registering a profile with the same name as the currently active profile will cause those changes to take effect in the active profile immediately, and do not require reloading the profile. Registered settings profiles can be retrieved later by name with `get_profile()`.

- **static get_profile(name)[source]**  
  Returns the settings profile registered under `name`. If no settings profile is registered under `name`, raises `InvalidArgument`.

- **static load_profile(name)[source]**  
  Makes the settings profile registered under `name` the active profile. If no settings profile is registered under `name`, raises `InvalidArgument`.

- **class hypothesis.Phase(value)[source]**  
  Options for the `settings.phases` argument to `@settings`.
  - `explicit = 'explicit'`: Controls whether explicit examples are run.
  - `reuse = 'reuse'`: Controls whether previous examples will be reused.
  - `generate = 'generate'`: Controls whether new examples will be generated.
  - `target = 'target'`: Controls whether examples will be mutated for targeting.
  - `shrink = 'shrink'`: Controls whether examples will be shrunk.
  - `explain = 'explain'`: Controls whether Hypothesis attempts to explain test failures.  
    The explain phase has two parts, each of which is best-effort - if Hypothesis can’t find a useful explanation, we’ll just print the minimal failing example.

- **class hypothesis.Verbosity(value)[source]**  
  Options for the `settings.verbosity` argument to `@settings`.
  - `quiet = 'quiet'`: Hypothesis will not print any output, not even the final falsifying example.
  - `normal = 'normal'`: Standard verbosity. Hypothesis will print the falsifying example, alongside any notes made with `note()` (only for the falsifying example).
  - `verbose = 'verbose'`: Increased verbosity. In addition to everything in `Verbosity.normal`, Hypothesis will print each example as it tries it, as well as any notes made with `note()` for every example. Hypothesis will also print shrinking attempts.
  - `debug = 'debug'`: Even more verbosity. Useful for debugging Hypothesis internals. You probably don’t want this.

- **class hypothesis.HealthCheck(value)[source]**  
  A `HealthCheck` is proactively raised by Hypothesis when Hypothesis detects that your test has performance problems, which may result in less rigorous testing than you expect. For example, if your test takes a long time to generate inputs, or filters away too many inputs using `assume()` or `.filter()`, Hypothesis will raise a corresponding health check. A health check is a proactive warning, not an error. We encourage suppressing health checks where you have evaluated they will not pose a problem, or where you have evaluated that fixing the underlying issue is not worthwhile. With the exception of `HealthCheck.function_scoped_fixture` and `HealthCheck.differing_executors`, all health checks warn about performance problems, not correctness errors.

**Disabling health checks**  
Health checks can be disabled by `settings.suppress_health_check`. To suppress all health checks, you can pass `suppress_health_check=list(HealthCheck)`.  
See also: [Suppress a health check everywhere how-to](#).

**Correctness health checks**  
Some health checks report potential correctness errors, rather than performance problems.  
- `HealthCheck.function_scoped_fixture` indicates that a function-scoped pytest fixture is used by an `@given` test. Many Hypothesis users expect function-scoped fixtures to reset once per input, but they actually reset once per test. We proactively raise `HealthCheck.function_scoped_fixture` to ensure you have considered this case.  
- `HealthCheck.differing_executors` indicates that the same `@given` test has been executed multiple times with multiple distinct executors. We recommend treating these particular health checks with more care, as suppressing them may result in an unsound test.

- `data_too_large = 'data_too_large'`: Checks if too many examples are aborted for being too large. This is measured by the number of random choices that Hypothesis makes in order to generate something, not the size of the generated object. For example, choosing a 100MB object from a predefined list would take only a few bits, while generating 10KB of JSON from scratch might trigger this health check.
- `filter_too_much = 'filter_too_much'`: Check for when the test is filtering out too many examples, either through use of `assume()` or `.filter()`, or occasionally for Hypothesis internal reasons.
- `too_slow = 'too_slow'`: Check for when input generation is very slow. Since Hypothesis generates 100 (by default) inputs per test execution, a slowdown in generating each input can result in very slow tests overall.
- `return_value = 'return_value'`: Deprecated; we always error if a test returns a non-None value.
- `large_base_example = 'large_base_example'`: Checks if the smallest natural input to your test is very large. This makes it difficult for Hypothesis to generate good inputs, especially when trying to shrink failing inputs.
- `not_a_test_method = 'not_a_test_method'`: Deprecated; we always error if `@given` is applied to a method defined by `unittest.TestCase` (i.e. not a test).
- `function_scoped_fixture = 'function_scoped_fixture'`: Checks if `@given` has been applied to a test with a pytest function-scoped fixture. Function-scoped fixtures run once for the whole function, not once per example, and this is usually not what you want. Because of this limitation, tests that need to set up or reset state for every example need to do so manually within the test itself, typically using an appropriate context manager. Suppress this health check only in the rare case that you are using a function-scoped fixture that does not need to be reset between individual examples, but for some reason you cannot use a wider fixture scope (e.g. session scope, module scope, class scope).This check requires the Hypothesis pytest plugin, which is enabled by default when running Hypothesis inside pytest.

- `differing_executors = 'differing_executors'`  
  Checks if `@given` has been applied to a test which is executed by different executors. If your test function is defined as a method on a class, that class will be your executor, and subclasses executing an inherited test is a common way for things to go wrong. The correct fix is often to bring the executor instance under the control of hypothesis by explicit parametrization over, or sampling from, subclasses, or to refactor so that `@given` is specified on leaf subclasses.

- `nested_given = 'nested_given'`  
  Checks if `@given` is used inside another `@given`. This results in quadratic generation and shrinking behavior, and can usually be expressed more cleanly by using `data()` to replace the inner `@given`. Nesting `@given` can be appropriate if you set appropriate limits for the quadratic behavior and cannot easily reexpress the inner function with `data()`. To suppress this health check, set `suppress_health_check=[HealthCheck.nested_given]` on the outer `@given`. Setting it on the inner `@given` has no effect. If you have more than one level of nesting, add a suppression for this health check to every `@given` except the innermost one.

## Database

- `class hypothesis.database.ExampleDatabase[source]`  
  A Hypothesis database, for use in `settings.database`. Hypothesis automatically saves failures to the database set in `settings.database`. The next time the test is run, Hypothesis will replay any failures from the database in `settings.database` for that test (in `Phase.reuse`). The database is best thought of as a cache that you never need to invalidate. Entries may be transparently dropped when upgrading your Hypothesis version or changing your test. Do not rely on the database for correctness; to ensure Hypothesis always tries an input, use `@example`. A Hypothesis database is a simple mapping of bytes to sets of bytes. Hypothesis provides several concrete database subclasses. To write your own database class, see Write a custom Hypothesis database.

## Change listening

An optional extension to `ExampleDatabase` is change listening. On databases which support change listening, calling `add_listener()` adds a function as a change listener, which will be called whenever a value is added, deleted, or moved inside the database. See `add_listener()` for details. All databases in Hypothesis support change listening. Custom database classes are not required to support change listening, though they will not be compatible with features that require change listening until they do so.

> **Note**  
> While no Hypothesis features currently require change listening, change listening is required by HypoFuzz.

## Database methods

**Required methods:**  
**Optional methods:**  
**Change listening methods:**

- `abstract save(key, value)[source]`  
  Save `value` under `key`. If `value` is already present in `key`, silently do nothing.

- `abstract delete(key, value)[source]`  
  Remove `value` from `key`. If `value` is not present in `key`, silently do nothing.

- `move(src, dest, value)[source]`  
  Move `value` from key `src` to key `dest`. Equivalent to `delete(src, value)` followed by `save(dest, value)`, but may have a more efficient implementation. Note that `value` will be inserted at `dest` regardless of whether it is currently present at `src`.

- `add_listener(f, /)[source]`  
  Add a change listener. `f` will be called whenever a value is saved, deleted, or moved in the database. `f` can be called with two different event values:  
  `("save", (key, value))`  
  `("delete", (key, value))`  
  where `key` and `value` are both `bytes`. There is no `move` event. Instead, a move is broadcasted as a `delete` event followed by a `save` event. For the `delete` event, `value` may be `None`. This might occur if the database knows that a deletion has occurred in `key`, but does not know what value was deleted.

- `remove_listener(f, /)[source]`  
  Removes `f` from the list of change listeners. If `f` is not in the list of change listeners, silently do nothing.

- `_broadcast_change(event)[source]`  
  Called when a value has been either added to or deleted from a key in the underlying database store. The possible values for `event` are:  
  `("save", (key, value))`  
  `("delete", (key, value))`  
  `value` may be `None` for the `delete` event, indicating we know that some value was deleted under this key, but not its exact value. Note that you should not assume your instance is the only reference to the underlying database store. For example, if two instances of `DirectoryBasedExampleDatabase` reference the same directory, `_broadcast_change` should be called whenever a file is added or removed from the directory, even if that database was not responsible for changing the file.

- `_start_listening()[source]`  
  Called when the database adds a change listener, and did not previously have any change listeners. Intended to allow databases to wait to start expensive listening operations until necessary. `_start_listening` and `_stop_listening` are guaranteed to alternate, so you do not need to handle the case of multiple consecutive `_start_listening` calls without an intermediate `_stop_listening` call.

- `class hypothesis.database.InMemoryExampleDatabase[source]`  
  A non-persistent example database, implemented in terms of an in-memory dictionary. This can be useful if you call a test function several times in a single session, or for testing other database implementations, but because it does not persist between runs we do not recommend it for general use.

- `class hypothesis.database.DirectoryBasedExampleDatabase(path)[source]`  
  Use a directory to store Hypothesis examples as files. Each test corresponds to a directory, and each example to a file within that directory. While the contents are fairly opaque, a `DirectoryBasedExampleDatabase` can be shared by checking the directory into version control, for example with the following `.gitignore`:  
  ```gitignore
  # Ignore files cached by Hypothesis...
  .hypothesis/*
  # except for the examples directory
  !.hypothesis/examples/
  ```  
  Note however that this only makes sense if you also pin to an exact version of Hypothesis, and we would usually recommend implementing a shared database with a network datastore — see `ExampleDatabase`, and the `MultiplexedDatabase` helper.

- `class hypothesis.database.GitHubArtifactDatabase(owner, repo, artifact_name='hypothesis-example-db', cache_timeout=datetime.timedelta(days=1), path=None)`  
  A file-based database loaded from a GitHub Actions artifact. You can use this for sharing example databases between CI runs and developers, allowing the latter to get read-only access to the former. This is particularly useful for continuous fuzzing (i.e. with HypoFuzz), where the CI system can help find new failing examples through fuzzing, and developers can reproduce them locally without any manual effort.  

  > **Note**  
  > You must provide `GITHUB_TOKEN` as an environment variable. In CI, Github Actions provides this automatically, but it needs to be set manually for local usage. In a developer machine, this would usually be a Personal Access Token. If the repository is private, it’s necessary for the token to have `repo` scope in the case of a classic token, or `actions:read` in the case of a fine-grained token.  

  In most cases, this will be used through the `MultiplexedDatabase`, by combining a local directory-based database with this one. For example:  
  ```python
  local = DirectoryBasedExampleDatabase(".hypothesis/examples")
  shared = ReadOnlyDatabase(GitHubArtifactDatabase("user", "repo"))
  settings.register_profile("ci", database=local)
  settings.register_profile("dev", database=MultiplexedDatabase(local, shared))
  # We don't want to use the shared database in CI, only to populate its local one.
  # which the workflow should then upload as an artifact.
  settings.load_profile("ci" if os.environ.get("CI") else "dev")
  ```  

  > **Note**  
  > Because this database is read-only, you always need to wrap it with the `ReadOnlyDatabase`.  

  A setup like this can be paired with a GitHub Actions workflow including something like the following:  
  ```yaml
  - name: Download example database
    uses: dawidd6/action-download-artifact@v9
    with:
      name: hypothesis-example-db
      path: .hypothesis/examples
      if_no_artifact_found: warn
      workflow_conclusion: completed
  - name: Run tests
    run: pytest
  - name: Upload example database
    uses: actions/upload-artifact@v3
    if: always()
    with:
      name: hypothesis-example-db
      path: .hypothesis/examples
  ```  
  In this workflow, we use dawidd6/action-download-artifact to download the latest artifact given that the official actions/download-artifact does not support downloading artifacts from previous workflow runs. The database automatically implements a simple file-based cache with a default expiration period of 1 day. You can adjust this through the `cache_timeout` property. For mono-repo support, you can provide a unique `artifact_name` (e.g. `hypofuzz-example-db-frontend`).

- `class hypothesis.database.ReadOnlyDatabase(db)[source]`  
  A wrapper to make the given database read-only. The implementation passes through `fetch`, and turns `save`, `delete`, and `move` into silent no-ops. Note that this disables Hypothesis’ automatic discarding of stale examples. It is designed to allow local machines to access a shared database (e.g. from CI servers), without propagating changes back from a local or in-development branch.

- `class hypothesis.database.MultiplexedDatabase(*dbs)[source]`  
  A wrapper around multiple databases. Each `save`, `fetch`, `move`, or `delete` operation will be run against all of the wrapped databases. `fetch` does not yield duplicate values, even if the same value is present in two or more of the wrapped databases. This combines well with a `ReadOnlyDatabase`, as follows:  
  ```python
  local = DirectoryBasedExampleDatabase("/tmp/hypothesis/examples/")
  shared = CustomNetworkDatabase()
  settings.register_profile("ci", database=shared)
  settings.register_profile(
      "dev", database=MultiplexedDatabase(local, ReadOnlyDatabase(shared))
  )
  settings.load_profile("ci" if os.environ.get("CI") else "dev")
  ```So your CI system or fuzzing runs can populate a central shared database; while local runs on development machines can reproduce any failures from CI but will only cache their own failures locally and cannot remove examples from the shared database.

- class hypothesis.database.BackgroundWriteDatabase(db)[source]¶  
  A wrapper which defers writes on the given database to a background thread.  
  Calls to `fetch()` wait for any enqueued writes to finish before fetching from the database.

- class hypothesis.extra.redis.RedisExampleDatabase(redis, *, expire_after=datetime.timedelta(days=8), key_prefix=b'hypothesis-example:', listener_channel='hypothesis-changes')  
  Store Hypothesis examples as sets in the given Redis datastore. This is particularly useful for shared databases, as per the recipe for a `MultiplexedDatabase`.

  **Note**  
  If a test has not been run for `expire_after`, those examples will be allowed to expire. The default time-to-live persists examples between weekly runs.

## Stateful tests

- class hypothesis.stateful.RuleBasedStateMachine[source]¶  
  A RuleBasedStateMachine gives you a structured way to define state machines.  
  The idea is that a state machine carries the system under test and some supporting data. This data can be stored in instance variables or divided into Bundles. The state machine has a set of rules which may read data from bundles (or just from normal strategies), push data onto bundles, change the state of the machine, or verify properties. At any given point a random applicable rule will be executed.

## Rules

- hypothesis.stateful.rule(*, targets=(), target=None, **kwargs)[source]¶  
  Decorator for RuleBasedStateMachine. Any Bundle present in `target` or `targets` will define where the end result of this function should go. If both are empty then the end result will be discarded. `target` must be a Bundle, or if the result should be replicated to multiple bundles you can pass a tuple of them as the `targets` argument. It is invalid to use both arguments for a single rule. If the result should go to exactly one of several bundles, define a separate rule for each case.  
  `kwargs` then define the arguments that will be passed to the function invocation. If their value is a Bundle, or if it is `consumes(b)` where `b` is a Bundle, then values that have previously been produced for that bundle will be provided. If `consumes` is used, the value will also be removed from the bundle. Any other kwargs should be strategies and values from them will be provided.

- hypothesis.stateful.consumes(bundle)[source]¶  
  When introducing a rule in a RuleBasedStateMachine, this function can be used to mark bundles from which each value used in a step with the given rule should be removed. This function returns a strategy object that can be manipulated and combined like any other.  
  For example, a rule declared with  
  `@rule(value1=b1, value2=consumes(b2), value3=lists(consumes(b3)))`  
  will consume a value from Bundle `b2` and several values from Bundle `b3` to populate `value2` and `value3` each time it is executed.

- hypothesis.stateful.multiple(*args)[source]¶  
  This function can be used to pass multiple results to the target(s) of a rule. Just use `return multiple(result1, result2, ...)` in your rule.  
  It is also possible to use `return multiple()` with no arguments in order to end a rule without passing any result.

- class hypothesis.stateful.Bundle(name, *, consume=False, draw_references=True)[source]¶  
  A collection of values for use in stateful testing.  
  Bundles are a kind of strategy where values can be added by rules, and (like any strategy) used as inputs to future rules.  
  The `name` argument they are passed is the name they are referred to internally by the state machine; no two bundles may have the same name. It is idiomatic to use the attribute being assigned to as the name of the Bundle:  
  ```python
  class MyStateMachine(RuleBasedStateMachine):
      keys = Bundle("keys")
  ```  
  Bundles can contain the same value more than once; this becomes relevant when using `consumes()` to remove values again.  
  If the `consume` argument is set to True, then all values that are drawn from this bundle will be consumed (as above) when requested.

- hypothesis.stateful.initialize(*, targets=(), target=None, **kwargs)[source]¶  
  Decorator for RuleBasedStateMachine.  
  An initialize decorator behaves like a rule, but all `@initialize()` decorated methods will be called before any `@rule()` decorated methods, in an arbitrary order. Each `@initialize()` method will be called exactly once per run, unless one raises an exception – after which only the `.teardown()` method will be run. `@initialize()` methods may not have preconditions.

- hypothesis.stateful.precondition(precond)[source]¶  
  Decorator to apply a precondition for rules in a RuleBasedStateMachine. Specifies a precondition for a rule to be considered as a valid step in the state machine, which is more efficient than using `assume()` within the rule. The `precond` function will be called with the instance of RuleBasedStateMachine and should return True or False. Usually it will need to look at attributes on that instance.  
  For example:
  ```python
  class MyTestMachine(RuleBasedStateMachine):
      state = 1

      @precondition(lambda self: self.state != 0)
      @rule(numerator=integers())
      def divide_with(self, numerator):
          self.state = numerator / self.state
  ```  
  If multiple preconditions are applied to a single rule, it is only considered a valid step when all of them return True. Preconditions may be applied to invariants as well as rules.

- hypothesis.stateful.invariant(*, check_during_init=False)[source]¶  
  Decorator to apply an invariant for rules in a RuleBasedStateMachine. The decorated function will be run after every rule and can raise an exception to indicate failed invariants.  
  For example:
  ```python
  class MyTestMachine(RuleBasedStateMachine):
      state = 1

      @invariant()
      def is_nonzero(self):
          assert self.state != 0
  ```  
  By default, invariants are only checked after all `@initialize()` rules have been run. Pass `check_during_init=True` for invariants which can also be checked during initialization.

## Running state machines

If you want to bypass the TestCase infrastructure you can invoke these manually. The stateful module exposes `run_state_machine_as_test()`, which takes an arbitrary function returning a `RuleBasedStateMachine` and an optional settings parameter and does the same as the class based `runTest` provided.

- hypothesis.stateful.run_state_machine_as_test(state_machine_factory, *, settings=None, _min_steps=0)  
  Run a state machine definition as a test, either silently doing nothing or printing a minimal breaking program and raising an exception.  
  `state_machine_factory` is anything which returns an instance of `RuleBasedStateMachine` when called with no arguments – it can be a class or a function. `settings` will be used to control the execution of the test.

## Hypothesis exceptions

Custom exceptions raised by Hypothesis.

- class hypothesis.errors.HypothesisException[source]¶  
  Generic parent class for exceptions thrown by Hypothesis.

- class hypothesis.errors.HypothesisDeprecationWarning[source]¶  
  A deprecation warning issued by Hypothesis.  
  Actually inherits from FutureWarning, because DeprecationWarning is hidden by the default warnings filter.  
  You can configure the `warnings` module to handle these warnings differently to others, either turning them into errors or suppressing them entirely. Obviously we would prefer the former!

- class hypothesis.errors.Flaky[source]¶  
  Base class for indeterministic failures. Usually one of the more specific subclasses (`FlakyFailure` or `FlakyStrategyDefinition`) is raised.  
  See also the flaky failures tutorial.

- class hypothesis.errors.FlakyStrategyDefinition[source]¶  
  This function appears to cause inconsistent data generation.  
  **Common causes for this problem are:**  
  - The strategy depends on external state. e.g. it uses an external random number generator. Try to make a version that passes all the relevant state in from Hypothesis.  
  See also the flaky failures tutorial.

- class hypothesis.errors.FlakyFailure(msg, group)[source]¶  
  This function appears to fail non-deterministically: We have seen it fail when passed this example at least once, but a subsequent invocation did not fail, or caused a distinct error.  
  **Common causes for this problem are:**  
  - The function depends on external state. e.g. it uses an external random number generator. Try to make a version that passes all the relevant state in from Hypothesis.  
  - The function is suffering from too much recursion and its failure depends sensitively on where it’s been called from.  
  - The function is timing sensitive and can fail or pass depending on how long it takes. Try breaking it up into smaller functions which don’t do that and testing those instead.  
  See also the flaky failures tutorial.

- class hypothesis.errors.FlakyBackendFailure(msg, group)[source]¶  
  A failure was reported by an alternative backend, but this failure did not reproduce when replayed under the Hypothesis backend.  
  When an alternative backend reports a failure, Hypothesis first replays it under the standard Hypothesis backend to check for flakiness. If the failure does not reproduce, Hypothesis raises this exception.

- class hypothesis.errors.InvalidArgument[source]¶  
  Used to indicate that the arguments to a Hypothesis function were in some manner incorrect.

- class hypothesis.errors.ResolutionFailed[source]¶  
  Hypothesis had to resolve a type to a strategy, but this failed.  
  Type inference is best-effort, so this only happens when an annotation exists but could not be resolved for a required argument to the target of `builds()`, or where the user passed...

- class hypothesis.errors.Unsatisfiable[source]¶  
  We ran out of time or examples before we could find enough examples which satisfy the assumptions of this hypothesis.This could be because the function is too slow. If so, try upping the timeout. It could also be because the function is using `assume` in a way that is too hard to satisfy. If so, try writing a custom strategy or using a better starting point (e.g. if you are requiring a list has unique values you could instead filter out all duplicate values from the list).

- class hypothesis.errors.DeadlineExceeded(runtime, deadline)[source]¶  
  Raised when an input takes too long to run, relative to the `settings.deadline` setting.

## Django

See also  
[See the Django strategies reference](hypothesis.extra.django) for documentation on strategies in the `hypothesis.extra.django` module.

Hypothesis offers a number of features specific for Django testing, available in the `hypothesis[django]` extra. This is tested against each supported series with mainstream or extended support—if you’re still getting security patches, you can test with Hypothesis.

Using it is quite straightforward: All you need to do is subclass `hypothesis.extra.django.TestCase`, `hypothesis.extra.django.SimpleTestCase`, `hypothesis.extra.django.TransactionTestCase`, `LiveServerTestCase`, or `StaticLiveServerTestCase`, and you can use `@given` as normal, and the transactions will be per example rather than per test function as they would be if you used `@given` with a normal Django test suite (this is important because your test function will be called multiple times and you don’t want them to interfere with each other). Test cases on these classes that do not use `@given` will be run as normal for `django.test.TestCase` or `django.test.TransactionTestCase`.

We recommend avoiding `TransactionTestCase` unless you really have to run each test case in a database transaction. Because Hypothesis runs this in a loop, the performance problems `django.test.TransactionTestCase` normally has are significantly exacerbated and your tests will be really slow. If you are using `TransactionTestCase`, you may need to use `@settings(suppress_health_check=[HealthCheck.too_slow])` to avoid a `HealthCheck` error due to slow example generation.

Having set up a test class, you can now pass `@given` a strategy for Django models with `from_model()`.

For example, using the trivial django project we have for testing:
```python
>>> from hypothesis.extra.django import from_model
>>> from toystore.models import Customer
>>> c = from_model(Customer).example()
>>> c
<Customer: Customer object>
>>> c.email
'jaime.urbina@gmail.com'
>>> c.name
'\U00109d3d\U000e07be\U000165f8\U0003fabf\U000c12cd\U000f1910\U00059f12\U000519b0\U0003fabf\U000f1910\U000423fb\U000423fb\U00059f12\U000e07be\U000c12cd\U000e07be\U000519b0\U000165f8\U0003fabf\U0007bc31'
>>> c.age
-873375803
```
Hypothesis has just created this with whatever the relevant type of data is. Obviously the customer’s age is implausible, which is only possible because we have not used (e.g.) `MinValueValidator` to set the valid range for this field (or used a `PositiveSmallIntegerField`, which would only need a maximum value validator).

If you do have validators attached, Hypothesis will only generate examples that pass validation. Sometimes that will mean that we fail a `HealthCheck` because of the filtering, so let’s explicitly pass a strategy to skip validation at the strategy level:

## Custom field types

If you have a custom Django field type you can register it with Hypothesis’s model deriving functionality by registering a default strategy for it:
```python
>>> from toystore.models import CustomishField, Customish
>>> from_model(Customish).example()
hypothesis.errors.InvalidArgument: Missing arguments for mandatory field customish for model Customish
>>> from hypothesis.extra.django import register_field_strategy
>>> from hypothesis.strategies import just
>>> register_field_strategy(CustomishField, just("hi"))
>>> x = from_model(Customish).example()
>>> x.customish
'hi'
```
Note that this mapping is on exact type. Subtypes will not inherit it.

## Generating child models

For the moment there’s no explicit support in hypothesis-django for generating dependent models. i.e. a Company model will generate no Shops. However if you want to generate some dependent models as well, you can emulate this by using the `.flatmap()` function as follows:

Let’s unpack what this is doing:  
The way `flatmap` works is that we draw a value from the original strategy, then apply a function to it which gives us a new strategy. We then draw a value from that strategy. So in this case we’re first drawing a company, and then we’re drawing a list of shops belonging to that company: The `just()` strategy is a strategy such that drawing it always produces the individual value, so `from_model(Shop, company=just(company))` is a strategy that generates a Shop belonging to the original company.

So the following code would give us a list of shops all belonging to the same company:

The only difference from this and the above is that we want the company, not the shops. This is where the inner map comes in. We build the list of shops and then throw it away, instead returning the company we started for. This works because the models that Hypothesis generates are saved in the database, so we’re essentially running the inner strategy purely for the side effect of creating those children in the database.

## Generating primary key values

If your model includes a custom primary key that you want to generate using a strategy (rather than a default auto-increment primary key) then Hypothesis has to deal with the possibility of a duplicate primary key.

If a model strategy generates a value for the primary key field, Hypothesis will create the model instance with `update_or_create()`, overwriting any existing instance in the database for this test case with the same primary key.

## On the subject of MultiValueField

Django forms feature the `MultiValueField` which allows for several fields to be combined under a single named field, the default example of this is the `SplitDateTimeField`.

```python
class CustomerForm(forms.Form):
    name = forms.CharField()
    birth_date_time = forms.SplitDateTimeField()
```

`from_form()` supports `MultiValueField` subclasses directly, however if you want to define your own strategy be forewarned that Django binds data for a `MultiValueField` in a peculiar way. Specifically each sub-field is expected to have its own entry in `data` addressed by the field name (e.g. `birth_date_time`) and the index of the sub-field within the `MultiValueField`, so form data for the example above might look like this:
```python
{
    "name": "Samuel John",
    "birth_date_time_0": "2018-05-19",  # the date, as the first sub-field
    "birth_date_time_1": "15:18:00",   # the time, as the second sub-field
}
```
Thus, if you want to define your own strategies for such a field you must address your sub-fields appropriately:
```python
from_form(CustomerForm, birth_date_time_0=just("2018-05-19"))
```

## External fuzzers

- hypothesis.core.HypothesisHandle.fuzz_one_input = <property object>¶  
  Run the test as a fuzz target, driven with the `buffer` of bytes.

Depending on the passed `buffer` one of three things will happen:
- If the bytestring was invalid, for example because it was too short or was filtered out by `assume()` or `.filter()`, `fuzz_one_input()` returns `None`.
- If the bytestring was valid and the test passed, `fuzz_one_input()` returns a canonicalised and pruned bytestring which will replay that test case. This is provided as an option to improve the performance of mutating fuzzers, but can safely be ignored.
- If the test failed, i.e. raised an exception, `fuzz_one_input()` will add the pruned buffer to the Hypothesis example database and then re-raise that exception. All you need to do to reproduce, minimize, and de-duplicate all the failures found via fuzzing is run your test suite!

To reduce the performance impact of database writes, `fuzz_one_input()` only records failing inputs which would be valid shrinks for a known failure—meaning writes are somewhere between constant and log(N) rather than linear in runtime. However, this tracking only works within a persistent fuzzing process; for forkserver fuzzers we recommend `database=None` for the main run, and then replaying with a database enabled if you need to analyse failures.

Note that the interpretation of both input and output bytestrings is specific to the exact version of Hypothesis you are using and the strategies given to the test, just like the database and `@reproduce_failure`.

## Interaction with `@settings`

`fuzz_one_input()` uses just enough of Hypothesis’ internals to drive your test function with a bytestring, and most settings therefore have no effect in this mode. We recommend running your tests the usual way before fuzzing to get the benefits of health checks, as well as afterwards to replay, shrink, deduplicate, and report whatever errors were discovered.

- `settings.database` is used by `fuzz_one_input()`—adding failures to the database to be replayed when you next run your tests is our preferred reporting mechanism and response to the ‘fuzzer taming’ problem.
- `settings.verbosity` and `settings.stateful_step_count` work as usual.
- The `deadline`, `derandomize`, `max_examples`, `phases`, `print_blob`, `report_multiple_bugs`, and `suppress_health_check` settings do not affect `fuzz_one_input()`.

## Example Usage

```python
@given(st.text())
def test_foo(s):
    ...

# This is a traditional fuzz target - call it with a bytestring,
# or a binary IO object, and it runs the test once.
fuzz_target = test_foo.hypothesis.fuzz_one_input

# For example:
fuzz_target(b"\x00\x00\x00\x00\x00\x00\x00\x00")
fuzz_target(io.BytesIO(b"\x01"))
```

**Tip**  
If you expect to discover many failures while using `fuzz_one_input()`, consider wrapping your database with `BackgroundWriteDatabase`, for low-overhead writes of failures.

**Tip**  
Want an integrated workflow for your team’s local tests, CI, and continuous fuzzing? Use [HypoFuzz](https://hypofuzz.com/) to fuzz your whole test suite, and find more bugs with the same tests!

See also  
[See also the Use Hypothesis with an external fuzzer how-to.](https://hypothesis.readthedocs.io/en/latest/how-to-guides.html#use-hypothesis-with-an-external-fuzzer)

## Custom function execution

Hypothesis provides you with a hook that lets you control how it runs examples.This lets you do things like set up and tear down around each example, run examples in a subprocess, transform coroutine tests into normal tests, etc. For example, `TransactionTestCase` in the Django extra runs each example in a separate database transaction.

The way this works is by introducing the concept of an executor. An executor is essentially a function that takes a block of code and runs it. The default executor is:

```python
def default_executor(function):
    return function()
```

You define executors by defining a method `execute_example` on a class. Any test methods on that class with `@given` used on them will use `self.execute_example` as an executor with which to run tests. For example, the following executor runs all its code twice:

> **Note:** The functions you use in `map`, etc. will run inside the executor. i.e. they will not be called until you invoke the function passed to `execute_example`.

An executor must be able to handle being passed a function which returns `None`, otherwise it won’t be able to run normal test cases. So for example the following executor is invalid:

```python
from unittest import TestCase

class TestRunTwice(TestCase):
    def execute_example(self, f):
        return f()()
```

and should be rewritten as:

An alternative hook is provided for use by test runner extensions such as `pytest-trio`, which cannot use the `execute_example` method. This is not recommended for end-users—it is better to write a complete test function directly, perhaps by using a decorator to perform the same transformation before applying `@given`.

For authors of test runners however, assigning to the `inner_test` attribute of the `hypothesis` attribute of the test will replace the interior test.

> **Note:** The new `inner_test` must accept and pass through all the `*args` and `**kwargs` expected by the original test.
>
> If the end user has also specified a custom executor using the `execute_example` method, it—and all other execution-time logic—will be applied to the new inner test assigned by the test runner.

## Detection

- `hypothesis.is_hypothesis_test(f)`[[source]](source)
  
  Returns `True` iff `f` represents a test function that has been defined with Hypothesis. This is true for:
  
  - Functions decorated with `@given`
  - The `runTest` method of stateful tests
  
  For example:
  
  ```python
  @given(st.integers())
  def f(n): ...
  
  class MyStateMachine(RuleBasedStateMachine): ...
  
  assert is_hypothesis_test(f)
  assert is_hypothesis_test(MyStateMachine.TestCase().runTest)
  ```
  
  See also [Detect Hypothesis tests how-to](#).

- `hypothesis.currently_in_test_context()`[[source]](source)
  
  Return `True` if the calling code is currently running inside an `@given` or stateful test, and `False` otherwise.
  
  This is useful for third-party integrations and assertion helpers which may be called from either traditional or property-based tests, and can only use e.g. `assume()` or `target()` in the latter case.