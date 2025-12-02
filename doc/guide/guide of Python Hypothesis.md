      Hypothesis 6.148.5 documentation         body { --color-code-background: #eeffcc; --color-code-foreground: black; } @media not print { body\[data-theme="dark"\] { --color-code-background: #202020; --color-code-foreground: #d0d0d0; } @media (prefers-color-scheme: dark) { body:not(\[data-theme="light"\]) { --color-code-background: #202020; --color-code-foreground: #d0d0d0; } } } document.body.dataset.theme = localStorage.getItem("theme") || "auto"; Contents Menu Expand Light mode Dark mode Auto light/dark, in light mode Auto light/dark, in dark mode   [Skip to content](#furo-main-content)

[

Hypothesis

](#)

[

![Logo](_static/dragonfly-rainbow-150w.svg)

](#)

  

*   [Quickstart](#document-quickstart)
*   [Tutorial](#document-tutorial/index)
    *   [Introduction to Hypothesis](#document-tutorial/introduction)
    *   [Built-in strategies](#document-tutorial/builtin-strategies)
    *   [Adapting strategies](#document-tutorial/adapting-strategies)
    *   [Custom strategies](#document-tutorial/custom-strategies)
    *   [Configuring test settings](#document-tutorial/settings)
    *   [Replaying failed tests](#document-tutorial/replaying-failures)
    *   [Adding notes](#document-tutorial/adding-notes)
    *   [Flaky failures](#document-tutorial/flaky)
*   [How-to guides](#document-how-to/index)
    *   [Suppress a health check everywhere](#document-how-to/suppress-healthchecks)
    *   [Write type hints for strategies](#document-how-to/type-strategies)
    *   [Write a custom Hypothesis database](#document-how-to/custom-database)
    *   [Detect Hypothesis tests](#document-how-to/detect-hypothesis-tests)
    *   [Use Hypothesis with an external fuzzer](#document-how-to/external-fuzzers)
*   [Explanations](#document-explanation/index)
    *   [Domain and distribution](#document-explanation/domain)
    *   [How many times will Hypothesis run my test?](#document-explanation/example-count)
*   [API Reference](#document-reference/index)
    *   [API Reference](#document-reference/api)
    *   [Strategies Reference](#document-reference/strategies)
    *   [Integrations Reference](#document-reference/integrations)
    *   [Hypothesis internals](#document-reference/internals)
*   [Stateful tests](#document-stateful)
*   [Extras](#document-extras)
*   [Changelog](#document-changelog)

About Hypothesis

*   [Hypothesis development](#document-development)
*   [Compatibility](#document-compatibility)
*   [Projects using Hypothesis](#document-usage)
*   [Third-party extensions](#document-extensions)
*   [Packaging guidelines](#document-packaging)
*   [Community](#document-community)

[Back to top](#)

.row { clear: both; } .column img {border: 1px solid gray;} @media only screen and (min-width: 1000px) { .column { padding-left: 5px; padding-right: 5px; float: left; } .column2 { width: calc(50% - 11px); position: relative; } .column2:before { padding-top: 61.8%; content: ""; display: block; float: left; } .top-left { border-right: 1px solid var(--color-background-border); border-bottom: 1px solid var(--color-background-border); } .top-right { border-bottom: 1px solid var(--color-background-border); } .bottom-left { border-right: 1px solid var(--color-background-border); } }

Welcome to Hypothesis![¶](#welcome-to-hypothesis "Link to this heading")
========================================================================

Hypothesis is the property-based testing library for Python. With Hypothesis, you write tests which should pass for all inputs in whatever range you describe, and let Hypothesis randomly choose which of those inputs to check - including edge cases you might not have thought about. For example:

from hypothesis import given, strategies as st

@given(st.lists(st.integers() | st.floats()))
def test\_sort\_correctness\_using\_properties(lst):
    result \= my\_sort(lst)
    assert set(lst) \== set(result)
    assert all(a <= b for a, b in zip(result, result\[1:\]))

You should start with the [tutorial](#document-tutorial/index), or alternatively the more condensed [quickstart](#document-quickstart).

[Tutorial](#document-tutorial/index)[¶](#tutorial "Link to this heading")
-------------------------------------------------------------------------

An introduction to Hypothesis.

New users should start here, or with the more condensed [quickstart](#document-quickstart).

[How-to guides](#document-how-to/index)[¶](#how-to-guides "Link to this heading")
---------------------------------------------------------------------------------

Practical guides for applying Hypothesis in specific scenarios.

[Explanations](#document-explanation/index)[¶](#explanations "Link to this heading")
------------------------------------------------------------------------------------

Commentary oriented towards deepening your understanding of Hypothesis.

[API Reference](#document-reference/index)[¶](#api-reference "Link to this heading")
------------------------------------------------------------------------------------

Technical API reference.

### Quickstart[¶](#quickstart "Link to this heading")

This is a lightning introduction to the most important features of Hypothesis; enough to get you started writing tests. The [tutorial](#document-tutorial/index) introduces these features (and more) in greater detail.

#### Install Hypothesis[¶](#install-hypothesis "Link to this heading")

pip install hypothesis

#### Write your first test[¶](#write-your-first-test "Link to this heading")

Create a new file called `example.py`, containing a simple test:

\# contents of example.py
from hypothesis import given, strategies as st

@given(st.integers())
def test\_integers(n):
    print(f"called with {n}")
    assert isinstance(n, int)

test\_integers()

[`@given`](#hypothesis.given "hypothesis.given") is the standard entrypoint to Hypothesis. It takes a _strategy_, which describes the type of inputs you want the decorated function to accept. When we call `test_integers`, Hypothesis will generate random integers (because we used the [`integers()`](#hypothesis.strategies.integers "hypothesis.strategies.integers") strategy) and pass them as `n`. Let’s see that in action now by running `python example.py`:

called with 0
called with -18588
called with -672780074
called with 32616
...

We just called `test_integers()`, without passing a value for `n`, because Hypothesis generates random values of `n` for us.

Note

By default, Hypothesis generates 100 random inputs. You can control this with the [`max_examples`](#hypothesis.settings.max_examples "hypothesis.settings.max_examples") setting.

#### Running in a test suite[¶](#running-in-a-test-suite "Link to this heading")

A Hypothesis test is still a regular python function, which means pytest or unittest will pick it up and run it in all the normal ways.

\# contents of example.py
from hypothesis import given, strategies as st

@given(st.integers(0, 200))
def test\_integers(n):
    assert n < 50

This test will clearly fail, which can be confirmed by running `pytest example.py`:

$ pytest example.py

    ...

    @given(st.integers())
    def test\_integers(n):
>       assert n < 50
E       assert 50 < 50
E       Falsifying example: test\_integers(
E           n=50,
E       )

#### Arguments to [`@given`](#hypothesis.given "hypothesis.given")[¶](#arguments-to-given "Link to this heading")

You can pass multiple arguments to [`@given`](#hypothesis.given "hypothesis.given"):

@given(st.integers(), st.text())
def test\_integers(n, s):
    assert isinstance(n, int)
    assert isinstance(s, str)

Or use keyword arguments:

@given(n\=st.integers(), s\=st.text())
def test\_integers(n, s):
    assert isinstance(n, int)
    assert isinstance(s, str)

Note

See [`@given`](#hypothesis.given "hypothesis.given") for details about how [`@given`](#hypothesis.given "hypothesis.given") handles different types of arguments.

#### Filtering inside a test[¶](#filtering-inside-a-test "Link to this heading")

Sometimes, you need to remove invalid cases from your test. The best way to do this is with [`.filter()`](#hypothesis.strategies.SearchStrategy.filter "hypothesis.strategies.SearchStrategy.filter"):

@given(st.integers().filter(lambda n: n % 2 \== 0))
def test\_integers(n):
    assert n % 2 \== 0

For more complicated conditions, you can use [`assume()`](#hypothesis.assume "hypothesis.assume"), which tells Hypothesis to discard any test case with a false-y argument:

@given(st.integers(), st.integers())
def test\_integers(n1, n2):
    assume(n1 != n2)
    \# n1 and n2 are guaranteed to be different here

Note

You can learn more about [`.filter()`](#hypothesis.strategies.SearchStrategy.filter "hypothesis.strategies.SearchStrategy.filter") and [`assume()`](#hypothesis.assume "hypothesis.assume") in the [Adapting strategies](#document-tutorial/adapting-strategies) tutorial page.

#### Dependent generation[¶](#dependent-generation "Link to this heading")

You may want an input to depend on the value of another input. For instance, you might want to generate two integers `n1` and `n2` where `n1 <= n2`.

You can do this using the [`@composite`](#hypothesis.strategies.composite "hypothesis.strategies.composite") strategy. [`@composite`](#hypothesis.strategies.composite "hypothesis.strategies.composite") lets you define a new strategy which is itself built by drawing values from other strategies, using the automatically-passed `draw` function.

@st.composite
def ordered\_pairs(draw):
    n1 \= draw(st.integers())
    n2 \= draw(st.integers(min\_value\=n1))
    return (n1, n2)

@given(ordered\_pairs())
def test\_pairs\_are\_ordered(pair):
    n1, n2 \= pair
    assert n1 <= n2

In more complex cases, you might need to interleave generation and test code. In this case, use [`data()`](#hypothesis.strategies.data "hypothesis.strategies.data").

@given(st.data(), st.text(min\_size\=1))
def test\_string\_characters\_are\_substrings(data, string):
    assert isinstance(string, str)
    index \= data.draw(st.integers(0, len(string) \- 1))
    assert string\[index\] in string

#### Combining Hypothesis with pytest[¶](#combining-hypothesis-with-pytest "Link to this heading")

Hypothesis works with pytest features, like [pytest.mark.parametrize](https://docs.pytest.org/en/stable/reference/reference.html#pytest-mark-parametrize-ref "(in pytest v9.0.1)"):

import pytest

from hypothesis import given, strategies as st

@pytest.mark.parametrize("operation", \[reversed, sorted\])
@given(st.lists(st.integers()))
def test\_list\_operation\_preserves\_length(operation, lst):
    assert len(lst) \== len(list(operation(lst)))

Hypothesis also works with pytest fixtures:

import pytest

@pytest.fixture(scope\="session")
def shared\_mapping():
    return {n: 0 for n in range(101)}

@given(st.integers(0, 100))
def test\_shared\_mapping\_keys(shared\_mapping, n):
    assert n in shared\_mapping

### Tutorial[¶](#tutorial "Link to this heading")

The Hypothesis tutorial introduces the main features of Hypothesis. We suggest reading through in order until completing [Custom strategies](#document-tutorial/custom-strategies), at which point you can choose to read what seems interesting to you.

If you’re in a hurry, the [quickstart](#document-quickstart) is a much faster bare-bones version.

#### Introduction to Hypothesis[¶](#introduction-to-hypothesis "Link to this heading")

This page introduces two fundamental parts of Hypothesis ([`@given`](#hypothesis.given "hypothesis.given"), and strategies) and shows how to test a selection sort implementation using Hypothesis.

##### Install Hypothesis[¶](#install-hypothesis "Link to this heading")

First, let’s install Hypothesis:

pip install hypothesis

##### Defining a simple test[¶](#defining-a-simple-test "Link to this heading")

Hypothesis tests are defined using two things; [`@given`](#hypothesis.given "hypothesis.given"), and a _strategy_, which is passed to [`@given`](#hypothesis.given "hypothesis.given"). Here’s a simple example:

from hypothesis import given, strategies as st

@given(st.integers())
def test\_is\_integer(n):
    assert isinstance(n, int)

Adding the [`@given`](#hypothesis.given "hypothesis.given") decorator turns this function into a Hypothesis test. Passing [`integers()`](#hypothesis.strategies.integers "hypothesis.strategies.integers") to [`@given`](#hypothesis.given "hypothesis.given") says that Hypothesis should generate random integers for the argument `n` when testing.

We can run this test by calling it:

from hypothesis import given, strategies as st

@given(st.integers())
def test\_is\_integer(n):
    print(f"called with {n}")
    assert isinstance(n, int)

test\_is\_integer()

Note that we don’t pass anything for `n`; Hypothesis handles generating that value for us. The resulting output looks like this:

called with 0
called with -18588
called with -672780074
called with 32616
...

##### Testing a sorting algorithm[¶](#testing-a-sorting-algorithm "Link to this heading")

Suppose we have implemented a simple selection sort:

\# contents of example.py
from hypothesis import given, strategies as st

def selection\_sort(lst):
    result \= \[\]
    while lst:
        smallest \= min(lst)
        result.append(smallest)
        lst.remove(smallest)
    return result

and want to make sure it’s correct. We can write the following test by combining the [`integers()`](#hypothesis.strategies.integers "hypothesis.strategies.integers") and [`lists()`](#hypothesis.strategies.lists "hypothesis.strategies.lists") strategies:

...

@given(st.lists(st.integers()))
def test\_sort\_correct(lst):
    print(f"called with {lst}")
    assert selection\_sort(lst.copy()) \== sorted(lst)

test\_sort\_correct()

When running `test_sort_correct`, Hypothesis uses the `lists(integers())` strategy to generate random lists of integers. Feel free to run `python example.py` to get an idea of the kinds of lists Hypothesis generates (and to convince yourself that this test passes).

###### Adding floats to our test[¶](#adding-floats-to-our-test "Link to this heading")

This test is a good start. But `selection_sort` should be able to sort lists with floats, too. If we wanted to generate lists of either integers or floats, we can change our strategy:

\# changes to example.py
@given(st.lists(st.integers() | st.floats()))
def test\_sort\_correct(lst):
    pass

The pipe operator `|` takes two strategies, and returns a new strategy which generates values from either of its strategies. So the strategy `integers() | floats()` can generate either an integer, or a float.

Note

`strategy1 | strategy2` is equivalent to [`st.one_of(strategy1, strategy2)`](#hypothesis.strategies.one_of "hypothesis.strategies.one_of").

###### Preventing [`floats()`](#hypothesis.strategies.floats "hypothesis.strategies.floats") from generating `nan`[¶](#preventing-st-floats-from-generating-nan "Link to this heading")

Even though `test_sort_correct` passed when we used lists of integers, it actually fails now that we’ve added floats! If you run `python example.py`, you’ll likely (but not always; this is random testing, after all) find that Hypothesis reports a counterexample to `test_sort_correct`. For me, that counterexample is `[1.0, nan, 0]`. It might be different for you.

The issue is that sorting in the presence of `nan` is not well defined. As a result, we may decide that we don’t want to generate them while testing. We can pass `floats(allow_nan=False)` to tell Hypothesis not to generate `nan`:

\# changes to example.py
@given(st.lists(st.integers() | st.floats(allow\_nan\=False)))
def test\_sort\_correct(lst):
    pass

And now this test passes without issues.

Note

You can use the [`.example()`](#hypothesis.strategies.SearchStrategy.example "hypothesis.strategies.SearchStrategy.example") method to get an idea of the kinds of things a strategy will generate:

\>>> st.lists(st.integers() | st.floats(allow\_nan\=False)).example()
\[-5.969063e-08, 15283673678, 18717, -inf\]

Note that [`.example()`](#hypothesis.strategies.SearchStrategy.example "hypothesis.strategies.SearchStrategy.example") is intended for interactive use only (i.e., in a [REPL](https://docs.python.org/3/glossary.html#term-REPL "(in Python v3.14)")). It is not intended to be used inside tests.

##### Tests with multiple arguments[¶](#tests-with-multiple-arguments "Link to this heading")

If we wanted to pass multiple arguments to a test, we can do this by passing multiple strategies to [`@given`](#hypothesis.given "hypothesis.given"):

from hypothesis import given, strategies as st

@given(st.integers(), st.lists(st.floats()))
def test\_multiple\_arguments(n, lst):
    assert isinstance(n, int)
    assert isinstance(lst, list)
    for f in lst:
        assert isinstance(f, float)

###### Keyword arguments[¶](#keyword-arguments "Link to this heading")

We can also pass strategies using keyword arguments:

@given(lst\=st.lists(st.floats()), n\=st.integers())  \#  <-- changed
def test\_multiple\_arguments(n, lst):
    pass

Note that even though we changed the order the parameters to [`@given`](#hypothesis.given "hypothesis.given") appear, we also explicitly told it which parameters to pass to by using keyword arguments, so the meaning of the test hasn’t changed.

In general, you can think of positional and keyword arguments to [`@given`](#hypothesis.given "hypothesis.given") as being forwarded to the test arguments.

Note

One exception is that [`@given`](#hypothesis.given "hypothesis.given") does not support mixing positional and keyword arguments. See the [`@given`](#hypothesis.given "hypothesis.given") documentation for more about how it handles arguments.

##### Running Hypothesis tests[¶](#running-hypothesis-tests "Link to this heading")

There are a few ways to run a Hypothesis test.

*   Explicitly call it, like `test_is_integer()`, as we’ve seen. Hypothesis tests are just normal functions, except [`@given`](#hypothesis.given "hypothesis.given") handles generating and passing values for the function arguments.
    
*   Let a test runner such as [pytest](https://pypi.org/project/pytest/) pick up on it (as long as the function name starts with `test_`).
    

Concretely, when running a Hypothesis test, Hypothesis will:

*   generate 100 random inputs,
    
*   run the body of the function for each input, and
    
*   report any exceptions that get raised.
    

Note

The number of examples can be controlled with the [`max_examples`](#hypothesis.settings.max_examples "hypothesis.settings.max_examples") setting. The default is 100.

##### When to use Hypothesis and property-based testing[¶](#when-to-use-hypothesis-and-property-based-testing "Link to this heading")

Property-based testing is a powerful _addition_ to unit testing. It is not always a replacement.

If you’re having trouble coming up with a property in your code to test, we recommend trying the following:

*   Look for round-trip properties: encode/decode, serialize/deserialize, etc. These property-based tests tend to be both powerful and easy to write.
    
*   Look for `@pytest.mark.parametrize` in your existing tests. This is sometimes a good hint you can replace the parametrization with a strategy. For instance, `@pytest.mark.parametrize("n", range(0, 100))` could be replaced by `@given(st.integers(0, 100 - 1))`.
    
*   Simply call your code with random inputs (of the correct shape) from Hypothesis! You might be surprised how often this finds crashes. This can be especially valuable for projects with a single entrypoint interface to a lot of underlying code.
    

Other examples of properties include:

*   An optimized implementation is equivalent to a slower, but clearly correct, implementation.
    
*   A sequence of transactions in a financial system always “balances”; money never gets lost.
    
*   The derivative of a polynomial of order `n` has order `n - 1`.
    
*   A type-checker, linter, formatter, or compiler does not crash when called on syntactically valid code.
    
*   [And more](https://fsharpforfunandprofit.com/posts/property-based-testing-2/).
    

#### Built-in strategies[¶](#built-in-strategies "Link to this heading")

This page shows some of the strategies that Hypothesis provides for you.

##### Strategies provided by Hypothesis[¶](#strategies-provided-by-hypothesis "Link to this heading")

Here is a selection of strategies provided by Hypothesis that may be useful to know:

[`integers()`](#hypothesis.strategies.integers "hypothesis.strategies.integers")

Generates integers.

[`floats()`](#hypothesis.strategies.floats "hypothesis.strategies.floats")

Generates floats.

[`booleans()`](#hypothesis.strategies.booleans "hypothesis.strategies.booleans")

Generates booleans.

[`text()`](#hypothesis.strategies.text "hypothesis.strategies.text")

Generates unicode strings (i.e., instances of [`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.14)")). Can be constrained to ASCII with `st.text(st.characters(codec="ascii"))`.

[`lists()`](#hypothesis.strategies.lists "hypothesis.strategies.lists")

Generates lists with elements from the strategy passed to it. `st.lists(st.integers())` generates lists of integers.

[`tuples()`](#hypothesis.strategies.tuples "hypothesis.strategies.tuples")

Generates tuples of a fixed length. `st.tuples(st.integers(), st.floats())` generates tuples with two elements, where the first element is an integer and the second is a float.

[`one_of()`](#hypothesis.strategies.one_of "hypothesis.strategies.one_of")

Generates from any of the strategies passed to it. `st.one_of(st.integers(), st.floats())` generates either integers or floats. You can also use `|` to construct [`one_of()`](#hypothesis.strategies.one_of "hypothesis.strategies.one_of"), like `st.integers() | st.floats()`.

[`builds()`](#hypothesis.strategies.builds "hypothesis.strategies.builds")

Generates instances of a class (or other callable) by specifying a strategy for each argument, like `st.builds(Person, name=st.text(), age=st.integers())`.

[`just()`](#hypothesis.strategies.just "hypothesis.strategies.just")

Generates the exact value passed to it. `st.just("a")` generates the exact string `"a"`. This is useful when something expects to be passed a strategy. For instance, `st.lists(st.integers() | st.just("a"))` generates lists whose elements are either integers or the string `"a"`.

[`sampled_from()`](#hypothesis.strategies.sampled_from "hypothesis.strategies.sampled_from")

Generates a random value from a list. `st.sampled_from(["a", 1])` is roughly equivalent to `st.just("a") | st.just(1)`.

[`none()`](#hypothesis.strategies.none "hypothesis.strategies.none")

Generates `None`. Useful for parameters that can be optional, like `st.integers() | st.none()`.

See also

See the [strategies API reference](#document-reference/strategies) for a full list of strategies provided by Hypothesis.

#### Adapting strategies[¶](#adapting-strategies "Link to this heading")

This page discusses ways to adapt strategies to your needs, either by transforming them inline with [`.map()`](#hypothesis.strategies.SearchStrategy.map "hypothesis.strategies.SearchStrategy.map"), or filtering out unwanted inputs with [`.filter()`](#hypothesis.strategies.SearchStrategy.filter "hypothesis.strategies.SearchStrategy.filter") and [`assume()`](#hypothesis.assume "hypothesis.assume").

##### Mapping strategy inputs[¶](#mapping-strategy-inputs "Link to this heading")

Sometimes you want to apply a simple transformation to a strategy. For instance, we know that we can generate lists of integers with `lists(integers())`. But maybe we wanted to instead generate sorted lists. We could use an inline [`.map()`](#hypothesis.strategies.SearchStrategy.map "hypothesis.strategies.SearchStrategy.map") to achieve this:

\>>> lists(integers()).map(sorted).example()
\[-25527, -24245, -93, -70, -7, 0, 39, 65, 112, 6189, 19469, 32526, 1566924430\]

In general, `strategy.map(f)` returns a new strategy which transforms all the examples generated by `strategy` by calling `f` on them.

##### Filtering strategy inputs[¶](#filtering-strategy-inputs "Link to this heading")

Many strategies in Hypothesis offer some control over the kinds of values that get generated. For instance, `integers(min_value=0)` generates positive integers, and `integers(100, 200)` generates integers between `100` and `200`.

Sometimes, you need more control than this. The inputs from a strategy may not match exactly what you need, and you just need to filter out a few bad cases.

For instance, suppose we have written a simple test involving the modulo operator `%`:

from hypothesis import given, strategies as st

@given(st.integers(), st.integers())
def test\_remainder\_magnitude(a, b):
    \# the remainder after division is always less than
    \# the divisor
    assert abs(a % b) < abs(b)

Hypothesis will quickly report a failure for this test: `ZeroDivisionError: integer modulo by zero`. Just like division, modulo isn’t defined for 0. The case of `b == 0` isn’t interesting for the test, and we would like to get rid of it.

The best way to do this is with the [`.filter()`](#hypothesis.strategies.SearchStrategy.filter "hypothesis.strategies.SearchStrategy.filter") method:

from hypothesis import assume, given, strategies as st

@given(st.integers(), st.integers().filter(lambda n: n != 0))
def test\_remainder\_magnitude(a, b):
    \# b is guaranteed to be nonzero here, thanks to the filter
    assert abs(a % b) < abs(b)

This test now passes cleanly.

Calling [`.filter()`](#hypothesis.strategies.SearchStrategy.filter "hypothesis.strategies.SearchStrategy.filter") on a strategy creates a new strategy with that filter applied at generation-time. For instance, `integers().filter(lambda n: n != 0)` is a strategy which generates nonzero integers.

##### Assuming away test cases[¶](#assuming-away-test-cases "Link to this heading")

[`.filter()`](#hypothesis.strategies.SearchStrategy.filter "hypothesis.strategies.SearchStrategy.filter") lets you filter test inputs from a single strategy. Hypothesis also provides an [`assume()`](#hypothesis.assume "hypothesis.assume") function for when you need to filter an entire test case, based on an arbitrary condition.

The [`assume()`](#hypothesis.assume "hypothesis.assume") function skips test cases where some condition evaluates to `True`. You can use it anywhere in your test. We could have expressed our [`.filter()`](#hypothesis.strategies.SearchStrategy.filter "hypothesis.strategies.SearchStrategy.filter") example above using [`assume()`](#hypothesis.assume "hypothesis.assume") as well:

from hypothesis import assume, given, strategies as st

@given(st.integers(), st.integers())
def test\_remainder\_magnitude(a, b):
    assume(b != 0)
    \# b will be nonzero here
    assert abs(a % b) < abs(b)

###### [`assume()`](#hypothesis.assume "hypothesis.assume") vs [`.filter()`](#hypothesis.strategies.SearchStrategy.filter "hypothesis.strategies.SearchStrategy.filter")[¶](#assume-vs-filter "Link to this heading")

Where possible, you should use [`.filter()`](#hypothesis.strategies.SearchStrategy.filter "hypothesis.strategies.SearchStrategy.filter"). Hypothesis can often rewrite simple filters into more efficient sampling methods than rejection sampling, and will retry filters several times instead of aborting the entire test case (as with [`assume()`](#hypothesis.assume "hypothesis.assume")).

For more complex relationships that can’t be expressed with [`.filter()`](#hypothesis.strategies.SearchStrategy.filter "hypothesis.strategies.SearchStrategy.filter"), use [`assume()`](#hypothesis.assume "hypothesis.assume").

Here’s an example of a test where we want to filter out two different types of examples:

from hypothesis import assume, given, strategies as st

@given(st.integers(), st.integers())
def test\_floor\_division\_lossless\_when\_b\_divides\_a(a, b):
    \# we want to assume that:
    \# \* b is nonzero, and
    \# \* b divides a
    assert (a // b) \* b \== a

We could start by using [`assume()`](#hypothesis.assume "hypothesis.assume") for both:

from hypothesis import assume, given, strategies as st

@given(st.integers(), st.integers())
def test\_floor\_division\_lossless\_when\_b\_divides\_a(a, b):
    assume(b != 0)
    assume(a % b \== 0)
    assert (a // b) \* b \== a

And then notice that the `b != 0` condition can be moved into the strategy definition as a [`.filter()`](#hypothesis.strategies.SearchStrategy.filter "hypothesis.strategies.SearchStrategy.filter") call:

from hypothesis import assume, given, strategies as st

@given(st.integers(), st.integers().filter(lambda n: n != 0))
def test\_floor\_division\_lossless\_when\_b\_divides\_a(a, b):
    assume(a % b \== 0)
    assert (a // b) \* b \== a

However, the `a % b == 0` condition has to stay as an [`assume()`](#hypothesis.assume "hypothesis.assume"), because it expresses a more complicated relationship between `a` and `b`.

###### [`assume()`](#hypothesis.assume "hypothesis.assume") vs early-returning[¶](#assume-vs-early-returning "Link to this heading")

One other way we could have avoided the divide-by-zero error inside the test function is to early-return when `b == 0`:

from hypothesis import assume, given, strategies as st

@given(st.integers(), st.integers())
def test\_remainder\_magnitude(a, b):
    if b \== 0:
        \# bad plan - test "passes" without checking anything!
        return
    assert abs(a % b) < abs(b)

While this would have avoided the divide-by-zero, early-returning is not the same as using [`assume()`](#hypothesis.assume "hypothesis.assume"). With [`assume()`](#hypothesis.assume "hypothesis.assume"), Hypothesis knows that a test case has been filtered out, and will not count it towards the [`max_examples`](#hypothesis.settings.max_examples "hypothesis.settings.max_examples") limit. In contrast, early-returns are counted as a passing test, even though the assertions didn’t run! In more complicted cases, this could end up testing your code less than you expect, because many test cases get discarded without Hypothesis knowing about it.

In addition, [`assume()`](#hypothesis.assume "hypothesis.assume") lets you skip the test case at any point in the test, even inside arbitrarily deep nestings of functions.

#### Custom strategies[¶](#custom-strategies "Link to this heading")

This page describes how to write a custom strategy, for when the built-in strategies don’t quite fit your needs.

##### Writing helper functions[¶](#writing-helper-functions "Link to this heading")

Sometimes you might find it useful to write helper functions, to more concisely express a common pattern for your project. For example, it’s much easier to write (and read!) `response=json()` than to have the whole implementation inline:

def json(\*, finite\_only\=True):
    """Helper function to describe JSON objects, with optional inf and nan."""
    numbers \= st.floats(allow\_infinity\=not finite\_only, allow\_nan\=not finite\_only)
    return st.recursive(
        st.none() | st.booleans() | st.integers() | numbers | st.text(),
        extend\=lambda xs: st.lists(xs) | st.dictionaries(st.text(), xs),
    )

##### Writing your own strategy[¶](#writing-your-own-strategy "Link to this heading")

If a strategy in Hypothesis doesn’t match what you need, you can write your own strategy.

For instance, suppose we want to generate a list of floats which sum to `1`. We might start implementing this by generating lists of integers between 0 and 1 with `lists(floats(0, 1))`. But now we’re a bit stuck, and can’t go any further with the standard strategies.

One way to define a new strategy is using the [`@composite`](#hypothesis.strategies.composite "hypothesis.strategies.composite") decorator. [`@composite`](#hypothesis.strategies.composite "hypothesis.strategies.composite") lets you define a new strategy that uses arbitrary Python code. For instance, to implement the above:

from hypothesis import strategies as st

@st.composite
def sums\_to\_one(draw):
    l \= draw(st.lists(st.floats(0, 1)))
    return \[f / sum(l) for f in l\]

[`@composite`](#hypothesis.strategies.composite "hypothesis.strategies.composite") passes a `draw` function to the decorated function as its first argument. `draw` is used to draw a random value from another strategy. We return from `sums_to_one` a value of the form we wanted to generate; in this case, a list that sums to one.

Let’s see this new strategy in action:

import pytest

from hypothesis import given, strategies as st

@st.composite
def sums\_to\_one(draw):
    lst \= draw(st.lists(st.floats(0.001, 1), min\_size\=1))
    return \[f / sum(lst) for f in lst\]

@given(sums\_to\_one())
def test(lst):
    \# ignore floating point errors
    assert sum(lst) \== pytest.approx(1)

Note

Just like all other strategies, we called `sums_to_one` before passing it to [`@given`](#hypothesis.given "hypothesis.given"). [`@composite`](#hypothesis.strategies.composite "hypothesis.strategies.composite") should be thought of as turning its decorated function into a function which returns a stratgy when called. This is actually the same as existing strategies in Hypothesis; [`integers()`](#hypothesis.strategies.integers "hypothesis.strategies.integers") is really a function, which returns a strategy for integers when called.

###### Combining [`@composite`](#hypothesis.strategies.composite "hypothesis.strategies.composite") with parameters[¶](#combining-st-composite-with-parameters "Link to this heading")

You can add parameters to functions decorated with [`@composite`](#hypothesis.strategies.composite "hypothesis.strategies.composite"), including keyword-only arguments. These work as you would normally expect.

For instance, suppose we wanted to generalize our `sums_to_one` function to `sums_to_n`. We can add a parameter `n`:

import pytest

from hypothesis import assume, given, strategies as st

@st.composite
def sums\_to\_n(draw, n\=1):  \#  <-- changed
    lst \= draw(st.lists(st.floats(0, 1), min\_size\=1))
    assume(sum(lst) \> 0)
    return \[f / sum(lst) \* n for f in lst\]  \#  <-- changed

@given(sums\_to\_n(10))
def test(lst):
    assert sum(lst) \== pytest.approx(10)

And we could just as easily have made `n` a keyword-only argument instead:

import pytest

from hypothesis import assume, given, strategies as st

@st.composite
def sums\_to\_n(draw, \*, n\=1):  \#  <-- changed
    lst \= draw(st.lists(st.floats(0, 1), min\_size\=1))
    assume(sum(lst) \> 0)
    return \[f / sum(lst) \* n for f in lst\]

@given(sums\_to\_n(n\=10))  \#  <-- changed
def test(lst):
    assert sum(lst) \== pytest.approx(10)

###### Dependent generation with [`@composite`](#hypothesis.strategies.composite "hypothesis.strategies.composite")[¶](#dependent-generation-with-st-composite "Link to this heading")

Another scenario where [`@composite`](#hypothesis.strategies.composite "hypothesis.strategies.composite") is useful is when generating a value that depends on a value from another strategy. For instance, suppose we wanted to generate two integers `n1` and `n2` with `n1 <= n2`. We can do this using [`@composite`](#hypothesis.strategies.composite "hypothesis.strategies.composite"):

@st.composite
def ordered\_pairs(draw):
    n1 \= draw(st.integers())
    n2 \= draw(st.integers(min\_value\=n1))
    return (n1, n2)

@given(ordered\_pairs())
def test\_pairs\_are\_ordered(pair):
    n1, n2 \= pair
    assert n1 <= n2

Note

We could also have written this particular strategy as `st.tuples(st.integers(), st.integers()).map(sorted)` (see [Adapting strategies](#document-tutorial/adapting-strategies)). Some prefer this inline approach, while others prefer defining well-named helper functions with [`@composite`](#hypothesis.strategies.composite "hypothesis.strategies.composite"). Our suggestion is simply that you prioritize ease of understanding when choosing which to use.

##### Mixing data generation and test code[¶](#mixing-data-generation-and-test-code "Link to this heading")

When using [`@composite`](#hypothesis.strategies.composite "hypothesis.strategies.composite"), you have to finish generating the entire input before running your test. But maybe you don’t want to generate all of the input until you’re sure some initial test assertions have passed. Or maybe you have some complicated control flow which makes it necessary to generate something in the middle of the test.

[`data()`](#hypothesis.strategies.data "hypothesis.strategies.data") lets you to do this. It’s similar to [`@composite`](#hypothesis.strategies.composite "hypothesis.strategies.composite"), except it lets you mix test code and generation code.

Note

The downside of this power is that [`data()`](#hypothesis.strategies.data "hypothesis.strategies.data") is incompatible [`@example`](#hypothesis.example "hypothesis.example"), and that Hypothesis cannot print a nice representation of values generated from [`data()`](#hypothesis.strategies.data "hypothesis.strategies.data") when reporting failing examples, because the draws are spread out. Where possible, prefer [`@composite`](#hypothesis.strategies.composite "hypothesis.strategies.composite") to [`data()`](#hypothesis.strategies.data "hypothesis.strategies.data").

For instance, here’s how we would write our earlier [`@composite`](#hypothesis.strategies.composite "hypothesis.strategies.composite") example using [`data()`](#hypothesis.strategies.data "hypothesis.strategies.data"):

import pytest

from hypothesis import given, strategies as st

@given(st.data())
def test(data):
    lst \= data.draw(st.lists(st.floats(0.001, 1), min\_size\=1))
    lst \= \[f / sum(lst) for f in lst\]
    \# ignore floating point errors
    assert sum(lst) \== pytest.approx(1)

#### Configuring test settings[¶](#configuring-test-settings "Link to this heading")

This page discusses how to configure the behavior of a single Hypothesis test, or of an entire test suite.

##### Configuring a single test[¶](#configuring-a-single-test "Link to this heading")

Hypothesis lets you configure the default behavior of a test using the [`@settings`](#hypothesis.settings "hypothesis.settings") decorator. You can use settings to configure how many examples Hypothesis generates, how Hypothesis replays failing examples, and the verbosity level of the test, among others.

Using [`@settings`](#hypothesis.settings "hypothesis.settings") on a single test looks like this:

from hypothesis import given, settings, strategies as st

@given(st.integers())
@settings(max\_examples\=200)
def runs\_200\_times\_instead\_of\_100(n):
    pass

You can put [`@settings`](#hypothesis.settings "hypothesis.settings") either before or after [`@given`](#hypothesis.given "hypothesis.given"). Both are equivalent.

###### Changing the number of examples[¶](#changing-the-number-of-examples "Link to this heading")

If you have a test which is very expensive or very cheap to run, you can change the number of examples (inputs) Hypothesis generates with the [`max_examples`](#hypothesis.settings.max_examples "hypothesis.settings.max_examples") setting:

from hypothesis import given, settings, strategies as st

@given(st.integers())
@settings(max\_examples\=5)
def test(n):
    print("prints five times")

The default is 100 examples.

Note

See [How many times will Hypothesis run my test?](#document-explanation/example-count) for details on how [`max_examples`](#hypothesis.settings.max_examples "hypothesis.settings.max_examples") interacts with other parts of Hypothesis.

###### Other settings options[¶](#other-settings-options "Link to this heading")

Here are a few of the more commonly used setting values:

*   [`settings.phases`](#hypothesis.settings.phases "hypothesis.settings.phases") controls which phases of Hypothesis run, like replaying from the database or generating new inputs.
    
*   [`settings.database`](#hypothesis.settings.database "hypothesis.settings.database") controls how and if Hypothesis replays failing examples.
    
*   [`settings.verbosity`](#hypothesis.settings.verbosity "hypothesis.settings.verbosity") can print debug information.
    
*   [`settings.derandomize`](#hypothesis.settings.derandomize "hypothesis.settings.derandomize") makes Hypothesis deterministic. ([Two kinds of testing](https://blog.nelhage.com/post/two-kinds-of-testing/) discusses when and why you might want that).
    

Note

See the [`settings`](#hypothesis.settings "hypothesis.settings") reference for a full list of possible settings.

##### Changing settings across your test suite[¶](#changing-settings-across-your-test-suite "Link to this heading")

In addition to configuring individual test functions with [`@settings`](#hypothesis.settings "hypothesis.settings"), you can configure test behavior across your test suite using a settings profile. This might be useful for creating a development settings profile which runs fewer examples, or a settings profile in CI which connects to a separate database.

To create a settings profile, use [`register_profile()`](#hypothesis.settings.register_profile "hypothesis.settings.register_profile"):

from hypothesis import HealthCheck, settings

settings.register\_profile("fast", max\_examples\=10)

You can place this code in any file which gets loaded before your tests get run. This includes an `__init__.py` file in the test directory or any of the test files themselves. If using pytest, the standard location to place this code is in a `confest.py` file (though an `__init__.py` or test file will also work).

Note that registering a new profile will not affect tests until it is loaded with [`load_profile()`](#hypothesis.settings.load_profile "hypothesis.settings.load_profile"):

from hypothesis import HealthCheck, settings

settings.register\_profile("fast", max\_examples\=10)

\# any tests executed before loading this profile will still use the
\# default active profile of 100 examples.

settings.load\_profile("fast")

\# any tests executed after this point will use the active fast
\# profile of 10 examples.

There is no limit to the number of settings profiles you can create. Hypothesis creates a profile called `"default"`, which is active by default. You can also explicitly make it active at any time using `settings.load_profile("default")`, if for instance you wanted to revert a custom profile you had previously loaded.

###### Loading profiles from environment variables[¶](#loading-profiles-from-environment-variables "Link to this heading")

Using an environment variable to load a settings profile is a useful trick for choosing a settings profile depending on the environment:

\>>> import os
\>>> from hypothesis import settings, Verbosity
\>>> settings.register\_profile("long", max\_examples\=1000)
\>>> settings.register\_profile("fast", max\_examples\=10)
\>>> settings.register\_profile("debug", max\_examples\=10, verbosity\=Verbosity.verbose)
\>>> settings.load\_profile(os.getenv("HYPOTHESIS\_PROFILE", "default"))

If using pytest, you can also easily select the active profile with `--hypothesis-profile`:

$ pytest \--hypothesis-profile fast

See the [Hypothesis pytest plugin](#pytest-plugin).

#### Replaying failed tests[¶](#replaying-failed-tests "Link to this heading")

Replaying failures found by your Hypothesis tests is almost as important as finding failures in the first place. Hypothesis therefore contains several ways to replay failures: they are automatically saved to (and replayed from) a local [`ExampleDatabase`](#hypothesis.database.ExampleDatabase "hypothesis.database.ExampleDatabase"), and can be manually replayed via [`@example`](#hypothesis.example "hypothesis.example") or [`@reproduce_failure`](#hypothesis.reproduce_failure "hypothesis.reproduce_failure").

##### The Hypothesis database[¶](#the-hypothesis-database "Link to this heading")

When a test fails, Hypothesis automatically saves the failure so it can be replayed later. For instance, the first time you run the following code, it will take up to a few seconds to fail:

import time

from hypothesis import strategies as st

@given(st.integers())
def f(n):
    assert n < 50
    time.sleep(0.1)

f()

But the next time you run this code, it will fail instantly. When Hypothesis saw the failure the first time, it automatically saved that failing input. On future runs, Hypothesis retries any failing inputs (in [`Phase.explain`](#hypothesis.Phase.explain "hypothesis.Phase.explain")) before generating new inputs (in [`Phase.generate`](#hypothesis.Phase.generate "hypothesis.Phase.generate"))

Hypothesis saves failures to the [`settings.database`](#hypothesis.settings.database "hypothesis.settings.database") setting. By default, this is a [`DirectoryBasedExampleDatabase`](#hypothesis.database.DirectoryBasedExampleDatabase "hypothesis.database.DirectoryBasedExampleDatabase") in the local `.hypothesis` directory.

###### Disabling the database[¶](#disabling-the-database "Link to this heading")

You can disable the database by passing `database=None` to [`@settings`](#hypothesis.settings "hypothesis.settings"):

@settings(database\=None)
def f(n): ...

##### Using [`@example`](#hypothesis.example "hypothesis.example") to run a specific input[¶](#using-example-to-run-a-specific-input "Link to this heading")

If you want Hypothesis to always run a specific input, you can use [`@example`](#hypothesis.example "hypothesis.example"). [`@example`](#hypothesis.example "hypothesis.example") adds an explicit input which Hypothesis will run every time, in addition to the randomly generated examples. You can think of [`@example`](#hypothesis.example "hypothesis.example") as combining unit-testing with property-based testing.

For instance, suppose we write a test using [`integers()`](#hypothesis.strategies.integers "hypothesis.strategies.integers"), but want to make sure we try a few special prime numbers every time we run the test. We can add these inputs with [`@example`](#hypothesis.example "hypothesis.example"):

\# two mersenne primes
@example(2\*\*17 \- 1)
@example(2\*\*19 \- 1)
@given(st.integers())
def test\_integers(n):
    pass

test\_integers()

Hypothesis runs all explicit examples first, in the [`Phase.explicit`](#hypothesis.Phase.explicit "hypothesis.Phase.explicit") phase, before generating additional random examples in the [`Phase.generate`](#hypothesis.Phase.generate "hypothesis.Phase.generate") phase.

###### Inputs from [`@example`](#hypothesis.example "hypothesis.example") do not shrink[¶](#inputs-from-example-do-not-shrink "Link to this heading")

Note that unlike examples generated by Hypothesis, examples provided using [`@example`](#hypothesis.example "hypothesis.example") do not shrink. We can see this by adding a failing assertion:

@example(2\*\*17 \- 1)
@given(st.integers())
def test\_something\_with\_integers(n):
    assert n < 100

Hypothesis will print `Falsifying explicit example: test_something_with_integers(n=131071)`, instead of shrinking to `n=100`.

##### Prefer [`@example`](#hypothesis.example "hypothesis.example") over the database for correctness[¶](#prefer-example-over-the-database-for-correctness "Link to this heading")

While the database is useful for quick local iteration, Hypothesis may invalidate it when upgrading (because e.g. the internal format may have changed). Changes to the source code of a test function may also change its database key, invalidating its stored entries. We therefore recommend against relying on the database for the correctness of your tests. If you want to ensure an input is run every time, use [`@example`](#hypothesis.example "hypothesis.example").

##### Replaying examples with [`@reproduce_failure`](#hypothesis.reproduce_failure "hypothesis.reproduce_failure")[¶](#replaying-examples-with-reproduce-failure "Link to this heading")

If [`settings.print_blob`](#hypothesis.settings.print_blob "hypothesis.settings.print_blob") is set to `True` (the default in the `ci` settings profile), and a test fails, Hypothesis will print an [`@reproduce_failure`](#hypothesis.reproduce_failure "hypothesis.reproduce_failure") decorator containing an opaque blob as part of the error message:

\>>> from hypothesis import settings, given
\>>> import hypothesis.strategies as st
\>>> @given(st.floats())
... @settings(print\_blob\=True)
... def test(f):
...     assert f \== f
...
\>>> test()

...
Falsifying example: test(
    f=nan,
)
You can reproduce this example by temporarily adding @reproduce\_failure('6.131.23', b'ACh/+AAAAAAAAA==') as a decorator on your test case

You can add this decorator to your test to reproduce the failure. This can be useful for locally replaying failures found by CI. Note that the binary blob is not stable across Hypothesis versions, so you should not leave this decorator on your tests permanently. Use [`@example`](#hypothesis.example "hypothesis.example") with an explicit input instead.

##### Sharing failures with the database[¶](#sharing-failures-with-the-database "Link to this heading")

If you work with multiple developers, or want to share failures across environments (such as locally replaying a failure found by CI), another option is to share the Hypothesis database.

For instance, by setting [`settings.database`](#hypothesis.settings.database "hypothesis.settings.database") to an instance of a networked database like [`RedisExampleDatabase`](#hypothesis.extra.redis.RedisExampleDatabase "hypothesis.extra.redis.RedisExampleDatabase"), any developer connecting to that networked database will automatically replay any failures found by other developers.

Similarly, setting [`settings.database`](#hypothesis.settings.database "hypothesis.settings.database") to [`GitHubArtifactDatabase`](#hypothesis.database.GitHubArtifactDatabase "hypothesis.database.GitHubArtifactDatabase") will automatically replay any failures found by the connected CI artifact.

#### Adding notes[¶](#adding-notes "Link to this heading")

When a test fails, Hypothesis will normally print output that looks like this:

Falsifying example: test\_a\_thing(x\=1, y\="foo")

Sometimes you want to add some additional information to a failure, such as the output of some intermediate step in your test. The [`note()`](#hypothesis.note "hypothesis.note") function lets you do this:

\>>> from hypothesis import given, note, strategies as st
\>>> @given(st.lists(st.integers()), st.randoms())
... def test\_shuffle\_is\_noop(ls, r):
...     ls2 \= list(ls)
...     r.shuffle(ls2)
...     note(f"Shuffle: {ls2!r}")
...     assert ls \== ls2
...
\>>> try:
...     test\_shuffle\_is\_noop()
... except AssertionError:
...     print("ls != ls2")
...
Falsifying example: test\_shuffle\_is\_noop(ls=\[0, 1\], r=RandomWithSeed(1))
Shuffle: \[1, 0\]
ls != ls2

[`note()`](#hypothesis.note "hypothesis.note") is like a print statement that gets attached to the falsifying example reported by Hypothesis. It’s also reported by [observability](#observability), and shown for all examples (if [`settings.verbosity`](#hypothesis.settings.verbosity "hypothesis.settings.verbosity") is set to [`Verbosity.verbose`](#hypothesis.Verbosity.verbose "hypothesis.Verbosity.verbose") or higher).

Note

[`event()`](#hypothesis.event "hypothesis.event") is a similar function which tells Hypothesis to count the number of test cases which reported each distinct value you pass, for inclusion in [test statistics](#statistics) and [observability reports](#observability).

#### Flaky failures[¶](#flaky-failures "Link to this heading")

Have you ever had a test fail, and then you re-run it, only for the test to magically pass? That is a _flaky test_. A flaky test is one which might behave differently when called again. You can think of it as a test which is not deterministic.

Any test can be flaky, but because Hypothesis runs your test many times, Hypothesis tests are particularly likely to uncover flaky behavior.

Note that Hypothesis does not require tests to be fully deterministic. Only the sequence of calls to Hypothesis APIs like `draw` from [`@composite`](#hypothesis.strategies.composite "hypothesis.strategies.composite") and the outcome of the test (pass or fail) need to be deterministic. This means you can use randomness, threads, or nondeterminism in your test, as long as it doesn’t impact anything Hypothesis can see.

##### Why is flakiness bad?[¶](#why-is-flakiness-bad "Link to this heading")

Hypothesis raises an exception when it detects flakiness. This might seem extreme, relative to a simple warning. But there are good reasons to consider flakiness a fatal error.

*   Hypothesis relies on deterministic behavior for the database to work.
    
*   Flakiness makes debugging failures substantially harder if the failing input reported by Hypothesis only flakily reproduces.
    
*   Flakiness makes effectively exploration of the test’s behavior space by Hypothesis difficult or impossible.
    

##### Common sources of flakiness[¶](#common-sources-of-flakiness "Link to this heading")

Here is a quick and non-exhaustive enumeration of some reasons you might encounter flakiness:

*   Decisions based on global state.
    
*   Explicit dependencies between inputs.
    
*   Test depends on filesystem or database state which isn’t reset between inputs.
    
*   Un-managed sources of randomness. This includes standard PRNGs (see also [`register_random()`](#hypothesis.register_random "hypothesis.register_random")), but also thread scheduling, network timing, etc.
    

Note

If your tests depend on global state, consider replacing that state with [`shared()`](#hypothesis.strategies.shared "hypothesis.strategies.shared"). This is a common way to refactor your test to bring conceptually-global state under the control and visibility of Hypothesis.

##### Types of flakiness[¶](#types-of-flakiness "Link to this heading")

When Hypothesis detects that a test is flaky, it will raise one of two [`Flaky`](#hypothesis.errors.Flaky "hypothesis.errors.Flaky") exceptions.

###### Flaky failure[¶](#flaky-failure "Link to this heading")

The most common form of flakiness is that Hypothesis finds a failure, but then replaying that input does not reproduce the failure. For example, here is a contrived test which only fails the first time it is called:

called \= False

@given(st.integers())
def test\_fails\_flakily(n):
    global called
    if not called:
        called \= True
        assert False

The first time Hypothesis generates an input, this test will fail. But when Hypothesis tries replaying that failure—by generating the same input—the test will succeed. This test is flaky.

As a result, running `test_fails_flakily()` will raise [`FlakyFailure`](#hypothesis.errors.FlakyFailure "hypothesis.errors.FlakyFailure"). [`FlakyFailure`](#hypothesis.errors.FlakyFailure "hypothesis.errors.FlakyFailure") is an `ExceptionGroup`, which contains the origin failure as a sub-exception:

\+ Exception Group Traceback (most recent call last):
| hypothesis.errors.FlakyFailure: Hypothesis test\_fails\_flakily(n=0) produces unreliable results: Falsified on the first call but did not on a subsequent one (1 sub-exception)
| Falsifying example: test\_fails\_flakily(
|     n=0,
| )
| Failed to reproduce exception. Expected:
| Traceback (most recent call last):
|   File "/Users/tybug/Desktop/sandbox2.py", line 13, in test\_fails\_flakily
|     assert False
|            ^^^^^
| AssertionError
+-+---------------- 1 ----------------
  | ...
  | Traceback (most recent call last):
  |   File "/Users/tybug/Desktop/sandbox2.py", line 13, in test\_fails\_flakily
  |     assert False
  |            ^^^^^
  | AssertionError
  +------------------------------------

The solution to seeing [`FlakyFailure`](#hypothesis.errors.FlakyFailure "hypothesis.errors.FlakyFailure") is to refactor the test to not depend on external state. In this case, the external state is the variable `called`.

###### Flaky strategy definition[¶](#flaky-strategy-definition "Link to this heading")

Each strategy must ‘do the same thing’ (again, as seen by Hypothesis) if we replay a previously-seen input. Failing to do so is a more subtle but equally serious form of flakiness, which leaves us unable to shrink to a minimal failing input, or even reliably report the failure in future runs.

One easy way for this to occur is if a strategy depends on external state. For example, this strategy filters out previously-generated integers, including those seen in any previous test case:

seen \= set()

@st.composite
def unique\_ints(draw):
    while (n := draw(st.integers())) in seen:
        pass
    seen.add(n)
    return n

@given(unique\_ints(), unique\_ints())
def test\_ints(x, y): ...

By using `seen`, this test is relying on outside state! In the first test case where [`integers()`](#hypothesis.strategies.integers "hypothesis.strategies.integers") generates `0`, `unique_ints` draws only one integer. But if in the next test case [`integers()`](#hypothesis.strategies.integers "hypothesis.strategies.integers") generates `0`, `unique_ints` has to draw two integers because `0` is already in `seen`. This means data generation is not deterministic.

As a result, running `test_ints()` will raise [`FlakyStrategyDefinition`](#hypothesis.errors.FlakyStrategyDefinition "hypothesis.errors.FlakyStrategyDefinition"). The solution is to refactor the strategy to not depend on external state. One way to do this is using [`shared()`](#hypothesis.strategies.shared "hypothesis.strategies.shared"):

@st.composite
def unique\_ints(draw):
    seen\_this\_test \= draw(st.shared(st.builds(set), key\="seen\_ints"))
    while (n := draw(st.integers())) in seen\_this\_test:
        pass
    seen\_this\_test.add(n)
    return n

### How-to guides[¶](#how-to-guides "Link to this heading")

These how-to pages are practical guides for applying Hypothesis in specific scenarios. Each page addresses a particular question about using Hypothesis.

#### Suppress a health check everywhere[¶](#suppress-a-health-check-everywhere "Link to this heading")

Hypothesis sometimes raises a [`HealthCheck`](#hypothesis.HealthCheck "hypothesis.HealthCheck") to indicate that your test may be less effective than you expect, slower than you expect, unlikely to generate effective examples, or otherwise has silently degraded performance.

While [`HealthCheck`](#hypothesis.HealthCheck "hypothesis.HealthCheck") can be useful to proactively identify issues, you may not care about certain classes of them. If you want to disable a [`HealthCheck`](#hypothesis.HealthCheck "hypothesis.HealthCheck") everywhere, you can register and load a settings profile with [`register_profile()`](#hypothesis.settings.register_profile "hypothesis.settings.register_profile") and [`load_profile()`](#hypothesis.settings.load_profile "hypothesis.settings.load_profile"). Place the following code in any file which is loaded before running your tests (or in `conftest.py`, if using pytest):

from hypothesis import HealthCheck, settings

settings.register\_profile(
    "my\_profile", suppress\_health\_check\=\[HealthCheck.filter\_too\_much\]
)
settings.load\_profile("my\_profile")

This profile in particular suppresses the [`HealthCheck.filter_too_much`](#hypothesis.HealthCheck.filter_too_much "hypothesis.HealthCheck.filter_too_much") health check for all tests. The exception is if a test has a [`@settings`](#hypothesis.settings "hypothesis.settings") which explicitly sets a different value for `suppress_health_check`, in which case the profile value will be overridden by the local settings value.

##### I want to suppress all health checks![¶](#i-want-to-suppress-all-health-checks "Link to this heading")

Warning

We strongly recommend that you suppress health checks as you encounter them, rather than using a blanket suppression. Several health checks check for subtle interactions that may save you hours of debugging, such as [`HealthCheck.function_scoped_fixture`](#hypothesis.HealthCheck.function_scoped_fixture "hypothesis.HealthCheck.function_scoped_fixture") and [`HealthCheck.differing_executors`](#hypothesis.HealthCheck.differing_executors "hypothesis.HealthCheck.differing_executors").

If you really want to suppress _all_ health checks, for instance to speed up interactive prototyping, you can:

from hypothesis import HealthCheck, settings

settings.register\_profile("my\_profile", suppress\_health\_check\=list(HealthCheck))
settings.load\_profile("my\_profile")

#### Write type hints for strategies[¶](#write-type-hints-for-strategies "Link to this heading")

Hypothesis provides type hints for all strategies and functions which return a strategy:

from hypothesis import strategies as st

reveal\_type(st.integers())
\# SearchStrategy\[int\]

reveal\_type(st.lists(st.integers()))
\# SearchStrategy\[list\[int\]\]

[`SearchStrategy`](#hypothesis.strategies.SearchStrategy "hypothesis.strategies.SearchStrategy") is the type of a strategy. It is parametrized by the type of the example it generates. You can use it to write type hints for your functions which return a strategy:

from hypothesis import strategies as st
from hypothesis.strategies import SearchStrategy

\# returns a strategy for "normal" numbers
def numbers() \-> SearchStrategy\[int | float\]:
    return st.integers() | st.floats(allow\_nan\=False, allow\_infinity\=False)

It’s worth pointing out the distinction between a strategy, and a function that returns a strategy. [`integers()`](#hypothesis.strategies.integers "hypothesis.strategies.integers") is a function which returns a strategy, and that strategy has type `SearchStrategy[int]`. The function `st.integers` therefore has type `Callable[..., SearchStrategy[int]]`, while the value `s = st.integers()` has type `SearchStrategy[int]`.

##### Type hints for [`@composite`](#hypothesis.strategies.composite "hypothesis.strategies.composite")[¶](#type-hints-for-st-composite "Link to this heading")

When writing type hints for strategies defined with [`@composite`](#hypothesis.strategies.composite "hypothesis.strategies.composite"), use the type of the returned value (not `SearchStrategy`):

@st.composite
def ordered\_pairs(draw) \-> tuple\[int, int\]:
    n1 \= draw(st.integers())
    n2 \= draw(st.integers(min\_value\=n1))
    return (n1, n2)

##### Type variance of [`SearchStrategy`](#hypothesis.strategies.SearchStrategy "hypothesis.strategies.SearchStrategy")[¶](#type-variance-of-searchstrategy "Link to this heading")

[`SearchStrategy`](#hypothesis.strategies.SearchStrategy "hypothesis.strategies.SearchStrategy") is covariant, meaning that if `B < A` then `SearchStrategy[B] < SearchStrategy[A]`. In other words, the strategy `st.from_type(Dog)` is a subtype of the strategy `st.from_type(Animal)`.

#### Write a custom Hypothesis database[¶](#write-a-custom-hypothesis-database "Link to this heading")

To define your own [`ExampleDatabase`](#hypothesis.database.ExampleDatabase "hypothesis.database.ExampleDatabase") class, implement the [`save()`](#hypothesis.database.ExampleDatabase.save "hypothesis.database.ExampleDatabase.save"), [`fetch()`](#hypothesis.database.ExampleDatabase.fetch "hypothesis.database.ExampleDatabase.fetch"), and [`delete()`](#hypothesis.database.ExampleDatabase.delete "hypothesis.database.ExampleDatabase.delete") methods.

For example, here’s a simple database class that uses [`sqlite`](https://docs.python.org/3/library/sqlite3.html#module-sqlite3 "(in Python v3.14)") as the backing data store:

import sqlite3
from collections.abc import Iterable

from hypothesis.database import ExampleDatabase

class SQLiteExampleDatabase(ExampleDatabase):
    def \_\_init\_\_(self, db\_path: str):
        self.conn \= sqlite3.connect(db\_path)

        self.conn.execute(
            """
            CREATE TABLE examples (
                key BLOB,
                value BLOB,
                UNIQUE (key, value)
            )
        """
        )

    def save(self, key: bytes, value: bytes) \-> None:
        self.conn.execute(
            "INSERT OR IGNORE INTO examples VALUES (?, ?)",
            (key, value),
        )

    def fetch(self, key: bytes) \-> Iterable\[bytes\]:
        cursor \= self.conn.execute("SELECT value FROM examples WHERE key = ?", (key,))
        yield from \[value\[0\] for value in cursor.fetchall()\]

    def delete(self, key: bytes, value: bytes) \-> None:
        self.conn.execute(
            "DELETE FROM examples WHERE key = ? AND value = ?",
            (key, value),
        )

Database classes are not required to implement [`move()`](#hypothesis.database.ExampleDatabase.move "hypothesis.database.ExampleDatabase.move"). The default implementation of a move is a [`delete()`](#hypothesis.database.ExampleDatabase.delete "hypothesis.database.ExampleDatabase.delete") of the value in the old key, followed by a [`save()`](#hypothesis.database.ExampleDatabase.save "hypothesis.database.ExampleDatabase.save") of the value in the new key. You can override [`move()`](#hypothesis.database.ExampleDatabase.move "hypothesis.database.ExampleDatabase.move") to override this behavior, if for instance the backing store offers a more efficient move implementation.

##### Change listening[¶](#change-listening "Link to this heading")

To support change listening in a database class, you should call [`_broadcast_change()`](#hypothesis.database.ExampleDatabase._broadcast_change "hypothesis.database.ExampleDatabase._broadcast_change") whenever a value is saved, deleted, or moved in the backing database store. How you track this depends on the details of the database class. For instance, in [`DirectoryBasedExampleDatabase`](#hypothesis.database.DirectoryBasedExampleDatabase "hypothesis.database.DirectoryBasedExampleDatabase"), Hypothesis installs a filesystem monitor via [watchdog](https://pypi.org/project/watchdog/) in order to broadcast change events.

Two useful related methods are [`_start_listening()`](#hypothesis.database.ExampleDatabase._start_listening "hypothesis.database.ExampleDatabase._start_listening") and [`_stop_listening()`](#hypothesis.database.ExampleDatabase._stop_listening "hypothesis.database.ExampleDatabase._stop_listening"), which a database class can override to know when to start or stop expensive listening operations. See documentation for details.

#### Detect Hypothesis tests[¶](#detect-hypothesis-tests "Link to this heading")

How to dynamically determine whether a test function has been defined with Hypothesis.

##### Via `is_hypothesis_test`[¶](#via-is-hypothesis-test "Link to this heading")

The most straightforward way is to use [`is_hypothesis_test()`](#hypothesis.is_hypothesis_test "hypothesis.is_hypothesis_test"):

from hypothesis import is\_hypothesis\_test

@given(st.integers())
def f(n): ...

assert is\_hypothesis\_test(f)

This works for stateful tests as well:

from hypothesis import is\_hypothesis\_test
from hypothesis.stateful import RuleBasedStateMachine

class MyStateMachine(RuleBasedStateMachine): ...

assert is\_hypothesis\_test(MyStateMachine.TestCase().runTest)

##### Via pytest[¶](#via-pytest "Link to this heading")

If you’re working with [pytest](https://pypi.org/project/pytest/), the [Hypothesis pytest plugin](#pytest-plugin) automatically adds the `@pytest.mark.hypothesis` mark to all Hypothesis tests. You can use `node.get_closest_marker("hypothesis")` or similar methods to detect the existence of this mark.

#### Use Hypothesis with an external fuzzer[¶](#use-hypothesis-with-an-external-fuzzer "Link to this heading")

Sometimes you might want to point a traditional fuzzer like [python-afl](https://github.com/jwilk/python-afl) or Google’s [atheris](https://pypi.org/project/atheris/) at your code, to get coverage-guided exploration of native C extensions. The associated tooling is often much less mature than property-based testing libraries though, so you might want to use Hypothesis strategies to describe your input data, and our world-class shrinking and [observability](#observability) tools to wrangle the results. That’s exactly what this how-to guide is about!

Note

If you already have Hypothesis tests and want to fuzz them, or are targeting pure Python code, we strongly recommend the purpose-built [HypoFuzz](https://hypofuzz.com/). This page is about writing traditional ‘fuzz harnesses’ with an external fuzzer, using parts of Hypothesis.

In order to support this workflow, Hypothesis exposes the [`fuzz_one_input()`](#hypothesis.core.HypothesisHandle.fuzz_one_input "hypothesis.core.HypothesisHandle.fuzz_one_input") method. [`fuzz_one_input()`](#hypothesis.core.HypothesisHandle.fuzz_one_input "hypothesis.core.HypothesisHandle.fuzz_one_input") takes a bytestring, parses it into a test case, and executes the corresponding test once. This means you can treat each of your Hypothesis tests as a traditional fuzz target, by pointing the fuzzer at [`fuzz_one_input()`](#hypothesis.core.HypothesisHandle.fuzz_one_input "hypothesis.core.HypothesisHandle.fuzz_one_input").

For example:

from hypothesis import given, strategies as st

@given(st.integers())
def test\_ints(n):
    pass

\# this parses the bytestring into a test case using st.integers(),
\# and then executes \`test\_ints\` once.
test\_ints.hypothesis.fuzz\_one\_input(b"\\x00" \* 50)

Note that [`fuzz_one_input()`](#hypothesis.core.HypothesisHandle.fuzz_one_input "hypothesis.core.HypothesisHandle.fuzz_one_input") bypasses the standard test lifecycle. In a standard test run, Hypothesis is responsible for managing the lifecycle of a test, for example by moving between each [`Phase`](#hypothesis.Phase "hypothesis.Phase"). In contrast, [`fuzz_one_input()`](#hypothesis.core.HypothesisHandle.fuzz_one_input "hypothesis.core.HypothesisHandle.fuzz_one_input") executes one test case, independent of this lifecycle.

See the documentation of [`fuzz_one_input()`](#hypothesis.core.HypothesisHandle.fuzz_one_input "hypothesis.core.HypothesisHandle.fuzz_one_input") for details of how it interacts with other features of Hypothesis, such as [`@settings`](#hypothesis.settings "hypothesis.settings").

##### Worked example: using Atheris[¶](#worked-example-using-atheris "Link to this heading")

Here is an example that uses [`fuzz_one_input()`](#hypothesis.core.HypothesisHandle.fuzz_one_input "hypothesis.core.HypothesisHandle.fuzz_one_input") with the [Atheris](https://github.com/google/atheris) coverage-guided fuzzer (which is built on top of [libFuzzer](https://llvm.org/docs/LibFuzzer.html)):

import json
import sys

import atheris

from hypothesis import given, strategies as st

@given(
    st.recursive(
        st.none() | st.booleans() | st.integers() | st.floats() | st.text(),
        lambda j: st.lists(j) | st.dictionaries(st.text(), j),
    )
)
def test\_json\_dumps\_valid\_json(value):
    json.dumps(value)

atheris.Setup(sys.argv, test\_json\_dumps\_valid\_json.hypothesis.fuzz\_one\_input)
atheris.Fuzz()

Generating valid JSON objects based only on Atheris’ `FuzzDataProvider` interface would be considerably more difficult.

You may also want to use `atheris.instrument_all` or `atheris.instrument_imports` in order to add coverage instrumentation to Atheris. See the [Atheris](https://github.com/google/atheris) documentation for full details.

### Explanations[¶](#explanations "Link to this heading")

These explanation pages are oriented towards deepening your understanding of Hypothesis, including its design philosophy.

#### Domain and distribution[¶](#domain-and-distribution "Link to this heading")

Note

This page is primarily for users who may be familiar with other property-based testing libraries, and who expect control over the distribution of inputs in Hypothesis, via e.g. a `scale` parameter for size or a `frequency` parameter for relative probabilities.

Hypothesis makes a distinction between the _domain_ of a strategy, and the _distribution_ of a strategy.

The _domain_ is the set of inputs that should be possible to generate. For instance, in `lists(integers())`, the domain is lists of integers. For other strategies, particularly those that use [`@composite`](#hypothesis.strategies.composite "hypothesis.strategies.composite") or [`assume()`](#hypothesis.assume "hypothesis.assume") in their definition, the domain might be more complex.

The _distribution_ is the probability with which different elements in the domain should be generated. For `lists(integers())`, should Hypothesis generate many small lists? Large lists? More positive or more negative numbers? etc.

Hypothesis takes a philosophical stance that while users may be responsible for selecting the domain, the property-based testing library—not the user—should be responsible for selecting the distribution. As an intentional design choice, Hypothesis therefore lets you control the domain of inputs to your test, but not the distribution.

##### How should I choose a domain for my test?[¶](#how-should-i-choose-a-domain-for-my-test "Link to this heading")

We recommend using the most-general strategy for your test, so that it can in principle generate any edge case for which the test should pass. Limiting the size of generated inputs, and especially limiting the variety of inputs, can all too easily exclude the bug-triggering values from consideration - and be the difference between a test which finds the bug, or fails to do so.

Sometimes size limits are necessary for performance reasons, but we recommend limiting your strategies only after you’ve seen _substantial_ slowdowns without limits. Far better to find bugs slowly, than not find them at all - and you can manage performance with the [`phases`](#hypothesis.settings.phases "hypothesis.settings.phases") or [`max_examples`](#hypothesis.settings.max_examples "hypothesis.settings.max_examples") settings rather than weakening the test.

##### Why not let users control the distribution?[¶](#why-not-let-users-control-the-distribution "Link to this heading")

There are a few reasons Hypothesis doesn’t let users control the distribution.

*   Humans are pretty bad at choosing bug-finding distributions! Some bugs are “known unknowns”: you suspected that a part of the codebase was buggy in a particular way. Others are “unknown unknowns”: you didn’t know that a bug was possible until stumbling across it. Humans tend to overtune distributions for the former kind of bug, and not enough for the latter.
    
*   The ideal strategy distribution depends not only on the codebase, but also on the property being tested. A strategy used in many places may have a good distribution for one property, but not another.
    
*   The distribution of inputs is a deeply internal implementation detail. We sometimes change strategy distributions, either explicitly, or implicitly from other work on the Hypothesis engine. Exposing this would lock us into a public API that may make improvements to Hypothesis more difficult.
    

Finally, we think distribution control is better handled with [alternative backends](#alternative-backends). If existing backends like `hypofuzz` and `crosshair` don’t suit your needs, you can also write your own. Backends can automatically generalize and adapt to the strategy and property being tested and avoid most of the problems above.

We’re not saying that control over the distribution isn’t useful! We occasionally receive requests to expose the distribution in Hypothesis ([e.g.](https://github.com/HypothesisWorks/hypothesis/issues/4205)), and users wouldn’t be asking for it if it wasn’t. However, adding this to the public strategy API would make it easy for users to unknowingly weaken their tests, and would add maintenance overhead to Hypothesis, and so we haven’t yet done so.

##### Okay, but what _is_ the distribution?[¶](#okay-but-what-is-the-distribution "Link to this heading")

An exact answer depends on both the strategy or strategies for the tests, and the code being tested - but we can make some general remarks, starting with “it’s actually really complicated”.

Hypothesis’ default configuration uses a distribution which is tuned to maximize the chance of finding bugs, in as few executions as possible. We explicitly _don’t_ aim for a uniform distribution, nor for a ‘realistic’ distribution of inputs; Hypothesis’ goal is to search the domain for a failing input as efficiently as possible.

The test case distribution remains an active area of research and development, and we change it whenever we think that would be a net improvement for users. Today, Hypothesis’ default distribution is shaped by a wide variety of techniques and heuristics:

*   some are statically designed into strategies - for example, [`integers()`](#hypothesis.strategies.integers "hypothesis.strategies.integers") upweights range endpoints, and samples from a mixed distribution over integer bit-widths.
    
*   some are dynamic features of the engine - like replaying prior examples with subsections of the input ‘cloned’ or otherwise altered, for bugs which trigger only when different fields have the same value (which is otherwise exponentially unlikely).
    
*   some vary depending on the code under test - we collect interesting-looking constants from imported source files as seeds for test cases.
    

And as if that wasn’t enough, [alternative backends](#alternative-backends) can radically change the distribution again - for example [hypofuzz](https://pypi.org/project/hypofuzz/) uses runtime feedback to modify the distribution of inputs as the test runs, to maximize the rate at which we trigger new behaviors in that particular test and code. If Hypothesis’ defaults aren’t strong enough, we recommend trying Hypofuzz!

#### How many times will Hypothesis run my test?[¶](#how-many-times-will-hypothesis-run-my-test "Link to this heading")

This is a trickier question than you might expect. The short answer is “exactly [`max_examples`](#hypothesis.settings.max_examples "hypothesis.settings.max_examples") times”, with the following exceptions:

*   Less than [`max_examples`](#hypothesis.settings.max_examples "hypothesis.settings.max_examples") times, if Hypothesis exhausts the search space early.
    
*   More than [`max_examples`](#hypothesis.settings.max_examples "hypothesis.settings.max_examples") times, if Hypothesis retries some examples because either:
    
    *   They failed an [`assume()`](#hypothesis.assume "hypothesis.assume") or [`.filter()`](#hypothesis.strategies.SearchStrategy.filter "hypothesis.strategies.SearchStrategy.filter") condition, or
        
    *   They were too large to continue generating.
        
*   Either less or more than [`max_examples`](#hypothesis.settings.max_examples "hypothesis.settings.max_examples") times, if Hypothesis finds a failing example.
    

Read on for details.

##### Search space exhaustion[¶](#search-space-exhaustion "Link to this heading")

If Hypothesis detects that there are no more examples left to try, it may stop generating examples before it hits [`max_examples`](#hypothesis.settings.max_examples "hypothesis.settings.max_examples"). For example:

from hypothesis import given, strategies as st

calls \= 0

@given(st.integers(0, 19))
def test\_function(n):
    global calls
    calls += 1

test\_function()
assert calls \== 20

This runs `test_function` 20 times, not 100, since there are only 20 unique integers to try.

The search space tracking in Hypothesis is good, but not perfect. We treat this more as a bonus than something to strive for.

##### [`assume()`](#hypothesis.assume "hypothesis.assume") and [`.filter()`](#hypothesis.strategies.SearchStrategy.filter "hypothesis.strategies.SearchStrategy.filter")[¶](#assume-and-filter "Link to this heading")

If an example fails to satisfy an [`assume()`](#hypothesis.assume "hypothesis.assume") or [`.filter()`](#hypothesis.strategies.SearchStrategy.filter "hypothesis.strategies.SearchStrategy.filter") condition, Hypothesis will retry generating that example and will not count it towards the [`max_examples`](#hypothesis.settings.max_examples "hypothesis.settings.max_examples") limit. For instance:

from hypothesis import assume, given, strategies as st

@given(st.integers())
def test\_function(n):
    assume(n % 2 \== 0)

will run roughly 200 times, since half of the examples are discarded from the [`assume()`](#hypothesis.assume "hypothesis.assume").

Note that while failing an [`assume()`](#hypothesis.assume "hypothesis.assume") triggers an immediate retry of the entire example, Hypothesis will try several times in the same example to satisfy a [`.filter()`](#hypothesis.strategies.SearchStrategy.filter "hypothesis.strategies.SearchStrategy.filter") condition. This makes expressing the same condition using [`.filter()`](#hypothesis.strategies.SearchStrategy.filter "hypothesis.strategies.SearchStrategy.filter") more efficient than [`assume()`](#hypothesis.assume "hypothesis.assume").

Also note that even if your code does not explicitly use [`assume()`](#hypothesis.assume "hypothesis.assume") or [`.filter()`](#hypothesis.strategies.SearchStrategy.filter "hypothesis.strategies.SearchStrategy.filter"), a builtin strategy may still use them and cause retries. We try to directly satisfy conditions where possible instead of relying on rejection sampling, so this should be relatively uncommon.

##### Examples which are too large[¶](#examples-which-are-too-large "Link to this heading")

For performance reasons, Hypothesis places an internal limit on the size of a single example. If an example exceeds this size limit, we will retry generating it and will not count it towards the [`max_examples`](#hypothesis.settings.max_examples "hypothesis.settings.max_examples") limit. (And if we see too many of these large examples, we will raise [`HealthCheck.data_too_large`](#hypothesis.HealthCheck.data_too_large "hypothesis.HealthCheck.data_too_large"), unless suppressed with [`settings.suppress_health_check`](#hypothesis.settings.suppress_health_check "hypothesis.settings.suppress_health_check")).

The specific value of this size limit is an undocumented implementation detail. The majority of Hypothesis tests do not come close to hitting it.

##### Failing examples[¶](#failing-examples "Link to this heading")

If Hypothesis finds a failing example, it stops generation early, and may call the test function additional times during the [`Phase.shrink`](#hypothesis.Phase.shrink "hypothesis.Phase.shrink") and [`Phase.explain`](#hypothesis.Phase.explain "hypothesis.Phase.explain") phases. Sometimes, Hypothesis determines that the initial failing example was already as simple as possible, in which case [`Phase.shrink`](#hypothesis.Phase.shrink "hypothesis.Phase.shrink") will not result in additional test executions (but [`Phase.explain`](#hypothesis.Phase.explain "hypothesis.Phase.explain") might).

Regardless of whether Hypothesis runs the test during the shrinking and explain phases, it will always run the minimal failing example one additional time to check for flakiness. For instance, the following trivial test runs with `n=0` _twice_, even though it only uses the [`Phase.generate`](#hypothesis.Phase.generate "hypothesis.Phase.generate") phase:

from hypothesis import Phase, given, settings, strategies as st

@given(st.integers())
@settings(phases\=\[Phase.generate\])
def test\_function(n):
    print(f"called with {n}")
    assert n != 0

test\_function()

The first execution finds the initial failure with `n=0`, and the second execution replays `n=0` to ensure the failure is not flaky.

### API Reference[¶](#api-reference "Link to this heading")

The technical API reference for Hypothesis is split into four pages:

*   [API Reference](#document-reference/api). Non-strategy Hypothesis objects, classes, and functions. [`@given`](#hypothesis.given "hypothesis.given") and others live here.
    
*   [Strategies Reference](#document-reference/strategies). Hypothesis strategies, including for [extras](#document-extras).
    
*   [Integrations Reference](#document-reference/integrations). Features with a defined interface, but no code API.
    
*   [Hypothesis internals](#document-reference/internals). Internal APIs for developers building tools, libraries, or research on top of Hypothesis.
    

#### API Reference[¶](#api-reference "Link to this heading")

Reference for non-strategy objects that are part of the Hypothesis API. For documentation on strategies, see the [strategies reference](#document-reference/strategies).

##### `@given`[¶](#given "Link to this heading")

hypothesis.given(_\*\_given\_arguments_, _\*\*\_given\_kwargs_)[¶](#hypothesis.given "Link to this definition")

The [`@given`](#hypothesis.given "hypothesis.given") decorator turns a function into a Hypothesis test. This is the main entry point to Hypothesis.

See also

See also the [Introduction to Hypothesis](#document-tutorial/introduction) tutorial, which introduces defining Hypothesis tests with [`@given`](#hypothesis.given "hypothesis.given").

###### Arguments to `@given`[¶](#arguments-to-given "Link to this heading")

Arguments to [`@given`](#hypothesis.given "hypothesis.given") may be either positional or keyword arguments:

@given(st.integers(), st.floats())
def test\_one(x, y):
    pass

@given(x\=st.integers(), y\=st.floats())
def test\_two(x, y):
    pass

If using keyword arguments, the arguments may appear in any order, as with standard Python functions:

\# different order, but still equivalent to before
@given(y\=st.floats(), x\=st.integers())
def test(x, y):
    assert isinstance(x, int)
    assert isinstance(y, float)

If [`@given`](#hypothesis.given "hypothesis.given") is provided fewer positional arguments than the decorated test, the test arguments are filled in on the right side, leaving the leftmost positional arguments unfilled:

@given(st.integers(), st.floats())
def test(manual\_string, y, z):
    assert manual\_string \== "x"
    assert isinstance(y, int)
    assert isinstance(z, float)

\# \`test\` is now a callable which takes one argument \`manual\_string\`

test("x")
\# or equivalently:
test(manual\_string\="x")

The reason for this “from the right” behavior is to support using [`@given`](#hypothesis.given "hypothesis.given") with instance methods, by automatically passing through `self`:

class MyTest(TestCase):
    @given(st.integers())
    def test(self, x):
        assert isinstance(self, MyTest)
        assert isinstance(x, int)

If (and only if) using keyword arguments, [`@given`](#hypothesis.given "hypothesis.given") may be combined with `**kwargs` or `*args`:

@given(x\=integers(), y\=integers())
def test(x, \*\*kwargs):
    assert "y" in kwargs

@given(x\=integers(), y\=integers())
def test(x, \*args, \*\*kwargs):
    assert args \== ()
    assert "x" not in kwargs
    assert "y" in kwargs

It is an error to:

*   Mix positional and keyword arguments to [`@given`](#hypothesis.given "hypothesis.given").
    
*   Use [`@given`](#hypothesis.given "hypothesis.given") with a function that has a default value for an argument.
    
*   Use [`@given`](#hypothesis.given "hypothesis.given") with positional arguments with a function that uses `*args`, `**kwargs`, or keyword-only arguments.
    

The function returned by given has all the same arguments as the original test, minus those that are filled in by [`@given`](#hypothesis.given "hypothesis.given"). See the [notes on framework compatibility](#framework-compatibility) for how this interacts with features of other testing libraries, such as [pytest](https://pypi.org/project/pytest/) fixtures.

hypothesis.infer[¶](#hypothesis.infer "Link to this definition")

An alias for `...` ([`Ellipsis`](https://docs.python.org/3/library/constants.html#Ellipsis "(in Python v3.14)")). [`infer`](#hypothesis.infer "hypothesis.infer") can be passed to [`@given`](#hypothesis.given "hypothesis.given") or [`builds()`](#hypothesis.strategies.builds "hypothesis.strategies.builds") to indicate that a strategy for that parameter should be inferred from its type annotations.

In all cases, using [`infer`](#hypothesis.infer "hypothesis.infer") is equivalent to using `...`.

###### Inferred strategies[¶](#inferred-strategies "Link to this heading")

In some cases, Hypothesis can work out what to do when you omit arguments. This is based on introspection, _not_ magic, and therefore has well-defined limits.

[`builds()`](#hypothesis.strategies.builds "hypothesis.strategies.builds") will check the signature of the `target` (using [`inspect.signature()`](https://docs.python.org/3/library/inspect.html#inspect.signature "(in Python v3.14)")). If there are required arguments with type annotations and no strategy was passed to [`builds()`](#hypothesis.strategies.builds "hypothesis.strategies.builds"), [`from_type()`](#hypothesis.strategies.from_type "hypothesis.strategies.from_type") is used to fill them in. You can also pass the value `...` (`Ellipsis`) as a keyword argument, to force this inference for arguments with a default value.

\>>> def func(a: int, b: str):
...     return \[a, b\]
...
\>>> builds(func).example()
\[-6993, ''\]

[`@given`](#hypothesis.given "hypothesis.given") does not perform any implicit inference for required arguments, as this would break compatibility with pytest fixtures. `...` ([`Ellipsis`](https://docs.python.org/3/library/constants.html#Ellipsis "(in Python v3.14)")), can be used as a keyword argument to explicitly fill in an argument from its type annotation. You can also use the [`infer`](#hypothesis.infer "hypothesis.infer") alias if writing a literal `...` seems too weird.

@given(a\=...)  \# or @given(a=infer)
def test(a: int):
    pass

\# is equivalent to
@given(a\=from\_type(int))
def test(a):
    pass

`@given(...)` can also be specified to fill all arguments from their type annotations.

@given(...)
def test(a: int, b: str):
    pass

\# is equivalent to
@given(a\=..., b\=...)
def test(a, b):
    pass

###### Limitations[¶](#limitations "Link to this heading")

Hypothesis does not inspect [**PEP 484**](https://peps.python.org/pep-0484/) type comments at runtime. While [`from_type()`](#hypothesis.strategies.from_type "hypothesis.strategies.from_type") will work as usual, inference in [`builds()`](#hypothesis.strategies.builds "hypothesis.strategies.builds") and [`@given`](#hypothesis.given "hypothesis.given") will only work if you manually create the `__annotations__` attribute (e.g. by using `@annotations(...)` and `@returns(...)` decorators).

The [`typing`](https://docs.python.org/3/library/typing.html#module-typing "(in Python v3.14)") module changes between different Python releases, including at minor versions. These are all supported on a best-effort basis, but you may encounter problems. Please report them to us, and consider updating to a newer version of Python as a workaround.

##### Explicit inputs[¶](#explicit-inputs "Link to this heading")

See also

See also the [Replaying failed tests](#document-tutorial/replaying-failures) tutorial, which discusses using explicit inputs to reproduce failures.

_class_ hypothesis.example(_\*args_, _\*\*kwargs_)[¶](#hypothesis.example "Link to this definition")

Add an explicit input to a Hypothesis test, which Hypothesis will always try before generating random inputs. This combines the randomized nature of Hypothesis generation with a traditional parametrized test.

For example:

@example("Hello world")
@example("some string with special significance")
@given(st.text())
def test\_strings(s):
    pass

will call `test_strings("Hello World")` and `test_strings("some string with special significance")` before generating any random inputs. [`@example`](#hypothesis.example "hypothesis.example") may be placed in any order relative to [`@given`](#hypothesis.given "hypothesis.given") and [`@settings`](#hypothesis.settings "hypothesis.settings").

Explicit inputs from [`@example`](#hypothesis.example "hypothesis.example") are run in the [`Phase.explicit`](#hypothesis.Phase.explicit "hypothesis.Phase.explicit") phase. Explicit inputs do not count towards [`settings.max_examples`](#hypothesis.settings.max_examples "hypothesis.settings.max_examples"). Note that explicit inputs added by [`@example`](#hypothesis.example "hypothesis.example") do not shrink. If an explicit input fails, Hypothesis will stop and report the failure without generating any random inputs.

[`@example`](#hypothesis.example "hypothesis.example") can also be used to easily reproduce a failure. For instance, if Hypothesis reports that `f(n=[0, math.nan])` fails, you can add `@example(n=[0, math.nan])` to your test to quickly reproduce that failure.

###### Arguments to `@example`[¶](#arguments-to-example "Link to this heading")

Arguments to [`@example`](#hypothesis.example "hypothesis.example") have the same behavior and restrictions as arguments to [`@given`](#hypothesis.given "hypothesis.given"). This means they may be either positional or keyword arguments (but not both in the same [`@example`](#hypothesis.example "hypothesis.example")):

@example(1, 2)
@example(x\=1, y\=2)
@given(st.integers(), st.integers())
def test(x, y):
    pass

Noting that while arguments to [`@given`](#hypothesis.given "hypothesis.given") are strategies (like [`integers()`](#hypothesis.strategies.integers "hypothesis.strategies.integers")), arguments to [`@example`](#hypothesis.example "hypothesis.example") are values instead (like `1`).

See the [Arguments to @given](#given-arguments) section for full details.

example.xfail(

_condition=True_,

_\*_,

_reason=''_,

_raises=<class 'BaseException'>_,

)[¶](#hypothesis.example.xfail "Link to this definition")

Mark this example as an expected failure, similarly to [`pytest.mark.xfail(strict=True)`](https://docs.pytest.org/en/stable/reference/reference.html#pytest.mark.xfail "(in pytest v9.0.1)").

Expected-failing examples allow you to check that your test does fail on some examples, and therefore build confidence that _passing_ tests are because your code is working, not because the test is missing something.

@example(...).xfail()
@example(...).xfail(reason\="Prices must be non-negative")
@example(...).xfail(raises\=(KeyError, ValueError))
@example(...).xfail(sys.version\_info\[:2\] \>= (3, 12), reason\="needs py 3.12")
@example(...).xfail(condition\=sys.platform != "linux", raises\=OSError)
def test(x):
    pass

Note

Expected-failing examples are handled separately from those generated by strategies, so you should usually ensure that there is no overlap.

@example(x\=1, y\=0).xfail(raises\=ZeroDivisionError)
@given(x\=st.just(1), y\=st.integers())  \# Missing \`.filter(bool)\`!
def test\_fraction(x, y):
    \# This test will try the explicit example and see it fail as
    \# expected, then go on to generate more examples from the
    \# strategy.  If we happen to generate y=0, the test will fail
    \# because only the explicit example is treated as xfailing.
    x / y

example.via(_whence_, _/_)[¶](#hypothesis.example.via "Link to this definition")

Attach a machine-readable label noting what the origin of this example was. [`example.via`](#hypothesis.example.via "hypothesis.example.via") is completely optional and does not change runtime behavior.

[`example.via`](#hypothesis.example.via "hypothesis.example.via") is intended to support self-documenting behavior, as well as tooling which might add (or remove) [`@example`](#hypothesis.example "hypothesis.example") decorators automatically. For example:

\# Annotating examples is optional and does not change runtime behavior
@example(...)
@example(...).via("regression test for issue #42")
@example(...).via("discovered failure")
def test(x):
    pass

Note

[HypoFuzz](https://hypofuzz.com/) uses [`example.via`](#hypothesis.example.via "hypothesis.example.via") to tag examples in the patch of its high-coverage set of explicit inputs, on [the patches page](https://hypofuzz.com/example-dashboard/#/patches).

##### Reproducing inputs[¶](#reproducing-inputs "Link to this heading")

See also

See also the [Replaying failed tests](#document-tutorial/replaying-failures) tutorial.

hypothesis.reproduce\_failure(_version_, _blob_)[¶](#hypothesis.reproduce_failure "Link to this definition")

Run the example corresponding to the binary `blob` in order to reproduce a failure. `blob` is a serialized version of the internal input representation of Hypothesis.

A test decorated with [`@reproduce_failure`](#hypothesis.reproduce_failure "hypothesis.reproduce_failure") always runs exactly one example, which is expected to cause a failure. If the provided `blob` does not cause a failure, Hypothesis will raise [`DidNotReproduce`](#hypothesis.errors.DidNotReproduce "hypothesis.errors.DidNotReproduce").

Hypothesis will print an [`@reproduce_failure`](#hypothesis.reproduce_failure "hypothesis.reproduce_failure") decorator if [`settings.print_blob`](#hypothesis.settings.print_blob "hypothesis.settings.print_blob") is `True` (which is the default in CI).

[`@reproduce_failure`](#hypothesis.reproduce_failure "hypothesis.reproduce_failure") is intended to be temporarily added to your test suite in order to reproduce a failure. It is not intended to be a permanent addition to your test suite. Because of this, no compatibility guarantees are made across Hypothesis versions, and [`@reproduce_failure`](#hypothesis.reproduce_failure "hypothesis.reproduce_failure") will error if used on a different Hypothesis version than it was created for.

See also

See also the [Replaying failed tests](#document-tutorial/replaying-failures) tutorial.

hypothesis.seed(_seed_)[¶](#hypothesis.seed "Link to this definition")

Seed the randomness for this test.

`seed` may be any hashable object. No exact meaning for `seed` is provided other than that for a fixed seed value Hypothesis will produce the same examples (assuming that there are no other sources of nondeterminisim, such as timing, hash randomization, or external state).

For example, the following test function and [`RuleBasedStateMachine`](#hypothesis.stateful.RuleBasedStateMachine "hypothesis.stateful.RuleBasedStateMachine") will each generate the same series of examples each time they are executed:

@seed(1234)
@given(st.integers())
def test(n): ...

@seed(6789)
class MyMachine(RuleBasedStateMachine): ...

If using pytest, you can alternatively pass `--hypothesis-seed` on the command line.

Setting a seed overrides [`settings.derandomize`](#hypothesis.settings.derandomize "hypothesis.settings.derandomize"), which is designed to enable deterministic CI tests rather than reproducing observed failures.

Hypothesis will only print the seed which would reproduce a failure if a test fails in an unexpected way, for instance inside Hypothesis internals.

##### Control[¶](#control "Link to this heading")

Functions that can be called from anywhere inside a test, to either modify how Hypothesis treats the current test case, or to give Hypothesis more information about the current test case.

hypothesis.assume(_condition_)[¶](#hypothesis.assume "Link to this definition")

Calling `assume` is like an [assert](https://docs.python.org/3/reference/simple_stmts.html#assert "(in Python v3.14)") that marks the example as bad, rather than failing the test.

This allows you to specify properties that you _assume_ will be true, and let Hypothesis try to avoid similar examples in future.

hypothesis.note(_value_)[¶](#hypothesis.note "Link to this definition")

Report this value for the minimal failing example.

hypothesis.event(_value_, _payload\=''_)[¶](#hypothesis.event "Link to this definition")

Record an event that occurred during this test. Statistics on the number of test runs with each event will be reported at the end if you run Hypothesis in statistics reporting mode.

Event values should be strings or convertible to them. If an optional payload is given, it will be included in the string for [Test statistics](#statistics).

You can mark custom events in a test using [`event()`](#hypothesis.event "hypothesis.event"):

from hypothesis import event, given, strategies as st

@given(st.integers().filter(lambda x: x % 2 \== 0))
def test\_even\_integers(i):
    event(f"i mod 3 = {i%3}")

These events appear in [observability](#observability) output, as well as the output of [our pytest plugin](#pytest-plugin) when run with `--hypothesis-show-statistics`.

For instance, in the latter case, you would see output like:

test\_even\_integers:

  - during generate phase (0.09 seconds):
      - Typical runtimes: < 1ms, ~ 59% in data generation
      - 100 passing examples, 0 failing examples, 32 invalid examples
      - Events:
        \* 54.55%, Retried draw from integers().filter(lambda x: x % 2 == 0) to satisfy filter
        \* 31.06%, i mod 3 = 2
        \* 28.79%, i mod 3 = 0
        \* 24.24%, Aborted test because unable to satisfy integers().filter(lambda x: x % 2 == 0)
        \* 15.91%, i mod 3 = 1
  - Stopped because settings.max\_examples=100

Arguments to `event` can be any hashable type, but two events will be considered the same if they are the same when converted to a string with [`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.14)").

###### Targeted property-based testing[¶](#targeted-property-based-testing "Link to this heading")

Targeted property-based testing combines the advantages of both search-based and property-based testing. Instead of being completely random, targeted PBT uses a search-based component to guide the input generation towards values that have a higher probability of falsifying a property. This explores the input space more effectively and requires fewer tests to find a bug or achieve a high confidence in the system being tested than random PBT. ([Löscher and Sagonas](http://proper.softlab.ntua.gr/Publications.html))

This is not _always_ a good idea - for example calculating the search metric might take time better spent running more uniformly-random test cases, or your target metric might accidentally lead Hypothesis _away_ from bugs - but if there is a natural metric like “floating-point error”, “load factor” or “queue length”, we encourage you to experiment with targeted testing.

We recommend that users also skim the papers introducing targeted PBT; from [ISSTA 2017](http://proper.softlab.ntua.gr/papers/issta2017.pdf) and [ICST 2018](http://proper.softlab.ntua.gr/papers/icst2018.pdf). For the curious, the initial implementation in Hypothesis uses hill-climbing search via a mutating fuzzer, with some tactics inspired by simulated annealing to avoid getting stuck and endlessly mutating a local maximum.

from hypothesis import given, strategies as st, target

@given(st.floats(0, 1e100), st.floats(0, 1e100), st.floats(0, 1e100))
def test\_associativity\_with\_target(a, b, c):
    ab\_c \= (a + b) + c
    a\_bc \= a + (b + c)
    difference \= abs(ab\_c \- a\_bc)
    target(difference)  \# Without this, the test almost always passes
    assert difference < 2.0

hypothesis.target(_observation_, _\*_, _label\=''_)[¶](#hypothesis.target "Link to this definition")

Calling this function with an `int` or `float` observation gives it feedback with which to guide our search for inputs that will cause an error, in addition to all the usual heuristics. Observations must always be finite.

Hypothesis will try to maximize the observed value over several examples; almost any metric will work so long as it makes sense to increase it. For example, `-abs(error)` is a metric that increases as `error` approaches zero.

Example metrics:

*   Number of elements in a collection, or tasks in a queue
    
*   Mean or maximum runtime of a task (or both, if you use `label`)
    
*   Compression ratio for data (perhaps per-algorithm or per-level)
    
*   Number of steps taken by a state machine
    

The optional `label` argument can be used to distinguish between and therefore separately optimise distinct observations, such as the mean and standard deviation of a dataset. It is an error to call `target()` with any label more than once per test case.

Note

The more examples you run, the better this technique works.

As a rule of thumb, the targeting effect is noticeable above [`max_examples=1000`](#hypothesis.settings.max_examples "hypothesis.settings.max_examples"), and immediately obvious by around ten thousand examples _per label_ used by your test.

[Test statistics](#statistics) include the best score seen for each label, which can help avoid [the threshold problem](https://hypothesis.works/articles/threshold-problem/) when the minimal example shrinks right down to the threshold of failure ([issue #2180](https://github.com/HypothesisWorks/hypothesis/issues/2180)).

##### Settings[¶](#settings "Link to this heading")

See also

See also [the tutorial for settings](#document-tutorial/settings).

_class_ hypothesis.settings(

_parent\=None_,

_\*_,

_max\_examples\=not\_set_,

_derandomize\=not\_set_,

_database\=not\_set_,

_verbosity\=not\_set_,

_phases\=not\_set_,

_stateful\_step\_count\=not\_set_,

_report\_multiple\_bugs\=not\_set_,

_suppress\_health\_check\=not\_set_,

_deadline\=not\_set_,

_print\_blob\=not\_set_,

_backend\=not\_set_,

)[¶](#hypothesis.settings "Link to this definition")

A settings object controls the following aspects of test behavior: [`max_examples`](#hypothesis.settings.max_examples "hypothesis.settings.max_examples"), [`derandomize`](#hypothesis.settings.derandomize "hypothesis.settings.derandomize"), [`database`](#hypothesis.settings.database "hypothesis.settings.database"), [`verbosity`](#hypothesis.settings.verbosity "hypothesis.settings.verbosity"), [`phases`](#hypothesis.settings.phases "hypothesis.settings.phases"), [`stateful_step_count`](#hypothesis.settings.stateful_step_count "hypothesis.settings.stateful_step_count"), [`report_multiple_bugs`](#hypothesis.settings.report_multiple_bugs "hypothesis.settings.report_multiple_bugs"), [`suppress_health_check`](#hypothesis.settings.suppress_health_check "hypothesis.settings.suppress_health_check"), [`deadline`](#hypothesis.settings.deadline "hypothesis.settings.deadline"), [`print_blob`](#hypothesis.settings.print_blob "hypothesis.settings.print_blob"), and [`backend`](#hypothesis.settings.backend "hypothesis.settings.backend").

A settings object can be applied as a decorator to a test function, in which case that test function will use those settings. A test may only have one settings object applied to it. A settings object can also be passed to [`register_profile()`](#hypothesis.settings.register_profile "hypothesis.settings.register_profile") or as a parent to another [`settings`](#hypothesis.settings "hypothesis.settings").

###### Attribute inheritance[¶](#attribute-inheritance "Link to this heading")

Settings objects are immutable once created. When a settings object is created, it uses the value specified for each attribute. Any attribute which is not specified will inherit from its value in the `parent` settings object. If `parent` is not passed, any attributes which are not specified will inherit from the current settings profile instead.

For instance, `settings(max_examples=10)` will have a `max_examples` of `10`, and the value of all other attributes will be equal to its value in the current settings profile.

Changes made from activating a new settings profile with [`load_profile()`](#hypothesis.settings.load_profile "hypothesis.settings.load_profile") will be reflected in settings objects created after the profile was loaded, but not in existing settings objects.

###### Built-in profiles[¶](#built-in-profiles "Link to this heading")

While you can register additional profiles with [`register_profile()`](#hypothesis.settings.register_profile "hypothesis.settings.register_profile"), Hypothesis comes with two built-in profiles: `default` and `ci`.

By default, the `default` profile is active. If the `CI` environment variable is set to any value, the `ci` profile is active by default. Hypothesis also automatically detects various vendor-specific CI environment variables.

The attributes of the currently active settings profile can be retrieved with `settings()` (so `settings().max_examples` is the currently active default for [`settings.max_examples`](#hypothesis.settings.max_examples "hypothesis.settings.max_examples")).

The settings attributes for the built-in profiles are as follows:

default \= settings.register\_profile(
    "default",
    max\_examples\=100,
    derandomize\=False,
    database\=not\_set,  \# see settings.database for the default database
    verbosity\=Verbosity.normal,
    phases\=tuple(Phase),
    stateful\_step\_count\=50,
    report\_multiple\_bugs\=True,
    suppress\_health\_check\=(),
    deadline\=duration(milliseconds\=200),
    print\_blob\=False,
    backend\="hypothesis",
)

ci \= settings.register\_profile(
    "ci",
    parent\=default,
    derandomize\=True,
    deadline\=None,
    database\=None,
    print\_blob\=True,
    suppress\_health\_check\=\[HealthCheck.too\_slow\],
)

You can replace either of the built-in profiles with [`register_profile()`](#hypothesis.settings.register_profile "hypothesis.settings.register_profile"):

\# run more examples in CI
settings.register\_profile(
    "ci",
    settings.get\_profile("ci"),
    max\_examples\=1000,
)

_property_ max\_examples[¶](#hypothesis.settings.max_examples "Link to this definition")

Once this many satisfying examples have been considered without finding any counter-example, Hypothesis will stop looking.

Note that we might call your test function fewer times if we find a bug early or can tell that we’ve exhausted the search space; or more if we discard some examples due to use of .filter(), assume(), or a few other things that can prevent the test case from completing successfully.

The default value is chosen to suit a workflow where the test will be part of a suite that is regularly executed locally or on a CI server, balancing total running time against the chance of missing a bug.

If you are writing one-off tests, running tens of thousands of examples is quite reasonable as Hypothesis may miss uncommon bugs with default settings. For very complex code, we have observed Hypothesis finding novel bugs after _several million_ examples while testing [SymPy](https://pypi.org/project/sympy/). If you are running more than 100k examples for a test, consider using our [integration for coverage-guided fuzzing](#fuzz-one-input) - it really shines when given minutes or hours to run.

The default max examples is `100`.

_property_ derandomize[¶](#hypothesis.settings.derandomize "Link to this definition")

If True, seed Hypothesis’ random number generator using a hash of the test function, so that every run will test the same set of examples until you update Hypothesis, Python, or the test function.

This allows you to [check for regressions and look for bugs](https://blog.nelhage.com/post/two-kinds-of-testing/) using separate settings profiles - for example running quick deterministic tests on every commit, and a longer non-deterministic nightly testing run.

The default is `False`. If running on CI, the default is `True` instead.

_property_ database[¶](#hypothesis.settings.database "Link to this definition")

An instance of [`ExampleDatabase`](#hypothesis.database.ExampleDatabase "hypothesis.database.ExampleDatabase") that will be used to save examples to and load previous examples from.

If not set, a [`DirectoryBasedExampleDatabase`](#hypothesis.database.DirectoryBasedExampleDatabase "hypothesis.database.DirectoryBasedExampleDatabase") is created in the current working directory under `.hypothesis/examples`. If this location is unusable, e.g. due to the lack of read or write permissions, Hypothesis will emit a warning and fall back to an [`InMemoryExampleDatabase`](#hypothesis.database.InMemoryExampleDatabase "hypothesis.database.InMemoryExampleDatabase").

If `None`, no storage will be used.

See the [database documentation](#database) for a list of database classes, and how to define custom database classes.

_property_ verbosity[¶](#hypothesis.settings.verbosity "Link to this definition")

Control the verbosity level of Hypothesis messages.

To see what’s going on while Hypothesis runs your tests, you can turn up the verbosity setting.

\>>> from hypothesis import settings, Verbosity
\>>> from hypothesis.strategies import lists, integers
\>>> @given(lists(integers()))
... @settings(verbosity\=Verbosity.verbose)
... def f(x):
...     assert not any(x)
... f()
Trying example: \[\]
Falsifying example: \[-1198601713, -67, 116, -29578\]
Shrunk example to \[-1198601713\]
Shrunk example to \[-128\]
Shrunk example to \[32\]
Shrunk example to \[1\]
\[1\]

The four levels are [`Verbosity.quiet`](#hypothesis.Verbosity.quiet "hypothesis.Verbosity.quiet"), [`Verbosity.normal`](#hypothesis.Verbosity.normal "hypothesis.Verbosity.normal"), [`Verbosity.verbose`](#hypothesis.Verbosity.verbose "hypothesis.Verbosity.verbose"), and [`Verbosity.debug`](#hypothesis.Verbosity.debug "hypothesis.Verbosity.debug"). [`Verbosity.normal`](#hypothesis.Verbosity.normal "hypothesis.Verbosity.normal") is the default. For [`Verbosity.quiet`](#hypothesis.Verbosity.quiet "hypothesis.Verbosity.quiet"), Hypothesis will not print anything out, not even the final falsifying example. [`Verbosity.debug`](#hypothesis.Verbosity.debug "hypothesis.Verbosity.debug") is basically [`Verbosity.verbose`](#hypothesis.Verbosity.verbose "hypothesis.Verbosity.verbose") but a bit more so. You probably don’t want it.

Verbosity can be passed either as a [`Verbosity`](#hypothesis.Verbosity "hypothesis.Verbosity") enum value, or as the corresponding string value, or as the corresponding integer value. For example:

\# these three are equivalent
settings(verbosity\=Verbosity.verbose)
settings(verbosity\="verbose")

If you are using [pytest](https://pypi.org/project/pytest/), you may also need to [disable output capturing for passing tests](https://docs.pytest.org/en/stable/how-to/capture-stdout-stderr.html "(in pytest v9.0.1)") to see verbose output as tests run.

_property_ phases[¶](#hypothesis.settings.phases "Link to this definition")

Control which phases should be run.

Hypothesis divides tests into logically distinct phases.

*   [`Phase.explicit`](#hypothesis.Phase.explicit "hypothesis.Phase.explicit"): Running explicit examples from [`@example`](#hypothesis.example "hypothesis.example").
    
*   [`Phase.reuse`](#hypothesis.Phase.reuse "hypothesis.Phase.reuse"): Running examples from the database which previously failed.
    
*   [`Phase.generate`](#hypothesis.Phase.generate "hypothesis.Phase.generate"): Generating new random examples.
    
*   [`Phase.target`](#hypothesis.Phase.target "hypothesis.Phase.target"): Mutating examples for [targeted property-based testing](#targeted). Requires [`Phase.generate`](#hypothesis.Phase.generate "hypothesis.Phase.generate").
    
*   [`Phase.shrink`](#hypothesis.Phase.shrink "hypothesis.Phase.shrink"): Shrinking failing examples.
    
*   [`Phase.explain`](#hypothesis.Phase.explain "hypothesis.Phase.explain"): Attempting to explain why a failure occurred. Requires [`Phase.shrink`](#hypothesis.Phase.shrink "hypothesis.Phase.shrink").
    

The phases argument accepts a collection with any subset of these. E.g. `settings(phases=[Phase.generate, Phase.shrink])` will generate new examples and shrink them, but will not run explicit examples or reuse previous failures, while `settings(phases=[Phase.explicit])` will only run explicit examples from [`@example`](#hypothesis.example "hypothesis.example").

Phases can be passed either as a [`Phase`](#hypothesis.Phase "hypothesis.Phase") enum value, or as the corresponding string value. For example:

\# these two are equivalent
settings(phases\=\[Phase.explicit\])
settings(phases\=\["explicit"\])

Following the first failure, Hypothesis will (usually, depending on which [`Phase`](#hypothesis.Phase "hypothesis.Phase") is enabled) track which lines of code are always run on failing but never on passing inputs. On 3.12+, this uses [`sys.monitoring`](https://docs.python.org/3/library/sys.monitoring.html#module-sys.monitoring "(in Python v3.14)"), while 3.11 and earlier uses [`sys.settrace()`](https://docs.python.org/3/library/sys.html#sys.settrace "(in Python v3.14)"). For python 3.11 and earlier, we therefore automatically disable the explain phase on PyPy, or if you are using [coverage](https://pypi.org/project/coverage/) or a debugger. If there are no clearly suspicious lines of code, [**we refuse the temptation to guess**](https://peps.python.org/pep-0020/).

After shrinking to a minimal failing example, Hypothesis will try to find parts of the example – e.g. separate args to [`@given`](#hypothesis.given "hypothesis.given") – which can vary freely without changing the result of that minimal failing example. If the automated experiments run without finding a passing variation, we leave a comment in the final report:

test\_x\_divided\_by\_y(
    x\=0,  \# or any other generated value
    y\=0,
)

Just remember that the _lack_ of an explanation sometimes just means that Hypothesis couldn’t efficiently find one, not that no explanation (or simpler failing example) exists.

_property_ stateful\_step\_count[¶](#hypothesis.settings.stateful_step_count "Link to this definition")

The maximum number of times to call an additional [`@rule`](#hypothesis.stateful.rule "hypothesis.stateful.rule") method in [stateful testing](#stateful) before we give up on finding a bug.

Note that this setting is effectively multiplicative with max\_examples, as each example will run for a maximum of `stateful_step_count` steps.

The default stateful step count is `50`.

_property_ report\_multiple\_bugs[¶](#hypothesis.settings.report_multiple_bugs "Link to this definition")

Because Hypothesis runs the test many times, it can sometimes find multiple bugs in a single run. Reporting all of them at once is usually very useful, but replacing the exceptions can occasionally clash with debuggers. If disabled, only the exception with the smallest minimal example is raised.

The default value is `True`.

_property_ suppress\_health\_check[¶](#hypothesis.settings.suppress_health_check "Link to this definition")

Suppress the given [`HealthCheck`](#hypothesis.HealthCheck "hypothesis.HealthCheck") exceptions. Those health checks will not be raised by Hypothesis. To suppress all health checks, you can pass `suppress_health_check=list(HealthCheck)`.

Health checks can be passed either as a [`HealthCheck`](#hypothesis.HealthCheck "hypothesis.HealthCheck") enum value, or as the corresponding string value. For example:

\# these two are equivalent
settings(suppress\_health\_check\=\[HealthCheck.filter\_too\_much\])
settings(suppress\_health\_check\=\["filter\_too\_much"\])

Health checks are proactive warnings, not correctness errors, so we encourage suppressing health checks where you have evaluated they will not pose a problem, or where you have evaluated that fixing the underlying issue is not worthwhile.

See also

See also the [Suppress a health check everywhere](#document-how-to/suppress-healthchecks) how-to.

_property_ deadline[¶](#hypothesis.settings.deadline "Link to this definition")

The maximum allowed duration of an individual test case, in milliseconds. You can pass an integer, float, or timedelta. If `None`, the deadline is disabled entirely.

We treat the deadline as a soft limit in some cases, where that would avoid flakiness due to timing variability.

The default deadline is 200 milliseconds. If running on CI, the default is `None` instead.

_property_ print\_blob[¶](#hypothesis.settings.print_blob "Link to this definition")

If set to `True`, Hypothesis will print code for failing examples that can be used with [`@reproduce_failure`](#hypothesis.reproduce_failure "hypothesis.reproduce_failure") to reproduce the failing example.

The default value is `False`. If running on CI, the default is `True` instead.

_property_ backend[¶](#hypothesis.settings.backend "Link to this definition")

Warning

EXPERIMENTAL AND UNSTABLE - see [Alternative backends for Hypothesis](#alternative-backends).

The importable name of a backend which Hypothesis should use to generate primitive types. We support heuristic-random, solver-based, and fuzzing-based backends.

_static_ register\_profile(_name_, _parent\=None_, _\*\*kwargs_)[¶](#hypothesis.settings.register_profile "Link to this definition")

Register a settings object as a settings profile, under the name `name`. The `parent` and `kwargs` arguments to this method are as for [`settings`](#hypothesis.settings "hypothesis.settings").

If a settings profile already exists under `name`, it will be overwritten. Registering a profile with the same name as the currently active profile will cause those changes to take effect in the active profile immediately, and do not require reloading the profile.

Registered settings profiles can be retrieved later by name with [`get_profile()`](#hypothesis.settings.get_profile "hypothesis.settings.get_profile").

_static_ get\_profile(_name_)[¶](#hypothesis.settings.get_profile "Link to this definition")

Returns the settings profile registered under `name`. If no settings profile is registered under `name`, raises [`InvalidArgument`](#hypothesis.errors.InvalidArgument "hypothesis.errors.InvalidArgument").

_static_ load\_profile(_name_)[¶](#hypothesis.settings.load_profile "Link to this definition")

Makes the settings profile registered under `name` the active profile.

If no settings profile is registered under `name`, raises [`InvalidArgument`](#hypothesis.errors.InvalidArgument "hypothesis.errors.InvalidArgument").

_static_ get\_current\_profile\_name()[¶](#hypothesis.settings.get_current_profile_name "Link to this definition")

The name of the current settings profile. For example:

\>>> settings.load\_profile("myprofile")
\>>> settings.get\_current\_profile\_name()
'myprofile'

_class_ hypothesis.Phase(_value_)[¶](#hypothesis.Phase "Link to this definition")

Options for the [`settings.phases`](#hypothesis.settings.phases "hypothesis.settings.phases") argument to [`@settings`](#hypothesis.settings "hypothesis.settings").

explicit _\= 'explicit'_[¶](#hypothesis.Phase.explicit "Link to this definition")

Controls whether explicit examples are run.

reuse _\= 'reuse'_[¶](#hypothesis.Phase.reuse "Link to this definition")

Controls whether previous examples will be reused.

generate _\= 'generate'_[¶](#hypothesis.Phase.generate "Link to this definition")

Controls whether new examples will be generated.

target _\= 'target'_[¶](#hypothesis.Phase.target "Link to this definition")

Controls whether examples will be mutated for targeting.

shrink _\= 'shrink'_[¶](#hypothesis.Phase.shrink "Link to this definition")

Controls whether examples will be shrunk.

explain _\= 'explain'_[¶](#hypothesis.Phase.explain "Link to this definition")

Controls whether Hypothesis attempts to explain test failures.

The explain phase has two parts, each of which is best-effort - if Hypothesis can’t find a useful explanation, we’ll just print the minimal failing example.

_class_ hypothesis.Verbosity(_value_)[¶](#hypothesis.Verbosity "Link to this definition")

Options for the [`settings.verbosity`](#hypothesis.settings.verbosity "hypothesis.settings.verbosity") argument to [`@settings`](#hypothesis.settings "hypothesis.settings").

quiet _\= 'quiet'_[¶](#hypothesis.Verbosity.quiet "Link to this definition")

Hypothesis will not print any output, not even the final falsifying example.

normal _\= 'normal'_[¶](#hypothesis.Verbosity.normal "Link to this definition")

Standard verbosity. Hypothesis will print the falsifying example, alongside any notes made with [`note()`](#hypothesis.note "hypothesis.note") (only for the falsfying example).

verbose _\= 'verbose'_[¶](#hypothesis.Verbosity.verbose "Link to this definition")

Increased verbosity. In addition to everything in [`Verbosity.normal`](#hypothesis.Verbosity.normal "hypothesis.Verbosity.normal"), Hypothesis will print each example as it tries it, as well as any notes made with [`note()`](#hypothesis.note "hypothesis.note") for every example. Hypothesis will also print shrinking attempts.

debug _\= 'debug'_[¶](#hypothesis.Verbosity.debug "Link to this definition")

Even more verbosity. Useful for debugging Hypothesis internals. You probably don’t want this.

_class_ hypothesis.HealthCheck(_value_)[¶](#hypothesis.HealthCheck "Link to this definition")

A [`HealthCheck`](#hypothesis.HealthCheck "hypothesis.HealthCheck") is proactively raised by Hypothesis when Hypothesis detects that your test has performance problems, which may result in less rigorous testing than you expect. For example, if your test takes a long time to generate inputs, or filters away too many inputs using [`assume()`](#hypothesis.assume "hypothesis.assume") or [`.filter()`](#hypothesis.strategies.SearchStrategy.filter "hypothesis.strategies.SearchStrategy.filter"), Hypothesis will raise a corresponding health check.

A health check is a proactive warning, not an error. We encourage suppressing health checks where you have evaluated they will not pose a problem, or where you have evaluated that fixing the underlying issue is not worthwhile.

With the exception of [`HealthCheck.function_scoped_fixture`](#hypothesis.HealthCheck.function_scoped_fixture "hypothesis.HealthCheck.function_scoped_fixture") and [`HealthCheck.differing_executors`](#hypothesis.HealthCheck.differing_executors "hypothesis.HealthCheck.differing_executors"), all health checks warn about performance problems, not correctness errors.

###### Disabling health checks[¶](#disabling-health-checks "Link to this heading")

Health checks can be disabled by [`settings.suppress_health_check`](#hypothesis.settings.suppress_health_check "hypothesis.settings.suppress_health_check"). To suppress all health checks, you can pass `suppress_health_check=list(HealthCheck)`.

See also

See also the [Suppress a health check everywhere](#document-how-to/suppress-healthchecks) how-to.

###### Correctness health checks[¶](#correctness-health-checks "Link to this heading")

Some health checks report potential correctness errors, rather than performance problems.

*   [`HealthCheck.function_scoped_fixture`](#hypothesis.HealthCheck.function_scoped_fixture "hypothesis.HealthCheck.function_scoped_fixture") indicates that a function-scoped pytest fixture is used by an [`@given`](#hypothesis.given "hypothesis.given") test. Many Hypothesis users expect function-scoped fixtures to reset once per input, but they actually reset once per test. We proactively raise [`HealthCheck.function_scoped_fixture`](#hypothesis.HealthCheck.function_scoped_fixture "hypothesis.HealthCheck.function_scoped_fixture") to ensure you have considered this case.
    
*   [`HealthCheck.differing_executors`](#hypothesis.HealthCheck.differing_executors "hypothesis.HealthCheck.differing_executors") indicates that the same [`@given`](#hypothesis.given "hypothesis.given") test has been executed multiple times with multiple distinct executors.
    

We recommend treating these particular health checks with more care, as suppressing them may result in an unsound test.

data\_too\_large _\= 'data\_too\_large'_[¶](#hypothesis.HealthCheck.data_too_large "Link to this definition")

Checks if too many examples are aborted for being too large.

This is measured by the number of random choices that Hypothesis makes in order to generate something, not the size of the generated object. For example, choosing a 100MB object from a predefined list would take only a few bits, while generating 10KB of JSON from scratch might trigger this health check.

filter\_too\_much _\= 'filter\_too\_much'_[¶](#hypothesis.HealthCheck.filter_too_much "Link to this definition")

Check for when the test is filtering out too many examples, either through use of [`assume()`](#hypothesis.assume "hypothesis.assume") or [`.filter()`](#hypothesis.strategies.SearchStrategy.filter "hypothesis.strategies.SearchStrategy.filter"), or occasionally for Hypothesis internal reasons.

too\_slow _\= 'too\_slow'_[¶](#hypothesis.HealthCheck.too_slow "Link to this definition")

Check for when input generation is very slow. Since Hypothesis generates 100 (by default) inputs per test execution, a slowdown in generating each input can result in very slow tests overall.

return\_value _\= 'return\_value'_[¶](#hypothesis.HealthCheck.return_value "Link to this definition")

Deprecated; we always error if a test returns a non-None value.

large\_base\_example _\= 'large\_base\_example'_[¶](#hypothesis.HealthCheck.large_base_example "Link to this definition")

Checks if the smallest natural input to your test is very large. This makes it difficult for Hypothesis to generate good inputs, especially when trying to shrink failing inputs.

not\_a\_test\_method _\= 'not\_a\_test\_method'_[¶](#hypothesis.HealthCheck.not_a_test_method "Link to this definition")

Deprecated; we always error if [`@given`](#hypothesis.given "hypothesis.given") is applied to a method defined by [`unittest.TestCase`](https://docs.python.org/3/library/unittest.html#unittest.TestCase "(in Python v3.14)") (i.e. not a test).

function\_scoped\_fixture _\= 'function\_scoped\_fixture'_[¶](#hypothesis.HealthCheck.function_scoped_fixture "Link to this definition")

Checks if [`@given`](#hypothesis.given "hypothesis.given") has been applied to a test with a pytest function-scoped fixture. Function-scoped fixtures run once for the whole function, not once per example, and this is usually not what you want.

Because of this limitation, tests that need to set up or reset state for every example need to do so manually within the test itself, typically using an appropriate context manager.

Suppress this health check only in the rare case that you are using a function-scoped fixture that does not need to be reset between individual examples, but for some reason you cannot use a wider fixture scope (e.g. session scope, module scope, class scope).

This check requires the [Hypothesis pytest plugin](#pytest-plugin), which is enabled by default when running Hypothesis inside pytest.

differing\_executors _\= 'differing\_executors'_[¶](#hypothesis.HealthCheck.differing_executors "Link to this definition")

Checks if [`@given`](#hypothesis.given "hypothesis.given") has been applied to a test which is executed by different [executors](#custom-function-execution). If your test function is defined as a method on a class, that class will be your executor, and subclasses executing an inherited test is a common way for things to go wrong.

The correct fix is often to bring the executor instance under the control of hypothesis by explicit parametrization over, or sampling from, subclasses, or to refactor so that [`@given`](#hypothesis.given "hypothesis.given") is specified on leaf subclasses.

nested\_given _\= 'nested\_given'_[¶](#hypothesis.HealthCheck.nested_given "Link to this definition")

Checks if [`@given`](#hypothesis.given "hypothesis.given") is used inside another [`@given`](#hypothesis.given "hypothesis.given"). This results in quadratic generation and shrinking behavior, and can usually be expressed more cleanly by using [`data()`](#hypothesis.strategies.data "hypothesis.strategies.data") to replace the inner [`@given`](#hypothesis.given "hypothesis.given").

Nesting @given can be appropriate if you set appropriate limits for the quadratic behavior and cannot easily reexpress the inner function with [`data()`](#hypothesis.strategies.data "hypothesis.strategies.data"). To suppress this health check, set `suppress_health_check=[HealthCheck.nested_given]` on the outer [`@given`](#hypothesis.given "hypothesis.given"). Setting it on the inner [`@given`](#hypothesis.given "hypothesis.given") has no effect. If you have more than one level of nesting, add a suppression for this health check to every [`@given`](#hypothesis.given "hypothesis.given") except the innermost one.

##### Database[¶](#database "Link to this heading")

_class_ hypothesis.database.ExampleDatabase[¶](#hypothesis.database.ExampleDatabase "Link to this definition")

A Hypothesis database, for use in [`settings.database`](#hypothesis.settings.database "hypothesis.settings.database").

Hypothesis automatically saves failures to the database set in [`settings.database`](#hypothesis.settings.database "hypothesis.settings.database"). The next time the test is run, Hypothesis will replay any failures from the database in [`settings.database`](#hypothesis.settings.database "hypothesis.settings.database") for that test (in [`Phase.reuse`](#hypothesis.Phase.reuse "hypothesis.Phase.reuse")).

The database is best thought of as a cache that you never need to invalidate. Entries may be transparently dropped when upgrading your Hypothesis version or changing your test. Do not rely on the database for correctness; to ensure Hypothesis always tries an input, use [`@example`](#hypothesis.example "hypothesis.example").

A Hypothesis database is a simple mapping of bytes to sets of bytes. Hypothesis provides several concrete database subclasses. To write your own database class, see [Write a custom Hypothesis database](#document-how-to/custom-database).

###### Change listening[¶](#change-listening "Link to this heading")

An optional extension to [`ExampleDatabase`](#hypothesis.database.ExampleDatabase "hypothesis.database.ExampleDatabase") is change listening. On databases which support change listening, calling [`add_listener()`](#hypothesis.database.ExampleDatabase.add_listener "hypothesis.database.ExampleDatabase.add_listener") adds a function as a change listener, which will be called whenever a value is added, deleted, or moved inside the database. See [`add_listener()`](#hypothesis.database.ExampleDatabase.add_listener "hypothesis.database.ExampleDatabase.add_listener") for details.

All databases in Hypothesis support change listening. Custom database classes are not required to support change listening, though they will not be compatible with features that require change listening until they do so.

Note

While no Hypothesis features currently require change listening, change listening is required by [HypoFuzz](https://hypofuzz.com/).

###### Database methods[¶](#database-methods "Link to this heading")

Required methods:

*   [`save()`](#hypothesis.database.ExampleDatabase.save "hypothesis.database.ExampleDatabase.save")
    
*   [`fetch()`](#hypothesis.database.ExampleDatabase.fetch "hypothesis.database.ExampleDatabase.fetch")
    
*   [`delete()`](#hypothesis.database.ExampleDatabase.delete "hypothesis.database.ExampleDatabase.delete")
    

Optional methods:

*   [`move()`](#hypothesis.database.ExampleDatabase.move "hypothesis.database.ExampleDatabase.move")
    

Change listening methods:

*   [`add_listener()`](#hypothesis.database.ExampleDatabase.add_listener "hypothesis.database.ExampleDatabase.add_listener")
    
*   [`remove_listener()`](#hypothesis.database.ExampleDatabase.remove_listener "hypothesis.database.ExampleDatabase.remove_listener")
    
*   [`clear_listeners()`](#hypothesis.database.ExampleDatabase.clear_listeners "hypothesis.database.ExampleDatabase.clear_listeners")
    
*   [`_start_listening()`](#hypothesis.database.ExampleDatabase._start_listening "hypothesis.database.ExampleDatabase._start_listening")
    
*   [`_stop_listening()`](#hypothesis.database.ExampleDatabase._stop_listening "hypothesis.database.ExampleDatabase._stop_listening")
    
*   [`_broadcast_change()`](#hypothesis.database.ExampleDatabase._broadcast_change "hypothesis.database.ExampleDatabase._broadcast_change")
    

_abstract_ save(_key_, _value_)[¶](#hypothesis.database.ExampleDatabase.save "Link to this definition")

Save `value` under `key`.

If `value` is already present in `key`, silently do nothing.

_abstract_ fetch(_key_)[¶](#hypothesis.database.ExampleDatabase.fetch "Link to this definition")

Return an iterable over all values matching this key.

_abstract_ delete(_key_, _value_)[¶](#hypothesis.database.ExampleDatabase.delete "Link to this definition")

Remove `value` from `key`.

If `value` is not present in `key`, silently do nothing.

move(_src_, _dest_, _value_)[¶](#hypothesis.database.ExampleDatabase.move "Link to this definition")

Move `value` from key `src` to key `dest`.

Equivalent to `delete(src, value)` followed by `save(src, value)`, but may have a more efficient implementation.

Note that `value` will be inserted at `dest` regardless of whether it is currently present at `src`.

add\_listener(_f_, _/_)[¶](#hypothesis.database.ExampleDatabase.add_listener "Link to this definition")

Add a change listener. `f` will be called whenever a value is saved, deleted, or moved in the database.

`f` can be called with two different event values:

*   `("save", (key, value))`
    
*   `("delete", (key, value))`
    

where `key` and `value` are both `bytes`.

There is no `move` event. Instead, a move is broadcasted as a `delete` event followed by a `save` event.

For the `delete` event, `value` may be `None`. This might occur if the database knows that a deletion has occurred in `key`, but does not know what value was deleted.

remove\_listener(_f_, _/_)[¶](#hypothesis.database.ExampleDatabase.remove_listener "Link to this definition")

Removes `f` from the list of change listeners.

If `f` is not in the list of change listeners, silently do nothing.

clear\_listeners()[¶](#hypothesis.database.ExampleDatabase.clear_listeners "Link to this definition")

Remove all change listeners.

\_broadcast\_change(_event_)[¶](#hypothesis.database.ExampleDatabase._broadcast_change "Link to this definition")

Called when a value has been either added to or deleted from a key in the underlying database store. The possible values for `event` are:

*   `("save", (key, value))`
    
*   `("delete", (key, value))`
    

`value` may be `None` for the `delete` event, indicating we know that some value was deleted under this key, but not its exact value.

Note that you should not assume your instance is the only reference to the underlying database store. For example, if two instances of [`DirectoryBasedExampleDatabase`](#hypothesis.database.DirectoryBasedExampleDatabase "hypothesis.database.DirectoryBasedExampleDatabase") reference the same directory, \_broadcast\_change should be called whenever a file is added or removed from the directory, even if that database was not responsible for changing the file.

\_start\_listening()[¶](#hypothesis.database.ExampleDatabase._start_listening "Link to this definition")

Called when the database adds a change listener, and did not previously have any change listeners. Intended to allow databases to wait to start expensive listening operations until necessary.

`_start_listening` and `_stop_listening` are guaranteed to alternate, so you do not need to handle the case of multiple consecutive `_start_listening` calls without an intermediate `_stop_listening` call.

\_stop\_listening()[¶](#hypothesis.database.ExampleDatabase._stop_listening "Link to this definition")

Called whenever no change listeners remain on the database.

`_stop_listening` and `_start_listening` are guaranteed to alternate, so you do not need to handle the case of multiple consecutive `_stop_listening` calls without an intermediate `_start_listening` call.

_class_ hypothesis.database.InMemoryExampleDatabase[¶](#hypothesis.database.InMemoryExampleDatabase "Link to this definition")

A non-persistent example database, implemented in terms of an in-memory dictionary.

This can be useful if you call a test function several times in a single session, or for testing other database implementations, but because it does not persist between runs we do not recommend it for general use.

_class_ hypothesis.database.DirectoryBasedExampleDatabase(_path_)[¶](#hypothesis.database.DirectoryBasedExampleDatabase "Link to this definition")

Use a directory to store Hypothesis examples as files.

Each test corresponds to a directory, and each example to a file within that directory. While the contents are fairly opaque, a [`DirectoryBasedExampleDatabase`](#hypothesis.database.DirectoryBasedExampleDatabase "hypothesis.database.DirectoryBasedExampleDatabase") can be shared by checking the directory into version control, for example with the following `.gitignore`:

\# Ignore files cached by Hypothesis...
.hypothesis/\*
# except for the examples directory
!.hypothesis/examples/

Note however that this only makes sense if you also pin to an exact version of Hypothesis, and we would usually recommend implementing a shared database with a network datastore - see [`ExampleDatabase`](#hypothesis.database.ExampleDatabase "hypothesis.database.ExampleDatabase"), and the [`MultiplexedDatabase`](#hypothesis.database.MultiplexedDatabase "hypothesis.database.MultiplexedDatabase") helper.

_class_ hypothesis.database.GitHubArtifactDatabase(

_owner_,

_repo_,

_artifact\_name\='hypothesis-example-db'_,

_cache\_timeout\=datetime.timedelta(days=1)_,

_path\=None_,

)[¶](#hypothesis.database.GitHubArtifactDatabase "Link to this definition")

A file-based database loaded from a [GitHub Actions](https://docs.github.com/en/actions) artifact.

You can use this for sharing example databases between CI runs and developers, allowing the latter to get read-only access to the former. This is particularly useful for continuous fuzzing (i.e. with [HypoFuzz](https://hypofuzz.com/)), where the CI system can help find new failing examples through fuzzing, and developers can reproduce them locally without any manual effort.

Note

You must provide `GITHUB_TOKEN` as an environment variable. In CI, Github Actions provides this automatically, but it needs to be set manually for local usage. In a developer machine, this would usually be a [Personal Access Token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens). If the repository is private, it’s necessary for the token to have `repo` scope in the case of a classic token, or `actions:read` in the case of a fine-grained token.

In most cases, this will be used through the [`MultiplexedDatabase`](#hypothesis.database.MultiplexedDatabase "hypothesis.database.MultiplexedDatabase"), by combining a local directory-based database with this one. For example:

local \= DirectoryBasedExampleDatabase(".hypothesis/examples")
shared \= ReadOnlyDatabase(GitHubArtifactDatabase("user", "repo"))

settings.register\_profile("ci", database\=local)
settings.register\_profile("dev", database\=MultiplexedDatabase(local, shared))
\# We don't want to use the shared database in CI, only to populate its local one.
\# which the workflow should then upload as an artifact.
settings.load\_profile("ci" if os.environ.get("CI") else "dev")

Note

Because this database is read-only, you always need to wrap it with the [`ReadOnlyDatabase`](#hypothesis.database.ReadOnlyDatabase "hypothesis.database.ReadOnlyDatabase").

A setup like this can be paired with a GitHub Actions workflow including something like the following:

\- name: Download example database
  uses: dawidd6/action-download-artifact@v9
  with:
    name: hypothesis-example-db
    path: .hypothesis/examples
    if\_no\_artifact\_found: warn
    workflow\_conclusion: completed

\- name: Run tests
  run: pytest

\- name: Upload example database
  uses: actions/upload-artifact@v3
  if: always()
  with:
    name: hypothesis-example-db
    path: .hypothesis/examples

In this workflow, we use [dawidd6/action-download-artifact](https://github.com/dawidd6/action-download-artifact) to download the latest artifact given that the official [actions/download-artifact](https://github.com/actions/download-artifact) does not support downloading artifacts from previous workflow runs.

The database automatically implements a simple file-based cache with a default expiration period of 1 day. You can adjust this through the `cache_timeout` property.

For mono-repo support, you can provide a unique `artifact_name` (e.g. `hypofuzz-example-db-frontend`).

_class_ hypothesis.database.ReadOnlyDatabase(_db_)[¶](#hypothesis.database.ReadOnlyDatabase "Link to this definition")

A wrapper to make the given database read-only.

The implementation passes through `fetch`, and turns `save`, `delete`, and `move` into silent no-ops.

Note that this disables Hypothesis’ automatic discarding of stale examples. It is designed to allow local machines to access a shared database (e.g. from CI servers), without propagating changes back from a local or in-development branch.

_class_ hypothesis.database.MultiplexedDatabase(_\*dbs_)[¶](#hypothesis.database.MultiplexedDatabase "Link to this definition")

A wrapper around multiple databases.

Each `save`, `fetch`, `move`, or `delete` operation will be run against all of the wrapped databases. `fetch` does not yield duplicate values, even if the same value is present in two or more of the wrapped databases.

This combines well with a [`ReadOnlyDatabase`](#hypothesis.database.ReadOnlyDatabase "hypothesis.database.ReadOnlyDatabase"), as follows:

local \= DirectoryBasedExampleDatabase("/tmp/hypothesis/examples/")
shared \= CustomNetworkDatabase()

settings.register\_profile("ci", database\=shared)
settings.register\_profile(
    "dev", database\=MultiplexedDatabase(local, ReadOnlyDatabase(shared))
)
settings.load\_profile("ci" if os.environ.get("CI") else "dev")

So your CI system or fuzzing runs can populate a central shared database; while local runs on development machines can reproduce any failures from CI but will only cache their own failures locally and cannot remove examples from the shared database.

_class_ hypothesis.database.BackgroundWriteDatabase(_db_)[¶](#hypothesis.database.BackgroundWriteDatabase "Link to this definition")

A wrapper which defers writes on the given database to a background thread.

Calls to [`fetch()`](#hypothesis.database.ExampleDatabase.fetch "hypothesis.database.ExampleDatabase.fetch") wait for any enqueued writes to finish before fetching from the database.

_class_ hypothesis.extra.redis.RedisExampleDatabase(

_redis_,

_\*_,

_expire\_after\=datetime.timedelta(days=8)_,

_key\_prefix\=b'hypothesis-example:'_,

_listener\_channel\='hypothesis-changes'_,

)[¶](#hypothesis.extra.redis.RedisExampleDatabase "Link to this definition")

Store Hypothesis examples as sets in the given [`Redis`](https://redis.readthedocs.io/en/stable/connections.html#redis.Redis "(in redis-py v7.1.0)") datastore.

This is particularly useful for shared databases, as per the recipe for a [`MultiplexedDatabase`](#hypothesis.database.MultiplexedDatabase "hypothesis.database.MultiplexedDatabase").

Note

If a test has not been run for `expire_after`, those examples will be allowed to expire. The default time-to-live persists examples between weekly runs.

##### Stateful tests[¶](#stateful-tests "Link to this heading")

_class_ hypothesis.stateful.RuleBasedStateMachine[¶](#hypothesis.stateful.RuleBasedStateMachine "Link to this definition")

A RuleBasedStateMachine gives you a structured way to define state machines.

The idea is that a state machine carries the system under test and some supporting data. This data can be stored in instance variables or divided into Bundles. The state machine has a set of rules which may read data from bundles (or just from normal strategies), push data onto bundles, change the state of the machine, or verify properties. At any given point a random applicable rule will be executed.

###### Rules[¶](#rules "Link to this heading")

hypothesis.stateful.rule(_\*_, _targets\=()_, _target\=None_, _\*\*kwargs_)[¶](#hypothesis.stateful.rule "Link to this definition")

Decorator for RuleBasedStateMachine. Any Bundle present in `target` or `targets` will define where the end result of this function should go. If both are empty then the end result will be discarded.

`target` must be a Bundle, or if the result should be replicated to multiple bundles you can pass a tuple of them as the `targets` argument. It is invalid to use both arguments for a single rule. If the result should go to exactly one of several bundles, define a separate rule for each case.

kwargs then define the arguments that will be passed to the function invocation. If their value is a Bundle, or if it is `consumes(b)` where `b` is a Bundle, then values that have previously been produced for that bundle will be provided. If `consumes` is used, the value will also be removed from the bundle.

Any other kwargs should be strategies and values from them will be provided.

hypothesis.stateful.consumes(_bundle_)[¶](#hypothesis.stateful.consumes "Link to this definition")

When introducing a rule in a RuleBasedStateMachine, this function can be used to mark bundles from which each value used in a step with the given rule should be removed. This function returns a strategy object that can be manipulated and combined like any other.

For example, a rule declared with

`@rule(value1=b1, value2=consumes(b2), value3=lists(consumes(b3)))`

will consume a value from Bundle `b2` and several values from Bundle `b3` to populate `value2` and `value3` each time it is executed.

hypothesis.stateful.multiple(_\*args_)[¶](#hypothesis.stateful.multiple "Link to this definition")

This function can be used to pass multiple results to the target(s) of a rule. Just use `return multiple(result1, result2, ...)` in your rule.

It is also possible to use `return multiple()` with no arguments in order to end a rule without passing any result.

_class_ hypothesis.stateful.Bundle(_name_, _\*_, _consume\=False_, _draw\_references\=True_)[¶](#hypothesis.stateful.Bundle "Link to this definition")

A collection of values for use in stateful testing.

Bundles are a kind of strategy where values can be added by rules, and (like any strategy) used as inputs to future rules.

The `name` argument they are passed is the they are referred to internally by the state machine; no two bundles may have the same name. It is idiomatic to use the attribute being assigned to as the name of the Bundle:

class MyStateMachine(RuleBasedStateMachine):
    keys \= Bundle("keys")

Bundles can contain the same value more than once; this becomes relevant when using [`consumes()`](#hypothesis.stateful.consumes "hypothesis.stateful.consumes") to remove values again.

If the `consume` argument is set to True, then all values that are drawn from this bundle will be consumed (as above) when requested.

hypothesis.stateful.initialize(_\*_, _targets\=()_, _target\=None_, _\*\*kwargs_)[¶](#hypothesis.stateful.initialize "Link to this definition")

Decorator for RuleBasedStateMachine.

An initialize decorator behaves like a rule, but all `@initialize()` decorated methods will be called before any `@rule()` decorated methods, in an arbitrary order. Each `@initialize()` method will be called exactly once per run, unless one raises an exception - after which only the `.teardown()` method will be run. `@initialize()` methods may not have preconditions.

hypothesis.stateful.precondition(_precond_)[¶](#hypothesis.stateful.precondition "Link to this definition")

Decorator to apply a precondition for rules in a RuleBasedStateMachine. Specifies a precondition for a rule to be considered as a valid step in the state machine, which is more efficient than using [`assume()`](#hypothesis.assume "hypothesis.assume") within the rule. The `precond` function will be called with the instance of RuleBasedStateMachine and should return True or False. Usually it will need to look at attributes on that instance.

For example:

class MyTestMachine(RuleBasedStateMachine):
    state \= 1

    @precondition(lambda self: self.state != 0)
    @rule(numerator\=integers())
    def divide\_with(self, numerator):
        self.state \= numerator / self.state

If multiple preconditions are applied to a single rule, it is only considered a valid step when all of them return True. Preconditions may be applied to invariants as well as rules.

hypothesis.stateful.invariant(_\*_, _check\_during\_init\=False_)[¶](#hypothesis.stateful.invariant "Link to this definition")

Decorator to apply an invariant for rules in a RuleBasedStateMachine. The decorated function will be run after every rule and can raise an exception to indicate failed invariants.

For example:

class MyTestMachine(RuleBasedStateMachine):
    state \= 1

    @invariant()
    def is\_nonzero(self):
        assert self.state != 0

By default, invariants are only checked after all [`@initialize()`](#hypothesis.stateful.initialize "hypothesis.stateful.initialize") rules have been run. Pass `check_during_init=True` for invariants which can also be checked during initialization.

###### Running state machines[¶](#running-state-machines "Link to this heading")

If you want to bypass the TestCase infrastructure you can invoke these manually. The stateful module exposes [`run_state_machine_as_test()`](#hypothesis.stateful.run_state_machine_as_test "hypothesis.stateful.run_state_machine_as_test"), which takes an arbitrary function returning a [`RuleBasedStateMachine`](#hypothesis.stateful.RuleBasedStateMachine "hypothesis.stateful.RuleBasedStateMachine") and an optional settings parameter and does the same as the class based runTest provided.

hypothesis.stateful.run\_state\_machine\_as\_test(

_state\_machine\_factory_,

_\*_,

_settings\=None_,

_\_min\_steps\=0_,

)[¶](#hypothesis.stateful.run_state_machine_as_test "Link to this definition")

Run a state machine definition as a test, either silently doing nothing or printing a minimal breaking program and raising an exception.

state\_machine\_factory is anything which returns an instance of RuleBasedStateMachine when called with no arguments - it can be a class or a function. settings will be used to control the execution of the test.

##### Hypothesis exceptions[¶](#hypothesis-exceptions "Link to this heading")

Custom exceptions raised by Hypothesis.

_class_ hypothesis.errors.HypothesisException[¶](#hypothesis.errors.HypothesisException "Link to this definition")

Generic parent class for exceptions thrown by Hypothesis.

_class_ hypothesis.errors.HypothesisDeprecationWarning[¶](#hypothesis.errors.HypothesisDeprecationWarning "Link to this definition")

A deprecation warning issued by Hypothesis.

Actually inherits from FutureWarning, because DeprecationWarning is hidden by the default warnings filter.

You can configure the [`warnings`](https://docs.python.org/3/library/warnings.html#module-warnings "(in Python v3.14)") module to handle these warnings differently to others, either turning them into errors or suppressing them entirely. Obviously we would prefer the former!

_class_ hypothesis.errors.Flaky[¶](#hypothesis.errors.Flaky "Link to this definition")

Base class for indeterministic failures. Usually one of the more specific subclasses ([`FlakyFailure`](#hypothesis.errors.FlakyFailure "hypothesis.errors.FlakyFailure") or [`FlakyStrategyDefinition`](#hypothesis.errors.FlakyStrategyDefinition "hypothesis.errors.FlakyStrategyDefinition")) is raised.

See also

See also the [flaky failures tutorial](#document-tutorial/flaky).

_class_ hypothesis.errors.FlakyStrategyDefinition[¶](#hypothesis.errors.FlakyStrategyDefinition "Link to this definition")

This function appears to cause inconsistent data generation.

Common causes for this problem are:

1.  The strategy depends on external state. e.g. it uses an external random number generator. Try to make a version that passes all the relevant state in from Hypothesis.
    

See also

See also the [flaky failures tutorial](#document-tutorial/flaky).

_class_ hypothesis.errors.FlakyFailure(_msg_, _group_)[¶](#hypothesis.errors.FlakyFailure "Link to this definition")

This function appears to fail non-deterministically: We have seen it fail when passed this example at least once, but a subsequent invocation did not fail, or caused a distinct error.

Common causes for this problem are:

1.  The function depends on external state. e.g. it uses an external random number generator. Try to make a version that passes all the relevant state in from Hypothesis.
    
2.  The function is suffering from too much recursion and its failure depends sensitively on where it’s been called from.
    
3.  The function is timing sensitive and can fail or pass depending on how long it takes. Try breaking it up into smaller functions which don’t do that and testing those instead.
    

See also

See also the [flaky failures tutorial](#document-tutorial/flaky).

_class_ hypothesis.errors.FlakyBackendFailure(_msg_, _group_)[¶](#hypothesis.errors.FlakyBackendFailure "Link to this definition")

A failure was reported by an [alternative backend](#alternative-backends), but this failure did not reproduce when replayed under the Hypothesis backend.

When an alternative backend reports a failure, Hypothesis first replays it under the standard Hypothesis backend to check for flakiness. If the failure does not reproduce, Hypothesis raises this exception.

_class_ hypothesis.errors.InvalidArgument[¶](#hypothesis.errors.InvalidArgument "Link to this definition")

Used to indicate that the arguments to a Hypothesis function were in some manner incorrect.

_class_ hypothesis.errors.ResolutionFailed[¶](#hypothesis.errors.ResolutionFailed "Link to this definition")

Hypothesis had to resolve a type to a strategy, but this failed.

Type inference is best-effort, so this only happens when an annotation exists but could not be resolved for a required argument to the target of `builds()`, or where the user passed `...`.

_class_ hypothesis.errors.Unsatisfiable[¶](#hypothesis.errors.Unsatisfiable "Link to this definition")

We ran out of time or examples before we could find enough examples which satisfy the assumptions of this hypothesis.

This could be because the function is too slow. If so, try upping the timeout. It could also be because the function is using assume in a way that is too hard to satisfy. If so, try writing a custom strategy or using a better starting point (e.g if you are requiring a list has unique values you could instead filter out all duplicate values from the list)

_class_ hypothesis.errors.DidNotReproduce[¶](#hypothesis.errors.DidNotReproduce "Link to this definition")

_class_ hypothesis.errors.DeadlineExceeded(_runtime_, _deadline_)[¶](#hypothesis.errors.DeadlineExceeded "Link to this definition")

Raised when an input takes too long to run, relative to the [`settings.deadline`](#hypothesis.settings.deadline "hypothesis.settings.deadline") setting.

##### Django[¶](#django "Link to this heading")

See also

See the [Django strategies reference](#django-strategies) for documentation on strategies in the `hypothesis.extra.django` module.

Hypothesis offers a number of features specific for Django testing, available in the `hypothesis[django]` [extra](#document-extras). This is tested against each supported series with mainstream or extended support - if you’re still getting security patches, you can test with Hypothesis.

_class_ hypothesis.extra.django.TestCase(_\*args_, _\*\*kwargs_)[¶](#hypothesis.extra.django.TestCase "Link to this definition")

Using it is quite straightforward: All you need to do is subclass [`hypothesis.extra.django.TestCase`](#hypothesis.extra.django.TestCase "hypothesis.extra.django.TestCase") or [`hypothesis.extra.django.SimpleTestCase`](#hypothesis.extra.django.SimpleTestCase "hypothesis.extra.django.SimpleTestCase") or [`hypothesis.extra.django.TransactionTestCase`](#hypothesis.extra.django.TransactionTestCase "hypothesis.extra.django.TransactionTestCase") or [`LiveServerTestCase`](#hypothesis.extra.django.LiveServerTestCase "hypothesis.extra.django.LiveServerTestCase") or [`StaticLiveServerTestCase`](#hypothesis.extra.django.StaticLiveServerTestCase "hypothesis.extra.django.StaticLiveServerTestCase") and you can use [`@given`](#hypothesis.given "hypothesis.given") as normal, and the transactions will be per example rather than per test function as they would be if you used [`@given`](#hypothesis.given "hypothesis.given") with a normal django test suite (this is important because your test function will be called multiple times and you don’t want them to interfere with each other). Test cases on these classes that do not use [`@given`](#hypothesis.given "hypothesis.given") will be run as normal for [`django.test.TestCase`](http://docs.djangoproject.com/en/stable/topics/testing/tools/#django.test.TestCase "(in Django v5.2)") or [`django.test.TransactionTestCase`](http://docs.djangoproject.com/en/stable/topics/testing/tools/#django.test.TransactionTestCase "(in Django v5.2)").

_class_ hypothesis.extra.django.SimpleTestCase(_\*args_, _\*\*kwargs_)[¶](#hypothesis.extra.django.SimpleTestCase "Link to this definition")

_class_ hypothesis.extra.django.TransactionTestCase(_\*args_, _\*\*kwargs_)[¶](#hypothesis.extra.django.TransactionTestCase "Link to this definition")

_class_ hypothesis.extra.django.LiveServerTestCase(_\*args_, _\*\*kwargs_)[¶](#hypothesis.extra.django.LiveServerTestCase "Link to this definition")

_class_ hypothesis.extra.django.StaticLiveServerTestCase(_\*args_, _\*\*kwargs_)[¶](#hypothesis.extra.django.StaticLiveServerTestCase "Link to this definition")

We recommend avoiding [`TransactionTestCase`](#hypothesis.extra.django.TransactionTestCase "hypothesis.extra.django.TransactionTestCase") unless you really have to run each test case in a database transaction. Because Hypothesis runs this in a loop, the performance problems [`django.test.TransactionTestCase`](http://docs.djangoproject.com/en/stable/topics/testing/tools/#django.test.TransactionTestCase "(in Django v5.2)") normally has are significantly exacerbated and your tests will be really slow. If you are using [`TransactionTestCase`](#hypothesis.extra.django.TransactionTestCase "hypothesis.extra.django.TransactionTestCase"), you may need to use `@settings(suppress_health_check=[HealthCheck.too_slow])` to avoid a [`HealthCheck`](#hypothesis.HealthCheck "hypothesis.HealthCheck") error due to slow example generation.

Having set up a test class, you can now pass [`@given`](#hypothesis.given "hypothesis.given") a strategy for Django models with [`from_model()`](#hypothesis.extra.django.from_model "hypothesis.extra.django.from_model"). For example, using [the trivial django project we have for testing](https://github.com/HypothesisWorks/hypothesis/blob/master/hypothesis-python/tests/django/toystore/models.py):

\>>> from hypothesis.extra.django import from\_model
\>>> from toystore.models import Customer
\>>> c \= from\_model(Customer).example()
\>>> c
<Customer: Customer object>
\>>> c.email
'jaime.urbina@gmail.com'
\>>> c.name
'\\U00109d3d\\U000e07be\\U000165f8\\U0003fabf\\U000c12cd\\U000f1910\\U00059f12\\U000519b0\\U0003fabf\\U000f1910\\U000423fb\\U000423fb\\U00059f12\\U000e07be\\U000c12cd\\U000e07be\\U000519b0\\U000165f8\\U0003fabf\\U0007bc31'
\>>> c.age
\-873375803

Hypothesis has just created this with whatever the relevant type of data is.

Obviously the customer’s age is implausible, which is only possible because we have not used (eg) [`MinValueValidator`](http://docs.djangoproject.com/en/stable/ref/validators/#django.core.validators.MinValueValidator "(in Django v5.2)") to set the valid range for this field (or used a [`PositiveSmallIntegerField`](http://docs.djangoproject.com/en/stable/ref/models/fields/#django.db.models.PositiveSmallIntegerField "(in Django v5.2)"), which would only need a maximum value validator).

If you _do_ have validators attached, Hypothesis will only generate examples that pass validation. Sometimes that will mean that we fail a [`HealthCheck`](#hypothesis.HealthCheck "hypothesis.HealthCheck") because of the filtering, so let’s explicitly pass a strategy to skip validation at the strategy level:

\>>> from hypothesis.strategies import integers
\>>> c \= from\_model(Customer, age\=integers(min\_value\=0, max\_value\=120)).example()
\>>> c
<Customer: Customer object>
\>>> c.age
5

###### Custom field types[¶](#custom-field-types "Link to this heading")

If you have a custom Django field type you can register it with Hypothesis’s model deriving functionality by registering a default strategy for it:

\>>> from toystore.models import CustomishField, Customish
\>>> from\_model(Customish).example()
hypothesis.errors.InvalidArgument: Missing arguments for mandatory field
    customish for model Customish
\>>> from hypothesis.extra.django import register\_field\_strategy
\>>> from hypothesis.strategies import just
\>>> register\_field\_strategy(CustomishField, just("hi"))
\>>> x \= from\_model(Customish).example()
\>>> x.customish
'hi'

Note that this mapping is on exact type. Subtypes will not inherit it.

###### Generating child models[¶](#generating-child-models "Link to this heading")

For the moment there’s no explicit support in hypothesis-django for generating dependent models. i.e. a Company model will generate no Shops. However if you want to generate some dependent models as well, you can emulate this by using the [`.flatmap()`](#hypothesis.strategies.SearchStrategy.flatmap "hypothesis.strategies.SearchStrategy.flatmap") function as follows:

from hypothesis.strategies import just, lists

def generate\_with\_shops(company):
    return lists(from\_model(Shop, company\=just(company))).map(lambda \_: company)

company\_with\_shops\_strategy \= from\_model(Company).flatmap(generate\_with\_shops)

Let’s unpack what this is doing:

The way flatmap works is that we draw a value from the original strategy, then apply a function to it which gives us a new strategy. We then draw a value from _that_ strategy. So in this case we’re first drawing a company, and then we’re drawing a list of shops belonging to that company: The [`just()`](#hypothesis.strategies.just "hypothesis.strategies.just") strategy is a strategy such that drawing it always produces the individual value, so `from_model(Shop, company=just(company))` is a strategy that generates a Shop belonging to the original company.

So the following code would give us a list of shops all belonging to the same company:

from\_model(Company).flatmap(lambda c: lists(from\_model(Shop, company\=just(c))))

The only difference from this and the above is that we want the company, not the shops. This is where the inner map comes in. We build the list of shops and then throw it away, instead returning the company we started for. This works because the models that Hypothesis generates are saved in the database, so we’re essentially running the inner strategy purely for the side effect of creating those children in the database.

###### Generating primary key values[¶](#generating-primary-key-values "Link to this heading")

If your model includes a custom primary key that you want to generate using a strategy (rather than a default auto-increment primary key) then Hypothesis has to deal with the possibility of a duplicate primary key.

If a model strategy generates a value for the primary key field, Hypothesis will create the model instance with [`update_or_create()`](http://docs.djangoproject.com/en/stable/ref/models/querysets/#django.db.models.query.QuerySet.update_or_create "(in Django v5.2)"), overwriting any existing instance in the database for this test case with the same primary key.

###### On the subject of `MultiValueField`[¶](#on-the-subject-of-multivaluefield "Link to this heading")

Django forms feature the [`MultiValueField`](http://docs.djangoproject.com/en/stable/ref/forms/fields/#django.forms.MultiValueField "(in Django v5.2)") which allows for several fields to be combined under a single named field, the default example of this is the [`SplitDateTimeField`](http://docs.djangoproject.com/en/stable/ref/forms/fields/#django.forms.SplitDateTimeField "(in Django v5.2)").

class CustomerForm(forms.Form):
    name \= forms.CharField()
    birth\_date\_time \= forms.SplitDateTimeField()

[`from_form()`](#hypothesis.extra.django.from_form "hypothesis.extra.django.from_form") supports `MultiValueField` subclasses directly, however if you want to define your own strategy be forewarned that Django binds data for a `MultiValueField` in a peculiar way. Specifically each sub-field is expected to have its own entry in `data` addressed by the field name (e.g. `birth_date_time`) and the index of the sub-field within the `MultiValueField`, so form `data` for the example above might look like this:

{
    "name": "Samuel John",
    "birth\_date\_time\_0": "2018-05-19",  \# the date, as the first sub-field
    "birth\_date\_time\_1": "15:18:00",  \# the time, as the second sub-field
}

Thus, if you want to define your own strategies for such a field you must address your sub-fields appropriately:

from\_form(CustomerForm, birth\_date\_time\_0\=just("2018-05-19"))

##### External fuzzers[¶](#external-fuzzers "Link to this heading")

hypothesis.core.HypothesisHandle.fuzz\_one\_input _\= <property object>_[¶](#hypothesis.core.HypothesisHandle.fuzz_one_input "Link to this definition")

Run the test as a fuzz target, driven with the `buffer` of bytes.

Depending on the passed `buffer` one of three things will happen:

*   If the bytestring was invalid, for example because it was too short or was filtered out by [`assume()`](#hypothesis.assume "hypothesis.assume") or [`.filter()`](#hypothesis.strategies.SearchStrategy.filter "hypothesis.strategies.SearchStrategy.filter"), [`fuzz_one_input()`](#hypothesis.core.HypothesisHandle.fuzz_one_input "hypothesis.core.HypothesisHandle.fuzz_one_input") returns `None`.
    
*   If the bytestring was valid and the test passed, [`fuzz_one_input()`](#hypothesis.core.HypothesisHandle.fuzz_one_input "hypothesis.core.HypothesisHandle.fuzz_one_input") returns a canonicalised and pruned bytestring which will replay that test case. This is provided as an option to improve the performance of mutating fuzzers, but can safely be ignored.
    
*   If the test _failed_, i.e. raised an exception, [`fuzz_one_input()`](#hypothesis.core.HypothesisHandle.fuzz_one_input "hypothesis.core.HypothesisHandle.fuzz_one_input") will add the pruned buffer to [the Hypothesis example database](#database) and then re-raise that exception. All you need to do to reproduce, minimize, and de-duplicate all the failures found via fuzzing is run your test suite!
    

To reduce the performance impact of database writes, [`fuzz_one_input()`](#hypothesis.core.HypothesisHandle.fuzz_one_input "hypothesis.core.HypothesisHandle.fuzz_one_input") only records failing inputs which would be valid shrinks for a known failure - meaning writes are somewhere between constant and log(N) rather than linear in runtime. However, this tracking only works within a persistent fuzzing process; for forkserver fuzzers we recommend `database=None` for the main run, and then replaying with a database enabled if you need to analyse failures.

Note that the interpretation of both input and output bytestrings is specific to the exact version of Hypothesis you are using and the strategies given to the test, just like the [database](#database) and [`@reproduce_failure`](#hypothesis.reproduce_failure "hypothesis.reproduce_failure").

###### Interaction with [`@settings`](#hypothesis.settings "hypothesis.settings")[¶](#interaction-with-settings "Link to this heading")

[`fuzz_one_input()`](#hypothesis.core.HypothesisHandle.fuzz_one_input "hypothesis.core.HypothesisHandle.fuzz_one_input") uses just enough of Hypothesis’ internals to drive your test function with a bytestring, and most settings therefore have no effect in this mode. We recommend running your tests the usual way before fuzzing to get the benefits of health checks, as well as afterwards to replay, shrink, deduplicate, and report whatever errors were discovered.

*   [`settings.database`](#hypothesis.settings.database "hypothesis.settings.database") _is_ used by [`fuzz_one_input()`](#hypothesis.core.HypothesisHandle.fuzz_one_input "hypothesis.core.HypothesisHandle.fuzz_one_input") - adding failures to the database to be replayed when you next run your tests is our preferred reporting mechanism and response to [the ‘fuzzer taming’ problem](https://blog.regehr.org/archives/925).
    
*   [`settings.verbosity`](#hypothesis.settings.verbosity "hypothesis.settings.verbosity") and [`settings.stateful_step_count`](#hypothesis.settings.stateful_step_count "hypothesis.settings.stateful_step_count") work as usual.
    
*   The [`deadline`](#hypothesis.settings.deadline "hypothesis.settings.deadline"), [`derandomize`](#hypothesis.settings.derandomize "hypothesis.settings.derandomize"), [`max_examples`](#hypothesis.settings.max_examples "hypothesis.settings.max_examples"), [`phases`](#hypothesis.settings.phases "hypothesis.settings.phases"), [`print_blob`](#hypothesis.settings.print_blob "hypothesis.settings.print_blob"), [`report_multiple_bugs`](#hypothesis.settings.report_multiple_bugs "hypothesis.settings.report_multiple_bugs"), and [`suppress_health_check`](#hypothesis.settings.suppress_health_check "hypothesis.settings.suppress_health_check") settings do not affect [`fuzz_one_input()`](#hypothesis.core.HypothesisHandle.fuzz_one_input "hypothesis.core.HypothesisHandle.fuzz_one_input").
    

###### Example Usage[¶](#example-usage "Link to this heading")

@given(st.text())
def test\_foo(s): ...

\# This is a traditional fuzz target - call it with a bytestring,
\# or a binary IO object, and it runs the test once.
fuzz\_target \= test\_foo.hypothesis.fuzz\_one\_input

\# For example:
fuzz\_target(b"\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00")
fuzz\_target(io.BytesIO(b"\\x01"))

Tip

If you expect to discover many failures while using [`fuzz_one_input()`](#hypothesis.core.HypothesisHandle.fuzz_one_input "hypothesis.core.HypothesisHandle.fuzz_one_input"), consider wrapping your database with [`BackgroundWriteDatabase`](#hypothesis.database.BackgroundWriteDatabase "hypothesis.database.BackgroundWriteDatabase"), for low-overhead writes of failures.

Tip

Want an integrated workflow for your team’s local tests, CI, and continuous fuzzing?

Use [HypoFuzz](https://hypofuzz.com/) to fuzz your whole test suite, and find more bugs with the same tests!

See also

See also the [Use Hypothesis with an external fuzzer](#document-how-to/external-fuzzers) how-to.

##### Custom function execution[¶](#custom-function-execution "Link to this heading")

Hypothesis provides you with a hook that lets you control how it runs examples.

This lets you do things like set up and tear down around each example, run examples in a subprocess, transform coroutine tests into normal tests, etc. For example, [`TransactionTestCase`](#hypothesis.extra.django.TransactionTestCase "hypothesis.extra.django.TransactionTestCase") in the Django extra runs each example in a separate database transaction.

The way this works is by introducing the concept of an executor. An executor is essentially a function that takes a block of code and run it. The default executor is:

def default\_executor(function):
    return function()

You define executors by defining a method `execute_example` on a class. Any test methods on that class with [`@given`](#hypothesis.given "hypothesis.given") used on them will use `self.execute_example` as an executor with which to run tests. For example, the following executor runs all its code twice:

from unittest import TestCase

class TestTryReallyHard(TestCase):
    @given(integers())
    def test\_something(self, i):
        perform\_some\_unreliable\_operation(i)

    def execute\_example(self, f):
        f()
        return f()

Note: The functions you use in map, etc. will run _inside_ the executor. i.e. they will not be called until you invoke the function passed to `execute_example`.

An executor must be able to handle being passed a function which returns None, otherwise it won’t be able to run normal test cases. So for example the following executor is invalid:

from unittest import TestCase

class TestRunTwice(TestCase):
    def execute\_example(self, f):
        return f()()

and should be rewritten as:

from unittest import TestCase

class TestRunTwice(TestCase):
    def execute\_example(self, f):
        result \= f()
        if callable(result):
            result \= result()
        return result

An alternative hook is provided for use by test runner extensions such as [pytest-trio](https://pypi.org/project/pytest-trio/), which cannot use the `execute_example` method. This is **not** recommended for end-users - it is better to write a complete test function directly, perhaps by using a decorator to perform the same transformation before applying [`@given`](#hypothesis.given "hypothesis.given").

@given(x\=integers())
@pytest.mark.trio
async def test(x): ...

\# Illustrative code, inside the pytest-trio plugin
test.hypothesis.inner\_test \= lambda x: trio.run(test, x)

For authors of test runners however, assigning to the `inner_test` attribute of the `hypothesis` attribute of the test will replace the interior test.

Note

The new `inner_test` must accept and pass through all the `*args` and `**kwargs` expected by the original test.

If the end user has also specified a custom executor using the `execute_example` method, it - and all other execution-time logic - will be applied to the _new_ inner test assigned by the test runner.

##### Detection[¶](#detection "Link to this heading")

hypothesis.is\_hypothesis\_test(_f_)[¶](#hypothesis.is_hypothesis_test "Link to this definition")

Returns `True` if `f` represents a test function that has been defined with Hypothesis. This is true for:

*   Functions decorated with [`@given`](#hypothesis.given "hypothesis.given")
    
*   The `runTest` method of stateful tests
    

For example:

@given(st.integers())
def f(n): ...

class MyStateMachine(RuleBasedStateMachine): ...

assert is\_hypothesis\_test(f)
assert is\_hypothesis\_test(MyStateMachine.TestCase().runTest)

See also

See also the [Detect Hypothesis tests](#document-how-to/detect-hypothesis-tests) how-to.

hypothesis.currently\_in\_test\_context()[¶](#hypothesis.currently_in_test_context "Link to this definition")

Return `True` if the calling code is currently running inside an [`@given`](#hypothesis.given "hypothesis.given") or [stateful](#stateful) test, and `False` otherwise.

This is useful for third-party integrations and assertion helpers which may be called from either traditional or property-based tests, and can only use e.g. [`assume()`](#hypothesis.assume "hypothesis.assume") or [`target()`](#hypothesis.target "hypothesis.target") in the latter case.

#### Strategies Reference[¶](#strategies-reference "Link to this heading")

Strategies are the way Hypothesis describes the values for [`@given`](#hypothesis.given "hypothesis.given") to generate. For instance, passing the strategy `st.lists(st.integers(), min_size=1)` to [`@given`](#hypothesis.given "hypothesis.given") tells Hypothesis to generate lists of integers with at least one element.

This reference page lists all of Hypothesis’ first-party functions which return a strategy. There are also many provided by [third-party libraries](#document-extensions). Note that we often say “strategy” when we mean “function returning a strategy”; it’s usually clear from context which one we mean.

Strategies can be passed to other strategies as arguments, combined using [combinator strategies](#combinators), or modified using [`.filter()`](#hypothesis.strategies.SearchStrategy.filter "hypothesis.strategies.SearchStrategy.filter"), [`.map()`](#hypothesis.strategies.SearchStrategy.map "hypothesis.strategies.SearchStrategy.map"), or [`.flatmap()`](#hypothesis.strategies.SearchStrategy.flatmap "hypothesis.strategies.SearchStrategy.flatmap").

##### Primitives[¶](#primitives "Link to this heading")

hypothesis.strategies.none()[¶](#hypothesis.strategies.none "Link to this definition")

Return a strategy which only generates None.

Examples from this strategy do not shrink (because there is only one).

hypothesis.strategies.nothing()[¶](#hypothesis.strategies.nothing "Link to this definition")

This strategy never successfully draws a value and will always reject on an attempt to draw.

Examples from this strategy do not shrink (because there are none).

hypothesis.strategies.just(_value_)[¶](#hypothesis.strategies.just "Link to this definition")

Return a strategy which only generates `value`.

Note: `value` is not copied. Be wary of using mutable values.

If `value` is the result of a callable, you can use [`builds(callable)`](#hypothesis.strategies.builds "hypothesis.strategies.builds") instead of `just(callable())` to get a fresh value each time.

Examples from this strategy do not shrink (because there is only one).

hypothesis.strategies.booleans()[¶](#hypothesis.strategies.booleans "Link to this definition")

Returns a strategy which generates instances of [`bool`](https://docs.python.org/3/library/functions.html#bool "(in Python v3.14)").

Examples from this strategy will shrink towards `False` (i.e. shrinking will replace `True` with `False` where possible).

##### Numeric[¶](#numeric "Link to this heading")

See also

See also the separate sections for [Numpy strategies](#hypothesis-numpy), [Pandas strategies](#hypothesis-pandas), and [Array API strategies](#array-api).

hypothesis.strategies.integers(_min\_value\=None_, _max\_value\=None_)[¶](#hypothesis.strategies.integers "Link to this definition")

Returns a strategy which generates integers.

If min\_value is not None then all values will be >= min\_value. If max\_value is not None then all values will be <= max\_value

Examples from this strategy will shrink towards zero, and negative values will also shrink towards positive (i.e. -n may be replaced by +n).

hypothesis.strategies.floats(

_min\_value\=None_,

_max\_value\=None_,

_\*_,

_allow\_nan\=None_,

_allow\_infinity\=None_,

_allow\_subnormal\=None_,

_width\=64_,

_exclude\_min\=False_,

_exclude\_max\=False_,

)[¶](#hypothesis.strategies.floats "Link to this definition")

Returns a strategy which generates floats.

*   If min\_value is not None, all values will be `>= min_value` (or `> min_value` if `exclude_min`).
    
*   If max\_value is not None, all values will be `<= max_value` (or `< max_value` if `exclude_max`).
    
*   If min\_value or max\_value is not None, it is an error to enable allow\_nan.
    
*   If both min\_value and max\_value are not None, it is an error to enable allow\_infinity.
    
*   If inferred values range does not include subnormal values, it is an error to enable allow\_subnormal.
    

Where not explicitly ruled out by the bounds, [subnormals](https://en.wikipedia.org/wiki/Subnormal_number), infinities, and NaNs are possible values generated by this strategy.

The width argument specifies the maximum number of bits of precision required to represent the generated float. Valid values are 16, 32, or 64. Passing `width=32` will still use the builtin 64-bit [`float`](https://docs.python.org/3/library/functions.html#float "(in Python v3.14)") class, but always for values which can be exactly represented as a 32-bit float.

The exclude\_min and exclude\_max argument can be used to generate numbers from open or half-open intervals, by excluding the respective endpoints. Excluding either signed zero will also exclude the other. Attempting to exclude an endpoint which is None will raise an error; use `allow_infinity=False` to generate finite floats. You can however use e.g. `min_value=-math.inf, exclude_min=True` to exclude only one infinite endpoint.

Examples from this strategy have a complicated and hard to explain shrinking behaviour, but it tries to improve “human readability”. Finite numbers will be preferred to infinity and infinity will be preferred to NaN.

hypothesis.strategies.complex\_numbers(

_\*_,

_min\_magnitude\=0_,

_max\_magnitude\=None_,

_allow\_infinity\=None_,

_allow\_nan\=None_,

_allow\_subnormal\=True_,

_width\=128_,

)[¶](#hypothesis.strategies.complex_numbers "Link to this definition")

Returns a strategy that generates [`complex`](https://docs.python.org/3/library/functions.html#complex "(in Python v3.14)") numbers.

This strategy draws complex numbers with constrained magnitudes. The `min_magnitude` and `max_magnitude` parameters should be non-negative [`Real`](https://docs.python.org/3/library/numbers.html#numbers.Real "(in Python v3.14)") numbers; a value of `None` corresponds an infinite upper bound.

If `min_magnitude` is nonzero or `max_magnitude` is finite, it is an error to enable `allow_nan`. If `max_magnitude` is finite, it is an error to enable `allow_infinity`.

`allow_infinity`, `allow_nan`, and `allow_subnormal` are applied to each part of the complex number separately, as for [`floats()`](#hypothesis.strategies.floats "hypothesis.strategies.floats").

The magnitude constraints are respected up to a relative error of (around) floating-point epsilon, due to implementation via the system `sqrt` function.

The `width` argument specifies the maximum number of bits of precision required to represent the entire generated complex number. Valid values are 32, 64 or 128, which correspond to the real and imaginary components each having width 16, 32 or 64, respectively. Passing `width=64` will still use the builtin 128-bit [`complex`](https://docs.python.org/3/library/functions.html#complex "(in Python v3.14)") class, but always for values which can be exactly represented as two 32-bit floats.

Examples from this strategy shrink by shrinking their real and imaginary parts, as [`floats()`](#hypothesis.strategies.floats "hypothesis.strategies.floats").

If you need to generate complex numbers with particular real and imaginary parts or relationships between parts, consider using [`builds(complex, ...)`](#hypothesis.strategies.builds "hypothesis.strategies.builds") or [`@composite`](#hypothesis.strategies.composite "hypothesis.strategies.composite") respectively.

hypothesis.strategies.decimals(

_min\_value\=None_,

_max\_value\=None_,

_\*_,

_allow\_nan\=None_,

_allow\_infinity\=None_,

_places\=None_,

)[¶](#hypothesis.strategies.decimals "Link to this definition")

Generates instances of [`decimal.Decimal`](https://docs.python.org/3/library/decimal.html#decimal.Decimal "(in Python v3.14)"), which may be:

*   A finite rational number, between `min_value` and `max_value`.
    
*   Not a Number, if `allow_nan` is True. None means “allow NaN, unless `min_value` and `max_value` are not None”.
    
*   Positive or negative infinity, if `max_value` and `min_value` respectively are None, and `allow_infinity` is not False. None means “allow infinity, unless excluded by the min and max values”.
    

Note that where floats have one `NaN` value, Decimals have four: signed, and either _quiet_ or _signalling_. See [the decimal module docs](https://docs.python.org/3/library/decimal.html#special-values) for more information on special values.

If `places` is not None, all finite values drawn from the strategy will have that number of digits after the decimal place.

Examples from this strategy do not have a well defined shrink order but try to maximize human readability when shrinking.

hypothesis.strategies.fractions(

_min\_value\=None_,

_max\_value\=None_,

_\*_,

_max\_denominator\=None_,

)[¶](#hypothesis.strategies.fractions "Link to this definition")

Returns a strategy which generates Fractions.

If `min_value` is not None then all generated values are no less than `min_value`. If `max_value` is not None then all generated values are no greater than `max_value`. `min_value` and `max_value` may be anything accepted by the [`Fraction`](https://docs.python.org/3/library/fractions.html#fractions.Fraction "(in Python v3.14)") constructor.

If `max_denominator` is not None then the denominator of any generated values is no greater than `max_denominator`. Note that `max_denominator` must be None or a positive integer.

Examples from this strategy shrink towards smaller denominators, then closer to zero.

##### Strings[¶](#strings "Link to this heading")

See also

The [`uuids()`](#hypothesis.strategies.uuids "hypothesis.strategies.uuids") and [`ip_addresses()`](#hypothesis.strategies.ip_addresses "hypothesis.strategies.ip_addresses") strategies generate instances of [`UUID`](https://docs.python.org/3/library/uuid.html#module-uuid "(in Python v3.14)") and [`IPAddress`](https://docs.python.org/3/library/ipaddress.html#module-ipaddress "(in Python v3.14)") respectively. You can generate corresponding string values by using [`.map()`](#hypothesis.strategies.SearchStrategy.map "hypothesis.strategies.SearchStrategy.map"), such as `st.uuids().map(str)`.

hypothesis.strategies.text(

_alphabet\=characters(codec='utf-8')_,

_\*_,

_min\_size\=0_,

_max\_size\=None_,

)[¶](#hypothesis.strategies.text "Link to this definition")

Generates strings with characters drawn from `alphabet`, which should be a collection of length one strings or a strategy generating such strings.

The default alphabet strategy can generate the full unicode range but excludes surrogate characters because they are invalid in the UTF-8 encoding. You can use [`characters()`](#hypothesis.strategies.characters "hypothesis.strategies.characters") without arguments to find surrogate-related bugs such as [bpo-34454](https://bugs.python.org/issue34454).

`min_size` and `max_size` have the usual interpretations. Note that Python measures string length by counting codepoints: U+00C5 `Å` is a single character, while U+0041 U+030A `Å` is two - the `A`, and a combining ring above.

Examples from this strategy shrink towards shorter strings, and with the characters in the text shrinking as per the alphabet strategy. This strategy does not [`normalize()`](https://docs.python.org/3/library/unicodedata.html#unicodedata.normalize "(in Python v3.14)") examples, so generated strings may be in any or none of the ‘normal forms’.

hypothesis.strategies.characters(

_\*_,

_codec\=None_,

_min\_codepoint\=None_,

_max\_codepoint\=None_,

_categories\=None_,

_exclude\_categories\=None_,

_exclude\_characters\=None_,

_include\_characters\=None_,

)[¶](#hypothesis.strategies.characters "Link to this definition")

Generates characters, length-one [`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.14)")ings, following specified filtering rules.

*   When no filtering rules are specified, any character can be produced.
    
*   If `min_codepoint` or `max_codepoint` is specified, then only characters having a codepoint in that range will be produced.
    
*   If `categories` is specified, then only characters from those Unicode categories will be produced. This is a further restriction, characters must also satisfy `min_codepoint` and `max_codepoint`.
    
*   If `exclude_categories` is specified, then any character from those categories will not be produced. You must not pass both `categories` and `exclude_categories`; these arguments are alternative ways to specify exactly the same thing.
    
*   If `include_characters` is specified, then any additional characters in that list will also be produced.
    
*   If `exclude_characters` is specified, then any characters in that list will be not be produced. Any overlap between `include_characters` and `exclude_characters` will raise an exception.
    
*   If `codec` is specified, only characters in the specified [codec encodings](https://docs.python.org/3/library/codecs.html#encodings-and-unicode) will be produced.
    

The `_codepoint` arguments must be integers between zero and [`sys.maxunicode`](https://docs.python.org/3/library/sys.html#sys.maxunicode "(in Python v3.14)"). The `_characters` arguments must be collections of length-one unicode strings, such as a unicode string.

The `_categories` arguments must be used to specify either the one-letter Unicode major category or the two-letter Unicode [general category](https://en.wikipedia.org/wiki/Unicode_character_property). For example, `('Nd', 'Lu')` signifies “Number, decimal digit” and “Letter, uppercase”. A single letter (‘major category’) can be given to match all corresponding categories, for example `'P'` for characters in any punctuation category.

We allow codecs from the [`codecs`](https://docs.python.org/3/library/codecs.html#module-codecs "(in Python v3.14)") module and their aliases, platform specific and user-registered codecs if they are available, and [python-specific text encodings](https://docs.python.org/3/library/codecs.html#python-specific-encodings) (but not text or binary transforms). `include_characters` which cannot be encoded using this codec will raise an exception. If non-encodable codepoints or categories are explicitly allowed, the `codec` argument will exclude them without raising an exception.

Examples from this strategy shrink towards the codepoint for `'0'`, or the first allowable codepoint after it if `'0'` is excluded.

hypothesis.strategies.from\_regex(_regex_, _\*_, _fullmatch\=False_, _alphabet\=None_)[¶](#hypothesis.strategies.from_regex "Link to this definition")

Generates strings that contain a match for the given regex (i.e. ones for which [`re.search()`](https://docs.python.org/3/library/re.html#re.search "(in Python v3.14)") will return a non-None result).

`regex` may be a pattern or [`compiled regex`](https://docs.python.org/3/library/re.html#re.compile "(in Python v3.14)"). Both byte-strings and unicode strings are supported, and will generate examples of the same type.

You can use regex flags such as [`re.IGNORECASE`](https://docs.python.org/3/library/re.html#re.IGNORECASE "(in Python v3.14)") or [`re.DOTALL`](https://docs.python.org/3/library/re.html#re.DOTALL "(in Python v3.14)") to control generation. Flags can be passed either in compiled regex or inside the pattern with a `(?iLmsux)` group.

Some regular expressions are only partly supported - the underlying strategy checks local matching and relies on filtering to resolve context-dependent expressions. Using too many of these constructs may cause health-check errors as too many examples are filtered out. This mainly includes (positive or negative) lookahead and lookbehind groups.

If you want the generated string to match the whole regex you should use boundary markers. So e.g. `r"\A.\Z"` will return a single character string, while `"."` will return any string, and `r"\A.$"` will return a single character optionally followed by a `"\n"`. Alternatively, passing `fullmatch=True` will ensure that the whole string is a match, as if you had used the `\A` and `\Z` markers.

The `alphabet=` argument constrains the characters in the generated string, as for [`text()`](#hypothesis.strategies.text "hypothesis.strategies.text"), and is only supported for unicode strings.

Examples from this strategy shrink towards shorter strings and lower character values, with exact behaviour that may depend on the pattern.

hypothesis.strategies.binary(_\*_, _min\_size\=0_, _max\_size\=None_)[¶](#hypothesis.strategies.binary "Link to this definition")

Generates [`bytes`](https://docs.python.org/3/library/stdtypes.html#bytes "(in Python v3.14)").

The generated [`bytes`](https://docs.python.org/3/library/stdtypes.html#bytes "(in Python v3.14)") will have a length of at least `min_size` and at most `max_size`. If `max_size` is None there is no upper limit.

Examples from this strategy shrink towards smaller strings and lower byte values.

hypothesis.strategies.emails(_\*_, _domains\=domains()_)[¶](#hypothesis.strategies.emails "Link to this definition")

A strategy for generating email addresses as unicode strings. The address format is specified in [**RFC 5322 Section 3.4.1**](https://datatracker.ietf.org/doc/html/rfc5322.html#section-3.4.1). Values shrink towards shorter local-parts and host domains.

If `domains` is given then it must be a strategy that generates domain names for the emails, defaulting to [`domains()`](#hypothesis.provisional.domains "hypothesis.provisional.domains").

This strategy is useful for generating “user data” for tests, as mishandling of email addresses is a common source of bugs.

hypothesis.provisional.domains(_\*_, _max\_length\=255_, _max\_element\_length\=63_)[¶](#hypothesis.provisional.domains "Link to this definition")

Generate [**RFC 1035**](https://datatracker.ietf.org/doc/html/rfc1035.html) compliant fully qualified domain names.

Warning

The [`domains()`](#hypothesis.provisional.domains "hypothesis.provisional.domains") strategy is provisional. Its interface may be changed in a minor release, without being subject to our [deprecation policy](#deprecation-policy). That said, we expect it to be relatively stable.

hypothesis.provisional.urls()[¶](#hypothesis.provisional.urls "Link to this definition")

A strategy for [**RFC 3986**](https://datatracker.ietf.org/doc/html/rfc3986.html), generating http/https URLs.

The generated URLs could, at least in theory, be passed to an HTTP client and fetched.

Warning

The [`urls()`](#hypothesis.provisional.urls "hypothesis.provisional.urls") strategy is provisional. Its interface may be changed in a minor release, without being subject to our [deprecation policy](#deprecation-policy). That said, we expect it to be relatively stable.

##### Collections[¶](#collections "Link to this heading")

hypothesis.strategies.lists(

_elements_,

_\*_,

_min\_size\=0_,

_max\_size\=None_,

_unique\_by\=None_,

_unique\=False_,

)[¶](#hypothesis.strategies.lists "Link to this definition")

Returns a list containing values drawn from elements with length in the interval \[min\_size, max\_size\] (no bounds in that direction if these are None). If max\_size is 0, only the empty list will be drawn.

If `unique` is True (or something that evaluates to True), we compare direct object equality, as if unique\_by was `lambda x: x`. This comparison only works for hashable types.

If `unique_by` is not None it must be a callable or tuple of callables returning a hashable type when given a value drawn from elements. The resulting list will satisfy the condition that for `i` != `j`, `unique_by(result[i])` != `unique_by(result[j])`.

If `unique_by` is a tuple of callables the uniqueness will be respective to each callable.

For example, the following will produce two columns of integers with both columns being unique respectively.

\>>> twoints \= st.tuples(st.integers(), st.integers())
\>>> st.lists(twoints, unique\_by\=(lambda x: x\[0\], lambda x: x\[1\]))

Examples from this strategy shrink by trying to remove elements from the list, and by shrinking each individual element of the list.

hypothesis.strategies.tuples(_\*args_)[¶](#hypothesis.strategies.tuples "Link to this definition")

Return a strategy which generates a tuple of the same length as args by generating the value at index i from args\[i\].

e.g. tuples(integers(), integers()) would generate a tuple of length two with both values an integer.

Examples from this strategy shrink by shrinking their component parts.

hypothesis.strategies.sets(_elements_, _\*_, _min\_size\=0_, _max\_size\=None_)[¶](#hypothesis.strategies.sets "Link to this definition")

This has the same behaviour as lists, but returns sets instead.

Note that Hypothesis cannot tell if values are drawn from elements are hashable until running the test, so you can define a strategy for sets of an unhashable type but it will fail at test time.

Examples from this strategy shrink by trying to remove elements from the set, and by shrinking each individual element of the set.

hypothesis.strategies.frozensets(_elements_, _\*_, _min\_size\=0_, _max\_size\=None_)[¶](#hypothesis.strategies.frozensets "Link to this definition")

This is identical to the sets function but instead returns frozensets.

hypothesis.strategies.dictionaries(

_keys_,

_values_,

_\*_,

_dict\_class=<class 'dict'>_,

_min\_size=0_,

_max\_size=None_,

)[¶](#hypothesis.strategies.dictionaries "Link to this definition")

Generates dictionaries of type `dict_class` with keys drawn from the `keys` argument and values drawn from the `values` argument.

The size parameters have the same interpretation as for [`lists()`](#hypothesis.strategies.lists "hypothesis.strategies.lists").

Examples from this strategy shrink by trying to remove keys from the generated dictionary, and by shrinking each generated key and value.

hypothesis.strategies.fixed\_dictionaries(_mapping_, _\*_, _optional\=None_)[¶](#hypothesis.strategies.fixed_dictionaries "Link to this definition")

Generates a dictionary of the same type as mapping with a fixed set of keys mapping to strategies. `mapping` must be a dict subclass.

Generated values have all keys present in mapping, in iteration order, with the corresponding values drawn from mapping\[key\].

If `optional` is passed, the generated value _may or may not_ contain each key from `optional` and a value drawn from the corresponding strategy. Generated values may contain optional keys in an arbitrary order.

Examples from this strategy shrink by shrinking each individual value in the generated dictionary, and omitting optional key-value pairs.

hypothesis.strategies.iterables(

_elements_,

_\*_,

_min\_size\=0_,

_max\_size\=None_,

_unique\_by\=None_,

_unique\=False_,

)[¶](#hypothesis.strategies.iterables "Link to this definition")

This has the same behaviour as lists, but returns iterables instead.

Some iterables cannot be indexed (e.g. sets) and some do not have a fixed length (e.g. generators). This strategy produces iterators, which cannot be indexed and do not have a fixed length. This ensures that you do not accidentally depend on sequence behaviour.

##### Datetime[¶](#datetime "Link to this heading")

hypothesis.strategies.dates(

_min\_value\=datetime.date.min_,

_max\_value\=datetime.date.max_,

)[¶](#hypothesis.strategies.dates "Link to this definition")

A strategy for dates between `min_value` and `max_value`.

Examples from this strategy shrink towards January 1st 2000.

hypothesis.strategies.times(

_min\_value\=datetime.time.min_,

_max\_value\=datetime.time.max_,

_\*_,

_timezones\=none()_,

)[¶](#hypothesis.strategies.times "Link to this definition")

A strategy for times between `min_value` and `max_value`.

The `timezones` argument is handled as for [`datetimes()`](#hypothesis.strategies.datetimes "hypothesis.strategies.datetimes").

Examples from this strategy shrink towards midnight, with the timezone component shrinking as for the strategy that provided it.

hypothesis.strategies.datetimes(

_min\_value\=datetime.datetime.min_,

_max\_value\=datetime.datetime.max_,

_\*_,

_timezones\=none()_,

_allow\_imaginary\=True_,

)[¶](#hypothesis.strategies.datetimes "Link to this definition")

A strategy for generating datetimes, which may be timezone-aware.

This strategy works by drawing a naive datetime between `min_value` and `max_value`, which must both be naive (have no timezone).

`timezones` must be a strategy that generates either `None`, for naive datetimes, or [`tzinfo`](https://docs.python.org/3/library/datetime.html#datetime.tzinfo "(in Python v3.14)") objects for ‘aware’ datetimes. You can construct your own, though we recommend using one of these built-in strategies:

*   with the standard library: [`hypothesis.strategies.timezones()`](#hypothesis.strategies.timezones "hypothesis.strategies.timezones");
    
*   with [dateutil](https://pypi.org/project/python-dateutil/): [`hypothesis.extra.dateutil.timezones()`](#hypothesis.extra.dateutil.timezones "hypothesis.extra.dateutil.timezones"); or
    
*   with [pytz](https://pypi.org/project/pytz/): [`hypothesis.extra.pytz.timezones()`](#hypothesis.extra.pytz.timezones "hypothesis.extra.pytz.timezones").
    

You may pass `allow_imaginary=False` to filter out “imaginary” datetimes which did not (or will not) occur due to daylight savings, leap seconds, timezone and calendar adjustments, etc. Imaginary datetimes are allowed by default, because malformed timestamps are a common source of bugs.

Examples from this strategy shrink towards midnight on January 1st 2000, local time.

hypothesis.strategies.timezones(_\*_, _no\_cache\=False_)[¶](#hypothesis.strategies.timezones "Link to this definition")

A strategy for [`zoneinfo.ZoneInfo`](https://docs.python.org/3/library/zoneinfo.html#zoneinfo.ZoneInfo "(in Python v3.14)") objects.

If `no_cache=True`, the generated instances are constructed using [`ZoneInfo.no_cache`](https://docs.python.org/3/library/zoneinfo.html#zoneinfo.ZoneInfo.no_cache "(in Python v3.14)") instead of the usual constructor. This may change the semantics of your datetimes in surprising ways, so only use it if you know that you need to!

Note

[The tzdata package is required on Windows](https://docs.python.org/3/library/zoneinfo.html#data-sources). `pip install hypothesis[zoneinfo]` installs it, if and only if needed.

hypothesis.strategies.timezone\_keys(_\*_, _allow\_prefix\=True_)[¶](#hypothesis.strategies.timezone_keys "Link to this definition")

A strategy for [IANA timezone names](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones).

As well as timezone names like `"UTC"`, `"Australia/Sydney"`, or `"America/New_York"`, this strategy can generate:

*   Aliases such as `"Antarctica/McMurdo"`, which links to `"Pacific/Auckland"`.
    
*   Deprecated names such as `"Antarctica/South_Pole"`, which _also_ links to `"Pacific/Auckland"`. Note that most but not all deprecated timezone names are also aliases.
    
*   Timezone names with the `"posix/"` or `"right/"` prefixes, unless `allow_prefix=False`.
    

These strings are provided separately from Tzinfo objects - such as ZoneInfo instances from the timezones() strategy - to facilitate testing of timezone logic without needing workarounds to access non-canonical names.

Note

[The tzdata package is required on Windows](https://docs.python.org/3/library/zoneinfo.html#data-sources). `pip install hypothesis[zoneinfo]` installs it, if and only if needed.

On Windows, you may need to access IANA timezone data via the [tzdata](https://pypi.org/project/tzdata/) package. For non-IANA timezones, such as Windows-native names or GNU TZ strings, we recommend using [`sampled_from()`](#hypothesis.strategies.sampled_from "hypothesis.strategies.sampled_from") with the [dateutil](https://pypi.org/project/python-dateutil/) package, e.g. [`dateutil.tz.tzwin.list()`](https://dateutil.readthedocs.io/en/stable/tz.html#dateutil.tz.tzwin.list "(in dateutil v3.9.0)").

hypothesis.strategies.timedeltas(

_min\_value\=datetime.timedelta.min_,

_max\_value\=datetime.timedelta.max_,

)[¶](#hypothesis.strategies.timedeltas "Link to this definition")

A strategy for timedeltas between `min_value` and `max_value`.

Examples from this strategy shrink towards zero.

##### Recursive[¶](#recursive "Link to this heading")

hypothesis.strategies.recursive(_base_, _extend_, _\*_, _max\_leaves\=100_)[¶](#hypothesis.strategies.recursive "Link to this definition")

base: A strategy to start from.

extend: A function which takes a strategy and returns a new strategy.

max\_leaves: The maximum number of elements to be drawn from base on a given run.

This returns a strategy `S` such that `S = extend(base | S)`. That is, values may be drawn from base, or from any strategy reachable by mixing applications of | and extend.

An example may clarify: `recursive(booleans(), lists)` would return a strategy that may return arbitrarily nested and mixed lists of booleans. So e.g. `False`, `[True]`, `[False, []]`, and `[[[[True]]]]` are all valid values to be drawn from that strategy.

Examples from this strategy shrink by trying to reduce the amount of recursion and by shrinking according to the shrinking behaviour of base and the result of extend.

hypothesis.strategies.deferred(_definition_)[¶](#hypothesis.strategies.deferred "Link to this definition")

A deferred strategy allows you to write a strategy that references other strategies that have not yet been defined. This allows for the easy definition of recursive and mutually recursive strategies.

The definition argument should be a zero-argument function that returns a strategy. It will be evaluated the first time the strategy is used to produce an example.

Example usage:

\>>> import hypothesis.strategies as st
\>>> x \= st.deferred(lambda: st.booleans() | st.tuples(x, x))
\>>> x.example()
(((False, (True, True)), (False, True)), (True, True))
\>>> x.example()
True

Mutual recursion also works fine:

\>>> a \= st.deferred(lambda: st.booleans() | b)
\>>> b \= st.deferred(lambda: st.tuples(a, a))
\>>> a.example()
True
\>>> b.example()
(False, (False, ((False, True), False)))

Examples from this strategy shrink as they normally would from the strategy returned by the definition.

##### Random[¶](#random "Link to this heading")

hypothesis.strategies.randoms(_\*_, _note\_method\_calls\=False_, _use\_true\_random\=False_)[¶](#hypothesis.strategies.randoms "Link to this definition")

Generates instances of `random.Random`. The generated Random instances are of a special HypothesisRandom subclass.

*   If `note_method_calls` is set to `True`, Hypothesis will print the randomly drawn values in any falsifying test case. This can be helpful for debugging the behaviour of randomized algorithms.
    
*   If `use_true_random` is set to `True` then values will be drawn from their usual distribution, otherwise they will actually be Hypothesis generated values (and will be shrunk accordingly for any failing test case). Setting `use_true_random=False` will tend to expose bugs that would occur with very low probability when it is set to True, and this flag should only be set to True when your code relies on the distribution of values for correctness.
    

For managing global state, see the [`random_module()`](#hypothesis.strategies.random_module "hypothesis.strategies.random_module") strategy and [`register_random()`](#hypothesis.register_random "hypothesis.register_random") function.

hypothesis.strategies.random\_module()[¶](#hypothesis.strategies.random_module "Link to this definition")

Hypothesis always seeds global PRNGs before running a test, and restores the previous state afterwards.

If having a fixed seed would unacceptably weaken your tests, and you cannot use a `random.Random` instance provided by [`randoms()`](#hypothesis.strategies.randoms "hypothesis.strategies.randoms"), this strategy calls [`random.seed()`](https://docs.python.org/3/library/random.html#random.seed "(in Python v3.14)") with an arbitrary integer and passes you an opaque object whose repr displays the seed value for debugging. If `numpy.random` is available, that state is also managed, as is anything managed by [`hypothesis.register_random()`](#hypothesis.register_random "hypothesis.register_random").

Examples from these strategy shrink to seeds closer to zero.

hypothesis.register\_random(_r_)[¶](#hypothesis.register_random "Link to this definition")

Register (a weakref to) the given Random-like instance for management by Hypothesis.

You can pass instances of structural subtypes of `random.Random` (i.e., objects with seed, getstate, and setstate methods) to `register_random(r)` to have their states seeded and restored in the same way as the global PRNGs from the `random` and `numpy.random` modules.

All global PRNGs, from e.g. simulation or scheduling frameworks, should be registered to prevent flaky tests. Hypothesis will ensure that the PRNG state is consistent for all test runs, always seeding them to zero and restoring the previous state after the test, or, reproducibly varied if you choose to use the [`random_module()`](#hypothesis.strategies.random_module "hypothesis.strategies.random_module") strategy.

`register_random` only makes [weakrefs](https://docs.python.org/3/library/weakref.html#module-weakref) to `r`, thus `r` will only be managed by Hypothesis as long as it has active references elsewhere at runtime. The pattern `register_random(MyRandom())` will raise a `ReferenceError` to help protect users from this issue. This check does not occur for the PyPy interpreter. See the following example for an illustration of this issue

def my\_BROKEN\_hook():
    r \= MyRandomLike()

    \# \`r\` will be garbage collected after the hook resolved
    \# and Hypothesis will 'forget' that it was registered
    register\_random(r)  \# Hypothesis will emit a warning

rng \= MyRandomLike()

def my\_WORKING\_hook():
    register\_random(rng)

##### Combinators[¶](#combinators "Link to this heading")

hypothesis.strategies.one\_of(_\*args_)[¶](#hypothesis.strategies.one_of "Link to this definition")

Return a strategy which generates values from any of the argument strategies.

This may be called with one iterable argument instead of multiple strategy arguments, in which case `one_of(x)` and `one_of(*x)` are equivalent.

Examples from this strategy will generally shrink to ones that come from strategies earlier in the list, then shrink according to behaviour of the strategy that produced them. In order to get good shrinking behaviour, try to put simpler strategies first. e.g. `one_of(none(), text())` is better than `one_of(text(), none())`.

This is especially important when using recursive strategies. e.g. `x = st.deferred(lambda: st.none() | st.tuples(x, x))` will shrink well, but `x = st.deferred(lambda: st.tuples(x, x) | st.none())` will shrink very badly indeed.

hypothesis.strategies.builds(_target_, _/_, _\*args_, _\*\*kwargs_)[¶](#hypothesis.strategies.builds "Link to this definition")

Generates values by drawing from `args` and `kwargs` and passing them to the callable (provided as the first positional argument) in the appropriate argument position.

e.g. `builds(target, integers(), flag=booleans())` would draw an integer `i` and a boolean `b` and call `target(i, flag=b)`.

If the callable has type annotations, they will be used to infer a strategy for required arguments that were not passed to builds. You can also tell builds to infer a strategy for an optional argument by passing `...` ([`Ellipsis`](https://docs.python.org/3/library/constants.html#Ellipsis "(in Python v3.14)")) as a keyword argument to builds, instead of a strategy for that argument to the callable.

If the callable is a class defined with [attrs](https://pypi.org/project/attrs/), missing required arguments will be inferred from the attribute on a best-effort basis, e.g. by checking [attrs standard validators](https://www.attrs.org/en/stable/api.html#api-validators "(in attrs v25.4)"). Dataclasses are handled natively by the inference from type hints.

Examples from this strategy shrink by shrinking the argument values to the callable.

hypothesis.strategies.composite(_f_)[¶](#hypothesis.strategies.composite "Link to this definition")

Defines a strategy that is built out of potentially arbitrarily many other strategies.

@composite provides a callable `draw` as the first parameter to the decorated function, which can be used to dynamically draw a value from any strategy. For example:

from hypothesis import strategies as st, given

@st.composite
def values(draw):
    n1 \= draw(st.integers())
    n2 \= draw(st.integers(min\_value\=n1))
    return (n1, n2)

@given(values())
def f(value):
    (n1, n2) \= value
    assert n1 <= n2

@composite cannot mix test code and generation code. If you need that, use [`data()`](#hypothesis.strategies.data "hypothesis.strategies.data").

If [`@composite`](#hypothesis.strategies.composite "hypothesis.strategies.composite") is used to decorate a method or classmethod, the `draw` argument must come before `self` or `cls`. While we therefore recommend writing strategies as standalone functions and using [`register_type_strategy()`](#hypothesis.strategies.register_type_strategy "hypothesis.strategies.register_type_strategy") to associate them with a class, methods are supported and the `@composite` decorator may be applied either before or after `@classmethod` or `@staticmethod`. See [issue #2578](https://github.com/HypothesisWorks/hypothesis/issues/2578) and [pull request #2634](https://github.com/HypothesisWorks/hypothesis/pull/2634) for more details.

Examples from this strategy shrink by shrinking the output of each draw call.

hypothesis.strategies.data()[¶](#hypothesis.strategies.data "Link to this definition")

Provides an object `data` with a `data.draw` function which acts like the `draw` callable provided by [`@composite`](#hypothesis.strategies.composite "hypothesis.strategies.composite"), in that it can be used to dynamically draw values from strategies. [`data()`](#hypothesis.strategies.data "hypothesis.strategies.data") is more powerful than [`@composite`](#hypothesis.strategies.composite "hypothesis.strategies.composite"), because it allows you to mix generation and test code.

Here’s an example of dynamically generating values using [`data()`](#hypothesis.strategies.data "hypothesis.strategies.data"):

from hypothesis import strategies as st, given

@given(st.data())
def test\_values(data):
    n1 \= data.draw(st.integers())
    n2 \= data.draw(st.integers(min\_value\=n1))
    assert n1 + 1 <= n2

If the test fails, each draw will be printed with the falsifying example. e.g. the above is wrong (it has a boundary condition error), so will print:

Falsifying example: test\_values(data=data(...))
Draw 1: 0
Draw 2: 0

Optionally, you can provide a label to identify values generated by each call to `data.draw()`. These labels can be used to identify values in the output of a falsifying example.

For instance:

@given(st.data())
def test\_draw\_sequentially(data):
    x \= data.draw(st.integers(), label\="First number")
    y \= data.draw(st.integers(min\_value\=x), label\="Second number")
    assert x < y

will produce:

Falsifying example: test\_draw\_sequentially(data=data(...))
Draw 1 (First number): 0
Draw 2 (Second number): 0

Examples from this strategy shrink by shrinking the output of each draw call.

##### Typing[¶](#typing "Link to this heading")

hypothesis.strategies.from\_type(_thing_)[¶](#hypothesis.strategies.from_type "Link to this definition")

Looks up the appropriate search strategy for the given type.

[`from_type()`](#hypothesis.strategies.from_type "hypothesis.strategies.from_type") is used internally to fill in missing arguments to [`builds()`](#hypothesis.strategies.builds "hypothesis.strategies.builds") and can be used interactively to explore what strategies are available or to debug type resolution.

You can use [`register_type_strategy()`](#hypothesis.strategies.register_type_strategy "hypothesis.strategies.register_type_strategy") to handle your custom types, or to globally redefine certain strategies - for example excluding NaN from floats, or use timezone-aware instead of naive time and datetime strategies.

[`from_type()`](#hypothesis.strategies.from_type "hypothesis.strategies.from_type") looks up a strategy in the following order:

1.  If `thing` is in the default lookup mapping or user-registered lookup, return the corresponding strategy. The default lookup covers all types with Hypothesis strategies, including extras where possible.
    
2.  If `thing` is from the [`typing`](https://docs.python.org/3/library/typing.html#module-typing "(in Python v3.14)") module, return the corresponding strategy (special logic).
    
3.  If `thing` has one or more subtypes in the merged lookup, return the union of the strategies for those types that are not subtypes of other elements in the lookup.
    
4.  Finally, if `thing` has type annotations for all required arguments, and is not an abstract class, it is resolved via [`builds()`](#hypothesis.strategies.builds "hypothesis.strategies.builds").
    
5.  Because [`abstract types`](https://docs.python.org/3/library/abc.html#module-abc "(in Python v3.14)") cannot be instantiated, we treat abstract types as the union of their concrete subclasses. Note that this lookup works via inheritance but not via [`register`](https://docs.python.org/3/library/abc.html#abc.ABCMeta.register "(in Python v3.14)"), so you may still need to use [`register_type_strategy()`](#hypothesis.strategies.register_type_strategy "hypothesis.strategies.register_type_strategy").
    

There is a valuable recipe for leveraging [`from_type()`](#hypothesis.strategies.from_type "hypothesis.strategies.from_type") to generate “everything except” values from a specified type. I.e.

def everything\_except(excluded\_types):
    return (
        from\_type(type)
        .flatmap(from\_type)
        .filter(lambda x: not isinstance(x, excluded\_types))
    )

For example, `everything_except(int)` returns a strategy that can generate anything that [`from_type()`](#hypothesis.strategies.from_type "hypothesis.strategies.from_type") can ever generate, except for instances of [`int`](https://docs.python.org/3/library/functions.html#int "(in Python v3.14)"), and excluding instances of types added via [`register_type_strategy()`](#hypothesis.strategies.register_type_strategy "hypothesis.strategies.register_type_strategy").

This is useful when writing tests which check that invalid input is rejected in a certain way.

hypothesis.strategies.register\_type\_strategy(_custom\_type_, _strategy_)[¶](#hypothesis.strategies.register_type_strategy "Link to this definition")

Add an entry to the global type-to-strategy lookup.

This lookup is used in [`builds()`](#hypothesis.strategies.builds "hypothesis.strategies.builds") and [`@given`](#hypothesis.given "hypothesis.given").

[`builds()`](#hypothesis.strategies.builds "hypothesis.strategies.builds") will be used automatically for classes with type annotations on `__init__` , so you only need to register a strategy if one or more arguments need to be more tightly defined than their type-based default, or if you want to supply a strategy for an argument with a default value.

`strategy` may be a search strategy, or a function that takes a type and returns a strategy (useful for generic types). The function may return [`NotImplemented`](https://docs.python.org/3/library/constants.html#NotImplemented "(in Python v3.14)") to conditionally not provide a strategy for the type (the type will still be resolved by other methods, if possible, as if the function was not registered).

Note that you may not register a parametrised generic type (such as `MyCollection[int]`) directly, because the resolution logic does not handle this case correctly. Instead, you may register a _function_ for `MyCollection` and [inspect the type parameters within that function](https://stackoverflow.com/q/48572831).

##### Hypothesis[¶](#hypothesis "Link to this heading")

hypothesis.strategies.runner(_\*_, _default\=not\_set_)[¶](#hypothesis.strategies.runner "Link to this definition")

A strategy for getting “the current test runner”, whatever that may be. The exact meaning depends on the entry point, but it will usually be the associated ‘self’ value for it.

If you are using this in a rule for stateful testing, this strategy will return the instance of the [`RuleBasedStateMachine`](#hypothesis.stateful.RuleBasedStateMachine "hypothesis.stateful.RuleBasedStateMachine") that the rule is running for.

If there is no current test runner and a default is provided, return that default. If no default is provided, raises InvalidArgument.

Examples from this strategy do not shrink (because there is only one).

hypothesis.strategies.shared(_base_, _\*_, _key\=None_)[¶](#hypothesis.strategies.shared "Link to this definition")

Returns a strategy that draws a single shared value per run, drawn from base. Any two shared instances with the same key will share the same value, otherwise the identity of this strategy will be used. That is:

\>>> s \= integers()  \# or any other strategy
\>>> x \= shared(s)
\>>> y \= shared(s)

In the above x and y may draw different (or potentially the same) values. In the following they will always draw the same:

\>>> x \= shared(s, key\="hi")
\>>> y \= shared(s, key\="hi")

Examples from this strategy shrink as per their base strategy.

##### Misc[¶](#misc "Link to this heading")

hypothesis.strategies.functions(_\*_, _like\=lambda : ..._, _returns\=..._, _pure\=False_)[¶](#hypothesis.strategies.functions "Link to this definition")

A strategy for functions, which can be used in callbacks.

The generated functions will mimic the interface of `like`, which must be a callable (including a class, method, or function). The return value for the function is drawn from the `returns` argument, which must be a strategy. If `returns` is not passed, we attempt to infer a strategy from the return-type annotation if present, falling back to [`none()`](#hypothesis.strategies.none "hypothesis.strategies.none").

If `pure=True`, all arguments passed to the generated function must be hashable, and if passed identical arguments the original return value will be returned again - _not_ regenerated, so beware mutable values.

If `pure=False`, generated functions do not validate their arguments, and may return a different value if called again with the same arguments.

Generated functions can only be called within the scope of the `@given` which created them.

hypothesis.strategies.slices(_size_)[¶](#hypothesis.strategies.slices "Link to this definition")

Generates slices that will select indices up to the supplied size

Generated slices will have start and stop indices that range from -size to size - 1 and will step in the appropriate direction. Slices should only produce an empty selection if the start and end are the same.

Examples from this strategy shrink toward 0 and smaller values

hypothesis.strategies.uuids(_\*_, _version\=None_, _allow\_nil\=False_)[¶](#hypothesis.strategies.uuids "Link to this definition")

Returns a strategy that generates [`UUIDs`](https://docs.python.org/3/library/uuid.html#uuid.UUID "(in Python v3.14)").

If the optional version argument is given, value is passed through to [`UUID`](https://docs.python.org/3/library/uuid.html#uuid.UUID "(in Python v3.14)") and only UUIDs of that version will be generated.

If `allow_nil` is True, generate the nil UUID much more often. Otherwise, all returned values from this will be unique, so e.g. if you do `lists(uuids())` the resulting list will never contain duplicates.

Examples from this strategy don’t have any meaningful shrink order.

hypothesis.strategies.ip\_addresses(_\*_, _v\=None_, _network\=None_)[¶](#hypothesis.strategies.ip_addresses "Link to this definition")

Generate IP addresses - `v=4` for [`IPv4Address`](https://docs.python.org/3/library/ipaddress.html#ipaddress.IPv4Address "(in Python v3.14)")es, `v=6` for [`IPv6Address`](https://docs.python.org/3/library/ipaddress.html#ipaddress.IPv6Address "(in Python v3.14)")es, or leave unspecified to allow both versions.

`network` may be an [`IPv4Network`](https://docs.python.org/3/library/ipaddress.html#ipaddress.IPv4Network "(in Python v3.14)") or [`IPv6Network`](https://docs.python.org/3/library/ipaddress.html#ipaddress.IPv6Network "(in Python v3.14)"), or a string representing a network such as `"127.0.0.0/24"` or `"2001:db8::/32"`. As well as generating addresses within a particular routable network, this can be used to generate addresses from a reserved range listed in the [IANA](https://www.iana.org/assignments/iana-ipv4-special-registry/) [registries](https://www.iana.org/assignments/iana-ipv6-special-registry/).

If you pass both `v` and `network`, they must be for the same version.

hypothesis.strategies.sampled\_from(_elements_)[¶](#hypothesis.strategies.sampled_from "Link to this definition")

Returns a strategy which generates any value present in `elements`.

Note that as with [`just()`](#hypothesis.strategies.just "hypothesis.strategies.just"), values will not be copied and thus you should be careful of using mutable data.

`sampled_from` supports ordered collections, as well as [`Enum`](https://docs.python.org/3/library/enum.html#enum.Enum "(in Python v3.14)") objects. [`Flag`](https://docs.python.org/3/library/enum.html#enum.Flag "(in Python v3.14)") objects may also generate any combination of their members.

Examples from this strategy shrink by replacing them with values earlier in the list. So e.g. `sampled_from([10, 1])` will shrink by trying to replace 1 values with 10, and `sampled_from([1, 10])` will shrink by trying to replace 10 values with 1.

It is an error to sample from an empty sequence, because returning [`nothing()`](#hypothesis.strategies.nothing "hypothesis.strategies.nothing") makes it too easy to silently drop parts of compound strategies. If you need that behaviour, use `sampled_from(seq) if seq else nothing()`.

hypothesis.strategies.permutations(_values_)[¶](#hypothesis.strategies.permutations "Link to this definition")

Return a strategy which returns permutations of the ordered collection `values`.

Examples from this strategy shrink by trying to become closer to the original order of values.

##### Related[¶](#related "Link to this heading")

_class_ hypothesis.strategies.DrawFn[¶](#hypothesis.strategies.DrawFn "Link to this definition")

This type only exists so that you can write type hints for functions decorated with [`@composite`](#hypothesis.strategies.composite "hypothesis.strategies.composite").

def draw(strategy: SearchStrategy\[Ex\], label: object \= None) \-> Ex: ...

@composite
def list\_and\_index(draw: DrawFn) \-> tuple\[int, str\]:
    i \= draw(integers())  \# type of \`i\` inferred as 'int'
    s \= draw(text())  \# type of \`s\` inferred as 'str'
    return i, s

_class_ hypothesis.strategies.DataObject[¶](#hypothesis.strategies.DataObject "Link to this definition")

This type only exists so that you can write type hints for tests using the [`data()`](#hypothesis.strategies.data "hypothesis.strategies.data") strategy. Do not use it directly!

draw(_strategy_, _label\=None_)[¶](#hypothesis.strategies.DataObject.draw "Link to this definition")

Like [`DrawFn`](#hypothesis.strategies.DrawFn "hypothesis.strategies.DrawFn").

_class_ hypothesis.strategies.SearchStrategy[¶](#hypothesis.strategies.SearchStrategy "Link to this definition")

A `SearchStrategy` tells Hypothesis how to generate that kind of input.

This class is only part of the public API for use in type annotations, so that you can write e.g. `-> SearchStrategy[Foo]` for your function which returns `builds(Foo, ...)`. Do not inherit from or directly instantiate this class.

example()[¶](#hypothesis.strategies.SearchStrategy.example "Link to this definition")

Provide an example of the sort of value that this strategy generates.

This method is designed for use in a REPL, and will raise an error if called from inside [`@given`](#hypothesis.given "hypothesis.given") or a strategy definition. For serious use, see [`@composite`](#hypothesis.strategies.composite "hypothesis.strategies.composite") or [`data()`](#hypothesis.strategies.data "hypothesis.strategies.data").

filter(_condition_)[¶](#hypothesis.strategies.SearchStrategy.filter "Link to this definition")

Returns a new strategy that generates values from this strategy which satisfy the provided condition.

Note that if the condition is too hard to satisfy this might result in your tests failing with an Unsatisfiable exception. A basic version of the filtering logic would look something like:

@st.composite
def filter\_like(draw, strategy, condition):
    for \_ in range(3):
        value \= draw(strategy)
        if condition(value):
            return value
    assume(False)

map(_pack_)[¶](#hypothesis.strategies.SearchStrategy.map "Link to this definition")

Returns a new strategy which generates a value from this one, and then returns `pack(value)`. For example, `integers().map(str)` could generate `str(5)` == `"5"`.

flatmap(_expand_)[¶](#hypothesis.strategies.SearchStrategy.flatmap "Link to this definition")

Old syntax for a special case of [`@composite`](#hypothesis.strategies.composite "hypothesis.strategies.composite"):

@st.composite
def flatmap\_like(draw, base\_strategy, expand):
    value \= draw(base\_strategy)
    new\_strategy \= expand(value)
    return draw(new\_strategy)

We find that the greater readability of [`@composite`](#hypothesis.strategies.composite "hypothesis.strategies.composite") usually outweighs the verbosity, with a few exceptions for simple cases or recipes like `from_type(type).flatmap(from_type)` (“pick a type, get a strategy for any instance of that type, and then generate one of those”).

##### NumPy[¶](#numpy "Link to this heading")

Hypothesis offers a number of strategies for [NumPy](https://numpy.org/) testing, available in the `hypothesis[numpy]` [extra](#document-extras). It lives in the `hypothesis.extra.numpy` package.

The centerpiece is the [`arrays()`](#hypothesis.extra.numpy.arrays "hypothesis.extra.numpy.arrays") strategy, which generates arrays with any dtype, shape, and contents you can specify or give a strategy for. To make this as useful as possible, strategies are provided to generate array shapes and generate all kinds of fixed-size or compound dtypes.

hypothesis.extra.numpy.array\_dtypes(

_subtype\_strategy\=scalar\_dtypes()_,

_\*_,

_min\_size\=1_,

_max\_size\=5_,

_allow\_subarrays\=False_,

)[¶](#hypothesis.extra.numpy.array_dtypes "Link to this definition")

Return a strategy for generating array (compound) dtypes, with members drawn from the given subtype strategy.

hypothesis.extra.numpy.array\_shapes(

_\*_,

_min\_dims\=1_,

_max\_dims\=None_,

_min\_side\=1_,

_max\_side\=None_,

)[¶](#hypothesis.extra.numpy.array_shapes "Link to this definition")

Return a strategy for array shapes (tuples of int >= 1).

*   `min_dims` is the smallest length that the generated shape can possess.
    
*   `max_dims` is the largest length that the generated shape can possess, defaulting to `min_dims + 2`.
    
*   `min_side` is the smallest size that a dimension can possess.
    
*   `max_side` is the largest size that a dimension can possess, defaulting to `min_side + 5`.
    

hypothesis.extra.numpy.arrays(

_dtype_,

_shape_,

_\*_,

_elements\=None_,

_fill\=None_,

_unique\=False_,

)[¶](#hypothesis.extra.numpy.arrays "Link to this definition")

Returns a strategy for generating [`numpy.ndarray`](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.3)")s.

*   `dtype` may be any valid input to [`dtype`](https://numpy.org/doc/stable/reference/generated/numpy.dtype.html#numpy.dtype "(in NumPy v2.3)") (this includes [`dtype`](https://numpy.org/doc/stable/reference/generated/numpy.dtype.html#numpy.dtype "(in NumPy v2.3)") objects), or a strategy that generates such values.
    
*   `shape` may be an integer >= 0, a tuple of such integers, or a strategy that generates such values.
    
*   `elements` is a strategy for generating values to put in the array. If it is None a suitable value will be inferred based on the dtype, which may give any legal value (including eg NaN for floats). If a mapping, it will be passed as `**kwargs` to `from_dtype()`
    
*   `fill` is a strategy that may be used to generate a single background value for the array. If None, a suitable default will be inferred based on the other arguments. If set to [`nothing()`](#hypothesis.strategies.nothing "hypothesis.strategies.nothing") then filling behaviour will be disabled entirely and every element will be generated independently.
    
*   `unique` specifies if the elements of the array should all be distinct from one another. Note that in this case multiple NaN values may still be allowed. If fill is also set, the only valid values for it to return are NaN values (anything for which [`numpy.isnan`](https://numpy.org/doc/stable/reference/generated/numpy.isnan.html#numpy.isnan "(in NumPy v2.3)") returns True. So e.g. for complex numbers `nan+1j` is also a valid fill). Note that if `unique` is set to `True` the generated values must be hashable.
    

Arrays of specified `dtype` and `shape` are generated for example like this:

\>>> import numpy as np
\>>> arrays(np.int8, (2, 3)).example()
array(\[\[-8,  6,  3\],
       \[-6,  4,  6\]\], dtype=int8)
\>>> arrays(np.float, 3, elements\=st.floats(0, 1)).example()
array(\[ 0.88974794,  0.77387938,  0.1977879 \])

Array values are generated in two parts:

1.  Some subset of the coordinates of the array are populated with a value drawn from the elements strategy (or its inferred form).
    
2.  If any coordinates were not assigned in the previous step, a single value is drawn from the `fill` strategy and is assigned to all remaining places.
    

You can set [`fill=nothing()`](#hypothesis.strategies.nothing "hypothesis.strategies.nothing") to disable this behaviour and draw a value for every element.

If `fill=None`, then it will attempt to infer the correct behaviour automatically. If `unique` is `True`, no filling will occur by default. Otherwise, if it looks safe to reuse the values of elements across multiple coordinates (this will be the case for any inferred strategy, and for most of the builtins, but is not the case for mutable values or strategies built with flatmap, map, composite, etc) then it will use the elements strategy as the fill, else it will default to having no fill.

Having a fill helps Hypothesis craft high quality examples, but its main importance is when the array generated is large: Hypothesis is primarily designed around testing small examples. If you have arrays with hundreds or more elements, having a fill value is essential if you want your tests to run in reasonable time.

hypothesis.extra.numpy.basic\_indices(

_shape_,

_\*_,

_min\_dims\=0_,

_max\_dims\=None_,

_allow\_newaxis\=False_,

_allow\_ellipsis\=True_,

)[¶](#hypothesis.extra.numpy.basic_indices "Link to this definition")

Return a strategy for [basic indexes](https://numpy.org/doc/stable/reference/routines.indexing.html "(in NumPy v2.3)") of arrays with the specified shape, which may include dimensions of size zero.

It generates tuples containing some mix of integers, [`slice`](https://docs.python.org/3/library/functions.html#slice "(in Python v3.14)") objects, `...` (an `Ellipsis`), and `None`. When a length-one tuple would be generated, this strategy may instead return the element which will index the first axis, e.g. `5` instead of `(5,)`.

*   `shape` is the shape of the array that will be indexed, as a tuple of positive integers. This must be at least two-dimensional for a tuple to be a valid index; for one-dimensional arrays use [`slices()`](#hypothesis.strategies.slices "hypothesis.strategies.slices") instead.
    
*   `min_dims` is the minimum dimensionality of the resulting array from use of the generated index. When `min_dims == 0`, scalars and zero-dimensional arrays are both allowed.
    
*   `max_dims` is the the maximum dimensionality of the resulting array, defaulting to `len(shape) if not allow_newaxis else max(len(shape), min_dims) + 2`.
    
*   `allow_newaxis` specifies whether `None` is allowed in the index.
    
*   `allow_ellipsis` specifies whether `...` is allowed in the index.
    

hypothesis.extra.numpy.boolean\_dtypes()[¶](#hypothesis.extra.numpy.boolean_dtypes "Link to this definition")

Return a strategy for boolean dtypes.

hypothesis.extra.numpy.broadcastable\_shapes(

_shape_,

_\*_,

_min\_dims\=0_,

_max\_dims\=None_,

_min\_side\=1_,

_max\_side\=None_,

)[¶](#hypothesis.extra.numpy.broadcastable_shapes "Link to this definition")

Return a strategy for shapes that are broadcast-compatible with the provided shape.

Examples from this strategy shrink towards a shape with length `min_dims`. The size of an aligned dimension shrinks towards size `1`. The size of an unaligned dimension shrink towards `min_side`.

*   `shape` is a tuple of integers.
    
*   `min_dims` is the smallest length that the generated shape can possess.
    
*   `max_dims` is the largest length that the generated shape can possess, defaulting to `max(len(shape), min_dims) + 2`.
    
*   `min_side` is the smallest size that an unaligned dimension can possess.
    
*   `max_side` is the largest size that an unaligned dimension can possess, defaulting to 2 plus the size of the largest aligned dimension.
    

The following are some examples drawn from this strategy.

\>>> \[broadcastable\_shapes(shape\=(2, 3)).example() for i in range(5)\]
\[(1, 3), (), (2, 3), (2, 1), (4, 1, 3), (3, )\]

hypothesis.extra.numpy.byte\_string\_dtypes(_\*_, _endianness\='?'_, _min\_len\=1_, _max\_len\=16_)[¶](#hypothesis.extra.numpy.byte_string_dtypes "Link to this definition")

Return a strategy for generating bytestring dtypes, of various lengths and byteorder.

While Hypothesis’ string strategies can generate empty strings, string dtypes with length 0 indicate that size is still to be determined, so the minimum length for string dtypes is 1.

hypothesis.extra.numpy.complex\_number\_dtypes(_\*_, _endianness\='?'_, _sizes\=(64, 128)_)[¶](#hypothesis.extra.numpy.complex_number_dtypes "Link to this definition")

Return a strategy for complex-number dtypes.

sizes is the total size in bits of a complex number, which consists of two floats. Complex halves (a 16-bit real part) are not supported by numpy and will not be generated by this strategy.

hypothesis.extra.numpy.datetime64\_dtypes(

_\*_,

_max\_period\='Y'_,

_min\_period\='ns'_,

_endianness\='?'_,

)[¶](#hypothesis.extra.numpy.datetime64_dtypes "Link to this definition")

Return a strategy for datetime64 dtypes, with various precisions from year to attosecond.

hypothesis.extra.numpy.floating\_dtypes(_\*_, _endianness\='?'_, _sizes\=(16, 32, 64)_)[¶](#hypothesis.extra.numpy.floating_dtypes "Link to this definition")

Return a strategy for floating-point dtypes.

sizes is the size in bits of floating-point number. Some machines support 96- or 128-bit floats, but these are not generated by default.

Larger floats (96 and 128 bit real parts) are not supported on all platforms and therefore disabled by default. To generate these dtypes, include these values in the sizes argument.

hypothesis.extra.numpy.from\_dtype(

_dtype_,

_\*_,

_alphabet\=None_,

_min\_size\=0_,

_max\_size\=None_,

_min\_value\=None_,

_max\_value\=None_,

_allow\_nan\=None_,

_allow\_infinity\=None_,

_allow\_subnormal\=None_,

_exclude\_min\=None_,

_exclude\_max\=None_,

_min\_magnitude\=0_,

_max\_magnitude\=None_,

)[¶](#hypothesis.extra.numpy.from_dtype "Link to this definition")

Creates a strategy which can generate any value of the given dtype.

Compatible parameters are passed to the inferred strategy function while inapplicable ones are ignored. This allows you, for example, to customise the min and max values, control the length or contents of strings, or exclude non-finite numbers. This is particularly useful when kwargs are passed through from [`arrays()`](#hypothesis.extra.numpy.arrays "hypothesis.extra.numpy.arrays") which allow a variety of numeric dtypes, as it seamlessly handles the `width` or representable bounds for you.

hypothesis.extra.numpy.integer\_array\_indices(

_shape_,

_\*_,

_result\_shape\=array\_shapes()_,

_dtype\=dtype('int64')_,

)[¶](#hypothesis.extra.numpy.integer_array_indices "Link to this definition")

Return a search strategy for tuples of integer-arrays that, when used to index into an array of shape `shape`, given an array whose shape was drawn from `result_shape`.

Examples from this strategy shrink towards the tuple of index-arrays:

len(shape) \* (np.zeros(drawn\_result\_shape, dtype), )

*   `shape` a tuple of integers that indicates the shape of the array, whose indices are being generated.
    
*   `result_shape` a strategy for generating tuples of integers, which describe the shape of the resulting index arrays. The default is [`array_shapes()`](#hypothesis.extra.numpy.array_shapes "hypothesis.extra.numpy.array_shapes"). The shape drawn from this strategy determines the shape of the array that will be produced when the corresponding example from `integer_array_indices` is used as an index.
    
*   `dtype` the integer data type of the generated index-arrays. Negative integer indices can be generated if a signed integer type is specified.
    

Recall that an array can be indexed using a tuple of integer-arrays to access its members in an arbitrary order, producing an array with an arbitrary shape. For example:

\>>> from numpy import array
\>>> x \= array(\[\-0, \-1, \-2, \-3, \-4\])
\>>> ind \= (array(\[\[4, 0\], \[0, 1\]\]),)  \# a tuple containing a 2D integer-array
\>>> x\[ind\]  \# the resulting array is commensurate with the indexing array(s)
array(\[\[-4,  0\],
       \[0, -1\]\])

Note that this strategy does not accommodate all variations of so-called ‘advanced indexing’, as prescribed by NumPy’s nomenclature. Combinations of basic and advanced indexes are too complex to usefully define in a standard strategy; we leave application-specific strategies to the user. Advanced-boolean indexing can be defined as `arrays(shape=..., dtype=bool)`, and is similarly left to the user.

hypothesis.extra.numpy.integer\_dtypes(_\*_, _endianness\='?'_, _sizes\=(8, 16, 32, 64)_)[¶](#hypothesis.extra.numpy.integer_dtypes "Link to this definition")

Return a strategy for signed integer dtypes.

endianness and sizes are treated as for [`unsigned_integer_dtypes()`](#hypothesis.extra.numpy.unsigned_integer_dtypes "hypothesis.extra.numpy.unsigned_integer_dtypes").

hypothesis.extra.numpy.mutually\_broadcastable\_shapes(

_\*_,

_num\_shapes\=not\_set_,

_signature\=not\_set_,

_base\_shape\=()_,

_min\_dims\=0_,

_max\_dims\=None_,

_min\_side\=1_,

_max\_side\=None_,

)[¶](#hypothesis.extra.numpy.mutually_broadcastable_shapes "Link to this definition")

Return a strategy for a specified number of shapes N that are mutually-broadcastable with one another and with the provided base shape.

*   `num_shapes` is the number of mutually broadcast-compatible shapes to generate.
    
*   `base_shape` is the shape against which all generated shapes can broadcast. The default shape is empty, which corresponds to a scalar and thus does not constrain broadcasting at all.
    
*   `min_dims` is the smallest length that the generated shape can possess.
    
*   `max_dims` is the largest length that the generated shape can possess, defaulting to `max(len(shape), min_dims) + 2`.
    
*   `min_side` is the smallest size that an unaligned dimension can possess.
    
*   `max_side` is the largest size that an unaligned dimension can possess, defaulting to 2 plus the size of the largest aligned dimension.
    

The strategy will generate a [`typing.NamedTuple`](https://docs.python.org/3/library/typing.html#typing.NamedTuple "(in Python v3.14)") containing:

*   `input_shapes` as a tuple of the N generated shapes.
    
*   `result_shape` as the resulting shape produced by broadcasting the N shapes with the base shape.
    

The following are some examples drawn from this strategy.

\>>> \# Draw three shapes where each shape is broadcast-compatible with (2, 3)
... strat \= mutually\_broadcastable\_shapes(num\_shapes\=3, base\_shape\=(2, 3))
\>>> for \_ in range(5):
...     print(strat.example())
BroadcastableShapes(input\_shapes=((4, 1, 3), (4, 2, 3), ()), result\_shape=(4, 2, 3))
BroadcastableShapes(input\_shapes=((3,), (1, 3), (2, 3)), result\_shape=(2, 3))
BroadcastableShapes(input\_shapes=((), (), ()), result\_shape=())
BroadcastableShapes(input\_shapes=((3,), (), (3,)), result\_shape=(3,))
BroadcastableShapes(input\_shapes=((1, 2, 3), (3,), ()), result\_shape=(1, 2, 3))

**Use with Generalised Universal Function signatures**

A [universal function](https://numpy.org/doc/stable/reference/ufuncs.html "(in NumPy v2.3)") (or ufunc for short) is a function that operates on ndarrays in an element-by-element fashion, supporting array broadcasting, type casting, and several other standard features. A [generalised ufunc](https://numpy.org/doc/stable/reference/c-api/generalized-ufuncs.html "(in NumPy v2.3)") operates on sub-arrays rather than elements, based on the “signature” of the function. Compare e.g. [`numpy.add()`](https://numpy.org/doc/stable/reference/generated/numpy.add.html#numpy.add "(in NumPy v2.3)") (ufunc) to [`numpy.matmul()`](https://numpy.org/doc/stable/reference/generated/numpy.matmul.html#numpy.matmul "(in NumPy v2.3)") (gufunc).

To generate shapes for a gufunc, you can pass the `signature` argument instead of `num_shapes`. This must be a gufunc signature string; which you can write by hand or access as e.g. `np.matmul.signature` on generalised ufuncs.

In this case, the `side` arguments are applied to the ‘core dimensions’ as well, ignoring any frozen dimensions. `base_shape` and the `dims` arguments are applied to the ‘loop dimensions’, and if necessary, the dimensionality of each shape is silently capped to respect the 32-dimension limit.

The generated `result_shape` is the real result shape of applying the gufunc to arrays of the generated `input_shapes`, even where this is different to broadcasting the loop dimensions.

gufunc-compatible shapes shrink their loop dimensions as above, towards omitting optional core dimensions, and smaller-size core dimensions.

\>>> \# np.matmul.signature == "(m?,n),(n,p?)->(m?,p?)"
\>>> for \_ in range(3):
...     mutually\_broadcastable\_shapes(signature\=np.matmul.signature).example()
BroadcastableShapes(input\_shapes=((2,), (2,)), result\_shape=())
BroadcastableShapes(input\_shapes=((3, 4, 2), (1, 2)), result\_shape=(3, 4))
BroadcastableShapes(input\_shapes=((4, 2), (1, 2, 3)), result\_shape=(4, 3))

hypothesis.extra.numpy.nested\_dtypes(

_subtype\_strategy\=scalar\_dtypes()_,

_\*_,

_max\_leaves\=10_,

_max\_itemsize\=None_,

)[¶](#hypothesis.extra.numpy.nested_dtypes "Link to this definition")

Return the most-general dtype strategy.

Elements drawn from this strategy may be simple (from the subtype\_strategy), or several such values drawn from [`array_dtypes()`](#hypothesis.extra.numpy.array_dtypes "hypothesis.extra.numpy.array_dtypes") with `allow_subarrays=True`. Subdtypes in an array dtype may be nested to any depth, subject to the max\_leaves argument.

hypothesis.extra.numpy.scalar\_dtypes()[¶](#hypothesis.extra.numpy.scalar_dtypes "Link to this definition")

Return a strategy that can return any non-flexible scalar dtype.

hypothesis.extra.numpy.timedelta64\_dtypes(

_\*_,

_max\_period\='Y'_,

_min\_period\='ns'_,

_endianness\='?'_,

)[¶](#hypothesis.extra.numpy.timedelta64_dtypes "Link to this definition")

Return a strategy for timedelta64 dtypes, with various precisions from year to attosecond.

hypothesis.extra.numpy.unicode\_string\_dtypes(

_\*_,

_endianness\='?'_,

_min\_len\=1_,

_max\_len\=16_,

)[¶](#hypothesis.extra.numpy.unicode_string_dtypes "Link to this definition")

Return a strategy for generating unicode string dtypes, of various lengths and byteorder.

While Hypothesis’ string strategies can generate empty strings, string dtypes with length 0 indicate that size is still to be determined, so the minimum length for string dtypes is 1.

hypothesis.extra.numpy.unsigned\_integer\_dtypes(

_\*_,

_endianness\='?'_,

_sizes\=(8, 16, 32, 64)_,

)[¶](#hypothesis.extra.numpy.unsigned_integer_dtypes "Link to this definition")

Return a strategy for unsigned integer dtypes.

endianness may be `<` for little-endian, `>` for big-endian, `=` for native byte order, or `?` to allow either byte order. This argument only applies to dtypes of more than one byte.

sizes must be a collection of integer sizes in bits. The default (8, 16, 32, 64) covers the full range of sizes.

hypothesis.extra.numpy.valid\_tuple\_axes(_ndim_, _\*_, _min\_size\=0_, _max\_size\=None_)[¶](#hypothesis.extra.numpy.valid_tuple_axes "Link to this definition")

Return a strategy for generating permissible tuple-values for the `axis` argument for a numpy sequential function (e.g. [`numpy.sum()`](https://numpy.org/doc/stable/reference/generated/numpy.sum.html#numpy.sum "(in NumPy v2.3)")), given an array of the specified dimensionality.

All tuples will have a length >= `min_size` and <= `max_size`. The default value for `max_size` is `ndim`.

Examples from this strategy shrink towards an empty tuple, which render most sequential functions as no-ops.

The following are some examples drawn from this strategy.

\>>> \[valid\_tuple\_axes(3).example() for i in range(4)\]
\[(-3, 1), (0, 1, -1), (0, 2), (0, -2, 2)\]

`valid_tuple_axes` can be joined with other strategies to generate any type of valid axis object, i.e. integers, tuples, and `None`:

any\_axis\_strategy \= none() | integers(\-ndim, ndim \- 1) | valid\_tuple\_axes(ndim)

##### pandas[¶](#pandas "Link to this heading")

Hypothesis provides strategies for several of the core pandas data types: [`pandas.Index`](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.Index.html#pandas.Index "(in pandas v2.3.3)"), [`pandas.Series`](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.Series.html#pandas.Series "(in pandas v2.3.3)") and [`pandas.DataFrame`](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html#pandas.DataFrame "(in pandas v2.3.3)").

The general approach taken by the pandas module is that there are multiple strategies for generating indexes, and all of the other strategies take the number of entries they contain from their index strategy (with sensible defaults). So e.g. a Series is specified by specifying its [`numpy.dtype`](https://numpy.org/doc/stable/reference/generated/numpy.dtype.html#numpy.dtype "(in NumPy v2.3)") (and/or a strategy for generating elements for it).

_class_ hypothesis.extra.pandas.column(

_name\=None_,

_elements\=None_,

_dtype\=None_,

_fill\=None_,

_unique\=False_,

)[¶](#hypothesis.extra.pandas.column "Link to this definition")

Data object for describing a column in a DataFrame.

Arguments:

*   name: the column name, or None to default to the column position. Must be hashable, but can otherwise be any value supported as a pandas column name.
    
*   elements: the strategy for generating values in this column, or None to infer it from the dtype.
    
*   dtype: the dtype of the column, or None to infer it from the element strategy. At least one of dtype or elements must be provided.
    
*   fill: A default value for elements of the column. See [`arrays()`](#hypothesis.extra.numpy.arrays "hypothesis.extra.numpy.arrays") for a full explanation.
    
*   unique: If all values in this column should be distinct.
    

hypothesis.extra.pandas.columns(

_names\_or\_number_,

_\*_,

_dtype\=None_,

_elements\=None_,

_fill\=None_,

_unique\=False_,

)[¶](#hypothesis.extra.pandas.columns "Link to this definition")

A convenience function for producing a list of [`column`](#hypothesis.extra.pandas.column "hypothesis.extra.pandas.column") objects of the same general shape.

The names\_or\_number argument is either a sequence of values, the elements of which will be used as the name for individual column objects, or a number, in which case that many unnamed columns will be created. All other arguments are passed through verbatim to create the columns.

hypothesis.extra.pandas.data\_frames(_columns\=None_, _\*_, _rows\=None_, _index\=None_)[¶](#hypothesis.extra.pandas.data_frames "Link to this definition")

Provides a strategy for producing a [`pandas.DataFrame`](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html#pandas.DataFrame "(in pandas v2.3.3)").

Arguments:

*   columns: An iterable of [`column`](#hypothesis.extra.pandas.column "hypothesis.extra.pandas.column") objects describing the shape of the generated DataFrame.
    
*   rows: A strategy for generating a row object. Should generate either dicts mapping column names to values or a sequence mapping column position to the value in that position (note that unlike the [`pandas.DataFrame`](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html#pandas.DataFrame "(in pandas v2.3.3)") constructor, single values are not allowed here. Passing e.g. an integer is an error, even if there is only one column).
    
    At least one of rows and columns must be provided. If both are provided then the generated rows will be validated against the columns and an error will be raised if they don’t match.
    
    Caveats on using rows:
    
    *   In general you should prefer using columns to rows, and only use rows if the columns interface is insufficiently flexible to describe what you need - you will get better performance and example quality that way.
        
    *   If you provide rows and not columns, then the shape and dtype of the resulting DataFrame may vary. e.g. if you have a mix of int and float in the values for one column in your row entries, the column will sometimes have an integral dtype and sometimes a float.
        
*   index: If not None, a strategy for generating indexes for the resulting DataFrame. This can generate either [`pandas.Index`](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.Index.html#pandas.Index "(in pandas v2.3.3)") objects or any sequence of values (which will be passed to the Index constructor).
    
    You will probably find it most convenient to use the [`indexes()`](#hypothesis.extra.pandas.indexes "hypothesis.extra.pandas.indexes") or [`range_indexes()`](#hypothesis.extra.pandas.range_indexes "hypothesis.extra.pandas.range_indexes") function to produce values for this argument.
    

Usage:

The expected usage pattern is that you use [`column`](#hypothesis.extra.pandas.column "hypothesis.extra.pandas.column") and [`columns()`](#hypothesis.extra.pandas.columns "hypothesis.extra.pandas.columns") to specify a fixed shape of the DataFrame you want as follows. For example the following gives a two column data frame:

\>>> from hypothesis.extra.pandas import column, data\_frames
\>>> data\_frames(\[
... column('A', dtype\=int), column('B', dtype\=float)\]).example()
            A              B
0  2021915903  1.793898e+232
1  1146643993            inf
2 -2096165693   1.000000e+07

If you want the values in different columns to interact in some way you can use the rows argument. For example the following gives a two column DataFrame where the value in the first column is always at most the value in the second:

\>>> from hypothesis.extra.pandas import column, data\_frames
\>>> import hypothesis.strategies as st
\>>> data\_frames(
...     rows\=st.tuples(st.floats(allow\_nan\=False),
...                    st.floats(allow\_nan\=False)).map(sorted)
... ).example()
               0             1
0  -3.402823e+38  9.007199e+15
1 -1.562796e-298  5.000000e-01

You can also combine the two:

\>>> from hypothesis.extra.pandas import columns, data\_frames
\>>> import hypothesis.strategies as st
\>>> data\_frames(
...     columns\=columns(\["lo", "hi"\], dtype\=float),
...     rows\=st.tuples(st.floats(allow\_nan\=False),
...                    st.floats(allow\_nan\=False)).map(sorted)
... ).example()
         lo            hi
0   9.314723e-49  4.353037e+45
1  -9.999900e-01  1.000000e+07
2 -2.152861e+134 -1.069317e-73

(Note that the column dtype must still be specified and will not be inferred from the rows. This restriction may be lifted in future).

Combining rows and columns has the following behaviour:

*   The column names and dtypes will be used.
    
*   If the column is required to be unique, this will be enforced.
    
*   Any values missing from the generated rows will be provided using the column’s fill.
    
*   Any values in the row not present in the column specification (if dicts are passed, if there are keys with no corresponding column name, if sequences are passed if there are too many items) will result in InvalidArgument being raised.
    

hypothesis.extra.pandas.indexes(

_\*_,

_elements\=None_,

_dtype\=None_,

_min\_size\=0_,

_max\_size\=None_,

_unique\=True_,

_name\=none()_,

)[¶](#hypothesis.extra.pandas.indexes "Link to this definition")

Provides a strategy for producing a [`pandas.Index`](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.Index.html#pandas.Index "(in pandas v2.3.3)").

Arguments:

*   elements is a strategy which will be used to generate the individual values of the index. If None, it will be inferred from the dtype. Note: even if the elements strategy produces tuples, the generated value will not be a MultiIndex, but instead be a normal index whose elements are tuples.
    
*   dtype is the dtype of the resulting index. If None, it will be inferred from the elements strategy. At least one of dtype or elements must be provided.
    
*   min\_size is the minimum number of elements in the index.
    
*   max\_size is the maximum number of elements in the index. If None then it will default to a suitable small size. If you want larger indexes you should pass a max\_size explicitly.
    
*   unique specifies whether all of the elements in the resulting index should be distinct.
    
*   name is a strategy for strings or `None`, which will be passed to the [`pandas.Index`](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.Index.html#pandas.Index "(in pandas v2.3.3)") constructor.
    

hypothesis.extra.pandas.range\_indexes(_min\_size\=0_, _max\_size\=None_, _name\=none()_)[¶](#hypothesis.extra.pandas.range_indexes "Link to this definition")

Provides a strategy which generates an [`Index`](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.Index.html#pandas.Index "(in pandas v2.3.3)") whose values are 0, 1, …, n for some n.

Arguments:

*   min\_size is the smallest number of elements the index can have.
    
*   max\_size is the largest number of elements the index can have. If None it will default to some suitable value based on min\_size.
    
*   name is the name of the index. If st.none(), the index will have no name.
    

hypothesis.extra.pandas.series(

_\*_,

_elements\=None_,

_dtype\=None_,

_index\=None_,

_fill\=None_,

_unique\=False_,

_name\=none()_,

)[¶](#hypothesis.extra.pandas.series "Link to this definition")

Provides a strategy for producing a [`pandas.Series`](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.Series.html#pandas.Series "(in pandas v2.3.3)").

Arguments:

*   elements: a strategy that will be used to generate the individual values in the series. If None, we will attempt to infer a suitable default from the dtype.
    
*   dtype: the dtype of the resulting series and may be any value that can be passed to [`numpy.dtype`](https://numpy.org/doc/stable/reference/generated/numpy.dtype.html#numpy.dtype "(in NumPy v2.3)"). If None, will use pandas’s standard behaviour to infer it from the type of the elements values. Note that if the type of values that comes out of your elements strategy varies, then so will the resulting dtype of the series.
    
*   index: If not None, a strategy for generating indexes for the resulting Series. This can generate either [`pandas.Index`](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.Index.html#pandas.Index "(in pandas v2.3.3)") objects or any sequence of values (which will be passed to the Index constructor).
    
    You will probably find it most convenient to use the [`indexes()`](#hypothesis.extra.pandas.indexes "hypothesis.extra.pandas.indexes") or [`range_indexes()`](#hypothesis.extra.pandas.range_indexes "hypothesis.extra.pandas.range_indexes") function to produce values for this argument.
    
*   name: is a strategy for strings or `None`, which will be passed to the [`pandas.Series`](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.Series.html#pandas.Series "(in pandas v2.3.3)") constructor.
    

Usage:

\>>> series(dtype\=int).example()
0   -2001747478
1    1153062837

###### Supported versions[¶](#supported-versions "Link to this heading")

There is quite a lot of variation between pandas versions. We only commit to supporting the latest version of pandas, but older minor versions are supported on a “best effort” basis. Hypothesis is currently tested against and confirmed working with every Pandas minor version from 1.1 through to 2.2.

Releases that are not the latest patch release of their minor version are not tested or officially supported, but will probably also work unless you hit a pandas bug.

##### Array API[¶](#array-api "Link to this heading")

Note

Several array libraries have more library-specific strategies, including [Xarray](https://pypi.org/project/xarray/) (via their [upstream strategies](https://docs.xarray.dev/en/stable/user-guide/testing.html#testing-hypothesis "(in xarray v2025.11.1)")) and [NumPy](https://pypi.org/project/NumPy/) (via [its Hypothesis extra](#hypothesis-numpy)). Of course, strategies in the Array API namespace can still be used to test Xarray or NumPy, just like any other array library.

Hypothesis offers strategies for [Array API](https://data-apis.org/) adopting libraries in the `hypothesis.extra.array_api` package. See [issue #3037](https://github.com/HypothesisWorks/hypothesis/issues/3037) for more details. If you want to test with [CuPy](https://pypi.org/project/cupy/), [Dask](https://pypi.org/project/dask/), [JAX](https://pypi.org/project/jax/), [MXNet](https://pypi.org/project/maxnet/), [PyTorch](https://pypi.org/project/torch/), [TensorFlow](https://pypi.org/project/tensorflow/), or [Xarray](https://pypi.org/project/xarray/) - or just [NumPy](https://pypi.org/project/numpy/) - this is the extension for you!

hypothesis.extra.array\_api.make\_strategies\_namespace(_xp_, _\*_, _api\_version\=None_)[¶](#hypothesis.extra.array_api.make_strategies_namespace "Link to this definition")

Creates a strategies namespace for the given array module.

*   `xp` is the Array API library to automatically pass to the namespaced methods.
    
*   `api_version` is the version of the Array API which the returned strategies namespace should conform to. If `None`, the latest API version which `xp` supports will be inferred from `xp.__array_api_version__`. If a version string in the `YYYY.MM` format, the strategies namespace will conform to that version if supported.
    

A [`types.SimpleNamespace`](https://docs.python.org/3/library/types.html#types.SimpleNamespace "(in Python v3.14)") is returned which contains all the strategy methods in this module but without requiring the `xp` argument. Creating and using a strategies namespace for NumPy’s Array API implementation would go like this:

\>>> xp.\_\_array\_api\_version\_\_  \# xp is your desired array library
'2021.12'
\>>> xps \= make\_strategies\_namespace(xp)
\>>> xps.api\_version
'2021.12'
\>>> x \= xps.arrays(xp.int8, (2, 3)).example()
\>>> x
Array(\[\[-8,  6,  3\],
       \[-6,  4,  6\]\], dtype=int8)
\>>> x.\_\_array\_namespace\_\_() is xp
True

The resulting namespace contains all our familiar strategies like [`arrays()`](#xps.arrays "xps.arrays") and [`from_dtype()`](#xps.from_dtype "xps.from_dtype"), but based on the Array API standard semantics and returning objects from the `xp` module:

xps.from\_dtype(

_dtype_,

_\*_,

_min\_value\=None_,

_max\_value\=None_,

_allow\_nan\=None_,

_allow\_infinity\=None_,

_allow\_subnormal\=None_,

_exclude\_min\=None_,

_exclude\_max\=None_,

)[¶](#xps.from_dtype "Link to this definition")

Return a strategy for any value of the given dtype.

Values generated are of the Python scalar which is [promotable](https://data-apis.org/array-api/latest/API_specification/type_promotion.html) to `dtype`, where the values do not exceed its bounds.

*   `dtype` may be a dtype object or the string name of a [valid dtype](https://data-apis.org/array-api/latest/API_specification/data_types.html).
    

Compatible `**kwargs` are passed to the inferred strategy function for integers and floats. This allows you to customise the min and max values, and exclude non-finite numbers. This is particularly useful when kwargs are passed through from [`arrays()`](#xps.arrays "xps.arrays"), as it seamlessly handles the `width` or other representable bounds for you.

xps.arrays(

_dtype_,

_shape_,

_\*_,

_elements\=None_,

_fill\=None_,

_unique\=False_,

)[¶](#xps.arrays "Link to this definition")

Returns a strategy for [arrays](https://data-apis.org/array-api/latest/API_specification/array_object.html).

*   `dtype` may be a [valid dtype](https://data-apis.org/array-api/latest/API_specification/data_types.html) object or name, or a strategy that generates such values.
    
*   `shape` may be an integer >= 0, a tuple of such integers, or a strategy that generates such values.
    
*   `elements` is a strategy for values to put in the array. If `None` then a suitable value will be inferred based on the dtype, which may give any legal value (including e.g. NaN for floats). If a mapping, it will be passed as `**kwargs` to [`from_dtype()`](#xps.from_dtype "xps.from_dtype") when inferring based on the dtype.
    
*   `fill` is a strategy that may be used to generate a single background value for the array. If `None`, a suitable default will be inferred based on the other arguments. If set to [`nothing()`](#hypothesis.strategies.nothing "hypothesis.strategies.nothing") then filling behaviour will be disabled entirely and every element will be generated independently.
    
*   `unique` specifies if the elements of the array should all be distinct from one another; if fill is also set, the only valid values for fill to return are NaN values.
    

Arrays of specified `dtype` and `shape` are generated for example like this:

\>>> from numpy import array\_api as xp
\>>> xps.arrays(xp, xp.int8, (2, 3)).example()
Array(\[\[-8,  6,  3\],
       \[-6,  4,  6\]\], dtype=int8)

Specifying element boundaries by a [`dict`](https://docs.python.org/3/library/stdtypes.html#dict "(in Python v3.14)") of the kwargs to pass to [`from_dtype()`](#xps.from_dtype "xps.from_dtype") will ensure `dtype` bounds will be respected.

\>>> xps.arrays(xp, xp.int8, 3, elements\={"min\_value": 10}).example()
Array(\[125, 13, 79\], dtype=int8)

\>>> xps.arrays(xp, xp.float32, 3, elements\=floats(0, 1, width\=32)).example()
Array(\[ 0.88974794,  0.77387938,  0.1977879 \], dtype=float32)

Array values are generated in two parts:

1.  A single value is drawn from the fill strategy and is used to create a filled array.
    
2.  Some subset of the coordinates of the array are populated with a value drawn from the elements strategy (or its inferred form).
    

You can set `fill` to [`nothing()`](#hypothesis.strategies.nothing "hypothesis.strategies.nothing") if you want to disable this behaviour and draw a value for every element.

By default `arrays` will attempt to infer the correct fill behaviour: if `unique` is also `True`, no filling will occur. Otherwise, if it looks safe to reuse the values of elements across multiple coordinates (this will be the case for any inferred strategy, and for most of the builtins, but is not the case for mutable values or strategies built with flatmap, map, composite, etc.) then it will use the elements strategy as the fill, else it will default to having no fill.

Having a fill helps Hypothesis craft high quality examples, but its main importance is when the array generated is large: Hypothesis is primarily designed around testing small examples. If you have arrays with hundreds or more elements, having a fill value is essential if you want your tests to run in reasonable time.

xps.array\_shapes(

_\*_,

_min\_dims\=1_,

_max\_dims\=None_,

_min\_side\=1_,

_max\_side\=None_,

)[¶](#xps.array_shapes "Link to this definition")

Return a strategy for array shapes (tuples of int >= 1).

*   `min_dims` is the smallest length that the generated shape can possess.
    
*   `max_dims` is the largest length that the generated shape can possess, defaulting to `min_dims + 2`.
    
*   `min_side` is the smallest size that a dimension can possess.
    
*   `max_side` is the largest size that a dimension can possess, defaulting to `min_side + 5`.
    

xps.scalar\_dtypes()[¶](#xps.scalar_dtypes "Link to this definition")

Return a strategy for all [valid dtype](https://data-apis.org/array-api/latest/API_specification/data_types.html) objects.

xps.boolean\_dtypes()[¶](#xps.boolean_dtypes "Link to this definition")

Return a strategy for just the boolean dtype object.

xps.numeric\_dtypes()[¶](#xps.numeric_dtypes "Link to this definition")

Return a strategy for all numeric dtype objects.

xps.real\_dtypes()[¶](#xps.real_dtypes "Link to this definition")

Return a strategy for all real-valued dtype objects.

xps.integer\_dtypes(_\*_, _sizes\=(8, 16, 32, 64)_)[¶](#xps.integer_dtypes "Link to this definition")

Return a strategy for signed integer dtype objects.

`sizes` contains the signed integer sizes in bits, defaulting to `(8, 16, 32, 64)` which covers all valid sizes.

xps.unsigned\_integer\_dtypes(_\*_, _sizes\=(8, 16, 32, 64)_)[¶](#xps.unsigned_integer_dtypes "Link to this definition")

Return a strategy for unsigned integer dtype objects.

`sizes` contains the unsigned integer sizes in bits, defaulting to `(8, 16, 32, 64)` which covers all valid sizes.

xps.floating\_dtypes(_\*_, _sizes\=(32, 64)_)[¶](#xps.floating_dtypes "Link to this definition")

Return a strategy for real-valued floating-point dtype objects.

`sizes` contains the floating-point sizes in bits, defaulting to `(32, 64)` which covers all valid sizes.

xps.complex\_dtypes(_\*_, _sizes\=(64, 128)_)[¶](#xps.complex_dtypes "Link to this definition")

Return a strategy for complex dtype objects.

`sizes` contains the complex sizes in bits, defaulting to `(64, 128)` which covers all valid sizes.

xps.valid\_tuple\_axes(_ndim_, _\*_, _min\_size\=0_, _max\_size\=None_)[¶](#xps.valid_tuple_axes "Link to this definition")

Return a strategy for permissible tuple-values for the `axis` argument in Array API sequential methods e.g. `sum`, given the specified dimensionality.

All tuples will have a length >= `min_size` and <= `max_size`. The default value for `max_size` is `ndim`.

Examples from this strategy shrink towards an empty tuple, which render most sequential functions as no-ops.

The following are some examples drawn from this strategy.

\>>> \[valid\_tuple\_axes(3).example() for i in range(4)\]
\[(-3, 1), (0, 1, -1), (0, 2), (0, -2, 2)\]

`valid_tuple_axes` can be joined with other strategies to generate any type of valid axis object, i.e. integers, tuples, and `None`:

any\_axis\_strategy \= none() | integers(\-ndim, ndim \- 1) | valid\_tuple\_axes(ndim)

xps.broadcastable\_shapes(

_shape_,

_\*_,

_min\_dims\=0_,

_max\_dims\=None_,

_min\_side\=1_,

_max\_side\=None_,

)[¶](#xps.broadcastable_shapes "Link to this definition")

Return a strategy for shapes that are broadcast-compatible with the provided shape.

Examples from this strategy shrink towards a shape with length `min_dims`. The size of an aligned dimension shrinks towards size `1`. The size of an unaligned dimension shrink towards `min_side`.

*   `shape` is a tuple of integers.
    
*   `min_dims` is the smallest length that the generated shape can possess.
    
*   `max_dims` is the largest length that the generated shape can possess, defaulting to `max(len(shape), min_dims) + 2`.
    
*   `min_side` is the smallest size that an unaligned dimension can possess.
    
*   `max_side` is the largest size that an unaligned dimension can possess, defaulting to 2 plus the size of the largest aligned dimension.
    

The following are some examples drawn from this strategy.

\>>> \[broadcastable\_shapes(shape\=(2, 3)).example() for i in range(5)\]
\[(1, 3), (), (2, 3), (2, 1), (4, 1, 3), (3, )\]

xps.mutually\_broadcastable\_shapes(

_num\_shapes_,

_\*_,

_base\_shape\=()_,

_min\_dims\=0_,

_max\_dims\=None_,

_min\_side\=1_,

_max\_side\=None_,

)[¶](#xps.mutually_broadcastable_shapes "Link to this definition")

Return a strategy for a specified number of shapes N that are mutually-broadcastable with one another and with the provided base shape.

*   `num_shapes` is the number of mutually broadcast-compatible shapes to generate.
    
*   `base_shape` is the shape against which all generated shapes can broadcast. The default shape is empty, which corresponds to a scalar and thus does not constrain broadcasting at all.
    
*   `min_dims` is the smallest length that the generated shape can possess.
    
*   `max_dims` is the largest length that the generated shape can possess, defaulting to `max(len(shape), min_dims) + 2`.
    
*   `min_side` is the smallest size that an unaligned dimension can possess.
    
*   `max_side` is the largest size that an unaligned dimension can possess, defaulting to 2 plus the size of the largest aligned dimension.
    

The strategy will generate a [`typing.NamedTuple`](https://docs.python.org/3/library/typing.html#typing.NamedTuple "(in Python v3.14)") containing:

*   `input_shapes` as a tuple of the N generated shapes.
    
*   `result_shape` as the resulting shape produced by broadcasting the N shapes with the base shape.
    

The following are some examples drawn from this strategy.

\>>> \# Draw three shapes where each shape is broadcast-compatible with (2, 3)
... strat \= mutually\_broadcastable\_shapes(num\_shapes\=3, base\_shape\=(2, 3))
\>>> for \_ in range(5):
...     print(strat.example())
BroadcastableShapes(input\_shapes=((4, 1, 3), (4, 2, 3), ()), result\_shape=(4, 2, 3))
BroadcastableShapes(input\_shapes=((3,), (1, 3), (2, 3)), result\_shape=(2, 3))
BroadcastableShapes(input\_shapes=((), (), ()), result\_shape=())
BroadcastableShapes(input\_shapes=((3,), (), (3,)), result\_shape=(3,))
BroadcastableShapes(input\_shapes=((1, 2, 3), (3,), ()), result\_shape=(1, 2, 3))

xps.indices(

_shape_,

_\*_,

_min\_dims\=0_,

_max\_dims\=None_,

_allow\_newaxis\=False_,

_allow\_ellipsis\=True_,

)[¶](#xps.indices "Link to this definition")

Return a strategy for [valid indices](https://data-apis.org/array-api/latest/API_specification/indexing.html) of arrays with the specified shape, which may include dimensions of size zero.

It generates tuples containing some mix of integers, [`slice`](https://docs.python.org/3/library/functions.html#slice "(in Python v3.14)") objects, `...` (an `Ellipsis`), and `None`. When a length-one tuple would be generated, this strategy may instead return the element which will index the first axis, e.g. `5` instead of `(5,)`.

*   `shape` is the shape of the array that will be indexed, as a tuple of integers >= 0. This must be at least two-dimensional for a tuple to be a valid index; for one-dimensional arrays use [`slices()`](#hypothesis.strategies.slices "hypothesis.strategies.slices") instead.
    
*   `min_dims` is the minimum dimensionality of the resulting array from use of the generated index.
    
*   `max_dims` is the the maximum dimensionality of the resulting array, defaulting to `len(shape) if not allow_newaxis else max(len(shape), min_dims) + 2`.
    
*   `allow_ellipsis` specifies whether `None` is allowed in the index.
    
*   `allow_ellipsis` specifies whether `...` is allowed in the index.
    

##### Django[¶](#django "Link to this heading")

See also

See the [Django API reference](#hypothesis-django) for documentation on testing Django with Hypothesis.

hypothesis.extra.django.from\_model(_model_, _/_, _\*\*field\_strategies_)[¶](#hypothesis.extra.django.from_model "Link to this definition")

Return a strategy for examples of `model`.

Warning

Hypothesis creates saved models. This will run inside your testing transaction when using the test runner, but if you use the dev console this will leave debris in your database.

`model` must be an subclass of [`Model`](http://docs.djangoproject.com/en/stable/ref/models/instances/#django.db.models.Model "(in Django v5.2)"). Strategies for fields may be passed as keyword arguments, for example `is_staff=st.just(False)`. In order to support models with fields named “model”, this is a positional-only parameter.

Hypothesis can often infer a strategy based the field type and validators, and will attempt to do so for any required fields. No strategy will be inferred for an [`AutoField`](http://docs.djangoproject.com/en/stable/ref/models/fields/#django.db.models.AutoField "(in Django v5.2)"), nullable field, foreign key, or field for which a keyword argument is passed to `from_model()`. For example, a Shop type with a foreign key to Company could be generated with:

shop\_strategy \= from\_model(Shop, company\=from\_model(Company))

Like for [`builds()`](#hypothesis.strategies.builds "hypothesis.strategies.builds"), you can pass `...` ([`Ellipsis`](https://docs.python.org/3/library/constants.html#Ellipsis "(in Python v3.14)")) as a keyword argument to infer a strategy for a field which has a default value instead of using the default.

hypothesis.extra.django.from\_form(_form_, _form\_kwargs\=None_, _\*\*field\_strategies_)[¶](#hypothesis.extra.django.from_form "Link to this definition")

Return a strategy for examples of `form`.

`form` must be an subclass of [`Form`](http://docs.djangoproject.com/en/stable/ref/forms/api/#django.forms.Form "(in Django v5.2)"). Strategies for fields may be passed as keyword arguments, for example `is_staff=st.just(False)`.

Hypothesis can often infer a strategy based the field type and validators, and will attempt to do so for any required fields. No strategy will be inferred for a disabled field or field for which a keyword argument is passed to `from_form()`.

This function uses the fields of an unbound `form` instance to determine field strategies, any keyword arguments needed to instantiate the unbound `form` instance can be passed into `from_form()` as a dict with the keyword `form_kwargs`. E.g.:

shop\_strategy \= from\_form(Shop, form\_kwargs\={"company\_id": 5})

Like for [`builds()`](#hypothesis.strategies.builds "hypothesis.strategies.builds"), you can pass `...` ([`Ellipsis`](https://docs.python.org/3/library/constants.html#Ellipsis "(in Python v3.14)")) as a keyword argument to infer a strategy for a field which has a default value instead of using the default.

hypothesis.extra.django.from\_field(_field_)[¶](#hypothesis.extra.django.from_field "Link to this definition")

Return a strategy for values that fit the given field.

This function is used by [`from_form()`](#hypothesis.extra.django.from_form "hypothesis.extra.django.from_form") and [`from_model()`](#hypothesis.extra.django.from_model "hypothesis.extra.django.from_model") for any fields that require a value, or for which you passed `...` ([`Ellipsis`](https://docs.python.org/3/library/constants.html#Ellipsis "(in Python v3.14)")) to infer a strategy from an annotation.

It’s pretty similar to the core [`from_type()`](#hypothesis.strategies.from_type "hypothesis.strategies.from_type") function, with a subtle but important difference: `from_field` takes a Field _instance_, rather than a Field _subtype_, so that it has access to instance attributes such as string length and validators.

hypothesis.extra.django.register\_field\_strategy(_field\_type_, _strategy_)[¶](#hypothesis.extra.django.register_field_strategy "Link to this definition")

Add an entry to the global field-to-strategy lookup used by [`from_field()`](#hypothesis.extra.django.from_field "hypothesis.extra.django.from_field").

`field_type` must be a subtype of [`django.db.models.Field`](http://docs.djangoproject.com/en/stable/ref/models/fields/#django.db.models.Field "(in Django v5.2)") or [`django.forms.Field`](http://docs.djangoproject.com/en/stable/ref/forms/fields/#django.forms.Field "(in Django v5.2)"), which must not already be registered. `strategy` must be a [`SearchStrategy`](#hypothesis.strategies.SearchStrategy "hypothesis.strategies.SearchStrategy").

##### hypothesis\[lark\][¶](#hypothesis-lark "Link to this heading")

Note

Strategies in this module require the `hypothesis[lark]` [extra](#document-extras), via `pip install hypothesis[lark]`.

This extra can be used to generate strings matching any context-free grammar, using the [Lark parser library](https://github.com/lark-parser/lark).

It currently only supports Lark’s native EBNF syntax, but we plan to extend this to support other common syntaxes such as ANTLR and [**RFC 5234**](https://datatracker.ietf.org/doc/html/rfc5234.html) ABNF. Lark already [supports loading grammars](https://lark-parser.readthedocs.io/en/stable/tools.html#importing-grammars-from-nearley-js) from [nearley.js](https://nearley.js.org/), so you may not have to write your own at all.

hypothesis.extra.lark.from\_lark(

_grammar_,

_\*_,

_start\=None_,

_explicit\=None_,

_alphabet\=characters(codec='utf-8')_,

)[¶](#hypothesis.extra.lark.from_lark "Link to this definition")

A strategy for strings accepted by the given context-free grammar.

`grammar` must be a `Lark` object, which wraps an EBNF specification. The Lark EBNF grammar reference can be found [here](https://lark-parser.readthedocs.io/en/latest/grammar.html).

`from_lark` will automatically generate strings matching the nonterminal `start` symbol in the grammar, which was supplied as an argument to the Lark class. To generate strings matching a different symbol, including terminals, you can override this by passing the `start` argument to `from_lark`. Note that Lark may remove unreachable productions when the grammar is compiled, so you should probably pass the same value for `start` to both.

Currently `from_lark` does not support grammars that need custom lexing. Any lexers will be ignored, and any undefined terminals from the use of `%declare` will result in generation errors. To define strategies for such terminals, pass a dictionary mapping their name to a corresponding strategy as the `explicit` argument.

The [hypothesmith](https://pypi.org/project/hypothesmith/) project includes a strategy for Python source, based on a grammar and careful post-processing.

Example grammars, which may provide a useful starting point for your tests, can be found [in the Lark repository](https://github.com/lark-parser/lark/tree/master/examples) and in [this third-party collection](https://github.com/ligurio/lark-grammars).

##### hypothesis\[pytz\][¶](#hypothesis-pytz "Link to this heading")

Note

Strategies in this module require the `hypothesis[pytz]` [extra](#document-extras), via `pip install hypothesis[pytz]`.

This module provides [pytz](https://pypi.org/project/pytz/) timezones.

If you are unable to use the stdlib [`zoneinfo`](https://docs.python.org/3/library/zoneinfo.html#module-zoneinfo "(in Python v3.14)") module, e.g. via the [`hypothesis.strategies.timezones()`](#hypothesis.strategies.timezones "hypothesis.strategies.timezones") strategy, you can use this strategy with [`hypothesis.strategies.datetimes()`](#hypothesis.strategies.datetimes "hypothesis.strategies.datetimes") and [`hypothesis.strategies.times()`](#hypothesis.strategies.times "hypothesis.strategies.times") to produce timezone-aware values.

Warning

Since [`zoneinfo`](https://docs.python.org/3/library/zoneinfo.html#module-zoneinfo "(in Python v3.14)") was added in Python 3.9, this extra is deprecated. We intend to remove it after libraries such as Pandas and Django complete their own migrations.

hypothesis.extra.pytz.timezones()[¶](#hypothesis.extra.pytz.timezones "Link to this definition")

Any timezone in the Olsen database, as a pytz tzinfo object.

This strategy minimises to UTC, or the smallest possible fixed offset, and is designed for use with [`hypothesis.strategies.datetimes()`](#hypothesis.strategies.datetimes "hypothesis.strategies.datetimes").

Tip

Prefer the [`hypothesis.strategies.timezones()`](#hypothesis.strategies.timezones "hypothesis.strategies.timezones") strategy, which uses the stdlib [`zoneinfo`](https://docs.python.org/3/library/zoneinfo.html#module-zoneinfo "(in Python v3.14)") module and avoids [the many footguns in pytz](https://blog.ganssle.io/articles/2018/03/pytz-fastest-footgun.html).

##### hypothesis\[dateutil\][¶](#hypothesis-dateutil "Link to this heading")

Note

Strategies in this module require the `hypothesis[dateutil]` [extra](#document-extras), via `pip install hypothesis[dateutil]`.

This module provides [dateutil](https://pypi.org/project/python-dateutil/) timezones.

You can use this strategy to make [`datetimes()`](#hypothesis.strategies.datetimes "hypothesis.strategies.datetimes") and [`times()`](#hypothesis.strategies.times "hypothesis.strategies.times") produce timezone-aware values.

Tip

Consider using the stdlib [`zoneinfo`](https://docs.python.org/3/library/zoneinfo.html#module-zoneinfo "(in Python v3.14)") module, via [`st.timezones()`](#hypothesis.strategies.timezones "hypothesis.strategies.timezones").

hypothesis.extra.dateutil.timezones()[¶](#hypothesis.extra.dateutil.timezones "Link to this definition")

Any timezone from [dateutil](https://pypi.org/project/python-dateutil/).

This strategy minimises to UTC, or the timezone with the smallest offset from UTC as of 2000-01-01, and is designed for use with [`datetimes()`](#hypothesis.strategies.datetimes "hypothesis.strategies.datetimes").

Note that the timezones generated by the strategy may vary depending on the configuration of your machine. See the dateutil documentation for more information.

#### Integrations Reference[¶](#integrations-reference "Link to this heading")

Reference for Hypothesis features with a defined interface, but no code API.

##### Ghostwriter[¶](#ghostwriter "Link to this heading")

Writing tests with Hypothesis frees you from the tedium of deciding on and writing out specific inputs to test. Now, the `hypothesis.extra.ghostwriter` module can write your test functions for you too!

The idea is to provide **an easy way to start** property-based testing, **and a seamless transition** to more complex test code - because ghostwritten tests are source code that you could have written for yourself.

So just pick a function you’d like tested, and feed it to one of the functions below. They follow imports, use but do not require type annotations, and generally do their best to write you a useful test. You can also use [our command-line interface](#hypothesis-cli):

$ hypothesis write --help
Usage: hypothesis write \[OPTIONS\] FUNC...

  \`hypothesis write\` writes property-based tests for you!

  Type annotations are helpful but not required for our advanced
  introspection and templating logic.  Try running the examples below to see
  how it works:

      hypothesis write gzip
      hypothesis write numpy.matmul
      hypothesis write pandas.from\_dummies
      hypothesis write re.compile --except re.error
      hypothesis write --equivalent ast.literal\_eval eval
      hypothesis write --roundtrip json.dumps json.loads
      hypothesis write --style=unittest --idempotent sorted
      hypothesis write --binary-op operator.add

Options:
  --roundtrip                 start by testing write/read or encode/decode!
  --equivalent                very useful when optimising or refactoring code
  --errors-equivalent         --equivalent, but also allows consistent errors
  --idempotent                check that f(x) == f(f(x))
  --binary-op                 associativity, commutativity, identity element
  --style \[pytest|unittest\]   pytest-style function, or unittest-style method?
  -e, --except OBJ\_NAME       dotted name of exception(s) to ignore
  --annotate / --no-annotate  force ghostwritten tests to be type-annotated
                              (or not).  By default, match the code to test.
  -h, --help                  Show this message and exit.

Tip

Using a light theme? Hypothesis respects [NO\_COLOR](https://no-color.org/) and `DJANGO_COLORS=light`.

Note

The ghostwriter requires [black](https://pypi.org/project/black/), but the generated code only requires Hypothesis itself.

Note

Legal questions? While the ghostwriter fragments and logic is under the MPL-2.0 license like the rest of Hypothesis, the _output_ from the ghostwriter is made available under the [Creative Commons Zero (CC0)](https://creativecommons.org/public-domain/cc0/) public domain dedication, so you can use it without any restrictions.

hypothesis.extra.ghostwriter.magic(

_\*modules\_or\_functions_,

_except\_\=()_,

_style\='pytest'_,

_annotate\=None_,

)[¶](#hypothesis.extra.ghostwriter.magic "Link to this definition")

Guess which ghostwriters to use, for a module or collection of functions.

As for all ghostwriters, the `except_` argument should be an [`Exception`](https://docs.python.org/3/library/exceptions.html#Exception "(in Python v3.14)") or tuple of exceptions, and `style` may be either `"pytest"` to write test functions or `"unittest"` to write test methods and [`TestCase`](https://docs.python.org/3/library/unittest.html#unittest.TestCase "(in Python v3.14)").

After finding the public functions attached to any modules, the `magic` ghostwriter looks for pairs of functions to pass to [`roundtrip()`](#hypothesis.extra.ghostwriter.roundtrip "hypothesis.extra.ghostwriter.roundtrip"), then checks for [`binary_operation()`](#hypothesis.extra.ghostwriter.binary_operation "hypothesis.extra.ghostwriter.binary_operation") and [`ufunc()`](#hypothesis.extra.ghostwriter.ufunc "hypothesis.extra.ghostwriter.ufunc") functions, and any others are passed to [`fuzz()`](#hypothesis.extra.ghostwriter.fuzz "hypothesis.extra.ghostwriter.fuzz").

For example, try **hypothesis write gzip** on the command line!

hypothesis.extra.ghostwriter.fuzz(_func_, _\*_, _except\_\=()_, _style\='pytest'_, _annotate\=None_)[¶](#hypothesis.extra.ghostwriter.fuzz "Link to this definition")

Write source code for a property-based test of `func`.

The resulting test checks that valid input only leads to expected exceptions. For example:

from re import compile, error

from hypothesis.extra import ghostwriter

ghostwriter.fuzz(compile, except\_\=error)

Gives:

\# This test code was written by the \`hypothesis.extra.ghostwriter\` module
\# and is provided under the Creative Commons Zero public domain dedication.
import re

from hypothesis import given, reject, strategies as st

\# TODO: replace st.nothing() with an appropriate strategy

@given(pattern\=st.nothing(), flags\=st.just(0))
def test\_fuzz\_compile(pattern, flags):
    try:
        re.compile(pattern\=pattern, flags\=flags)
    except re.error:
        reject()

Note that it includes all the required imports. Because the `pattern` parameter doesn’t have annotations or a default argument, you’ll need to specify a strategy - for example [`text()`](#hypothesis.strategies.text "hypothesis.strategies.text") or [`binary()`](#hypothesis.strategies.binary "hypothesis.strategies.binary"). After that, you have a test!

hypothesis.extra.ghostwriter.idempotent(

_func_,

_\*_,

_except\_\=()_,

_style\='pytest'_,

_annotate\=None_,

)[¶](#hypothesis.extra.ghostwriter.idempotent "Link to this definition")

Write source code for a property-based test of `func`.

The resulting test checks that if you call `func` on it’s own output, the result does not change. For example:

from typing import Sequence

from hypothesis.extra import ghostwriter

def timsort(seq: Sequence\[int\]) \-> Sequence\[int\]:
    return sorted(seq)

ghostwriter.idempotent(timsort)

Gives:

\# This test code was written by the \`hypothesis.extra.ghostwriter\` module
\# and is provided under the Creative Commons Zero public domain dedication.

from hypothesis import given, strategies as st

@given(seq\=st.one\_of(st.binary(), st.binary().map(bytearray), st.lists(st.integers())))
def test\_idempotent\_timsort(seq):
    result \= timsort(seq\=seq)
    repeat \= timsort(seq\=result)
    assert result \== repeat, (result, repeat)

hypothesis.extra.ghostwriter.roundtrip(_\*funcs_, _except\_\=()_, _style\='pytest'_, _annotate\=None_)[¶](#hypothesis.extra.ghostwriter.roundtrip "Link to this definition")

Write source code for a property-based test of `funcs`.

The resulting test checks that if you call the first function, pass the result to the second (and so on), the final result is equal to the first input argument.

This is a _very_ powerful property to test, especially when the config options are varied along with the object to round-trip. For example, try ghostwriting a test for [`json.dumps()`](https://docs.python.org/3/library/json.html#json.dumps "(in Python v3.14)") - would you have thought of all that?

hypothesis write \--roundtrip json.dumps json.loads

hypothesis.extra.ghostwriter.equivalent(

_\*funcs_,

_allow\_same\_errors\=False_,

_except\_\=()_,

_style\='pytest'_,

_annotate\=None_,

)[¶](#hypothesis.extra.ghostwriter.equivalent "Link to this definition")

Write source code for a property-based test of `funcs`.

The resulting test checks that calling each of the functions returns an equal value. This can be used as a classic ‘oracle’, such as testing a fast sorting algorithm against the [`sorted()`](https://docs.python.org/3/library/functions.html#sorted "(in Python v3.14)") builtin, or for differential testing where none of the compared functions are fully trusted but any difference indicates a bug (e.g. running a function on different numbers of threads, or simply multiple times).

The functions should have reasonably similar signatures, as only the common parameters will be passed the same arguments - any other parameters will be allowed to vary.

If allow\_same\_errors is True, then the test will pass if calling each of the functions returns an equal value, _or_ if the first function raises an exception and each of the others raises an exception of the same type. This relaxed mode can be useful for code synthesis projects.

hypothesis.extra.ghostwriter.binary\_operation(

_func_,

_\*_,

_associative\=True_,

_commutative\=True_,

_identity\=Ellipsis_,

_distributes\_over\=None_,

_except\_\=()_,

_style\='pytest'_,

_annotate\=None_,

)[¶](#hypothesis.extra.ghostwriter.binary_operation "Link to this definition")

Write property tests for the binary operation `func`.

While [binary operations](https://en.wikipedia.org/wiki/Binary_operation) are not particularly common, they have such nice properties to test that it seems a shame not to demonstrate them with a ghostwriter. For an operator `f`, test that:

*   if [associative](https://en.wikipedia.org/wiki/Associative_property), `f(a, f(b, c)) == f(f(a, b), c)`
    
*   if [commutative](https://en.wikipedia.org/wiki/Commutative_property), `f(a, b) == f(b, a)`
    
*   if [identity](https://en.wikipedia.org/wiki/Identity_element) is not None, `f(a, identity) == a`
    
*   if [distributes\_over](https://en.wikipedia.org/wiki/Distributive_property) is `+`, `f(a, b) + f(a, c) == f(a, b+c)`
    

For example:

ghostwriter.binary\_operation(
    operator.mul,
    identity\=1,
    distributes\_over\=operator.add,
    style\="unittest",
)

hypothesis.extra.ghostwriter.ufunc(_func_, _\*_, _except\_\=()_, _style\='pytest'_, _annotate\=None_)[¶](#hypothesis.extra.ghostwriter.ufunc "Link to this definition")

Write a property-based test for the [array ufunc](https://numpy.org/doc/stable/reference/ufuncs.html "(in NumPy v2.3)") `func`.

The resulting test checks that your ufunc or [gufunc](https://numpy.org/doc/stable/reference/c-api/generalized-ufuncs.html "(in NumPy v2.3)") has the expected broadcasting and dtype casting behaviour. You will probably want to add extra assertions, but as with the other ghostwriters this gives you a great place to start.

hypothesis write numpy.matmul

###### A note for test-generation researchers[¶](#a-note-for-test-generation-researchers "Link to this heading")

Ghostwritten tests are intended as a _starting point for human authorship_, to demonstrate best practice, help novices past blank-page paralysis, and save time for experts. They _may_ be ready-to-run, or include placeholders and `# TODO:` comments to fill in strategies for unknown types. In either case, improving tests for their own code gives users a well-scoped and immediately rewarding context in which to explore property-based testing.

By contrast, most test-generation tools aim to produce ready-to-run test suites… and implicitly assume that the current behavior is the desired behavior. However, the code might contain bugs, and we want our tests to fail if it does! Worse, tools require that the code to be tested is finished and executable, making it impossible to generate tests as part of the development process.

[Fraser 2013](https://doi.org/10.1145/2483760.2483774) found that evolving a high-coverage test suite (e.g. [Randoop](https://homes.cs.washington.edu/~mernst/pubs/feedback-testgen-icse2007.pdf), [EvoSuite](https://www.evosuite.org/wp-content/papercite-data/pdf/esecfse11.pdf), [Pynguin](https://arxiv.org/abs/2007.14049)) “leads to clear improvements in commonly applied quality metrics such as code coverage \[but\] no measurable improvement in the number of bugs actually found by developers” and that “generating a set of test cases, even high coverage test cases, does not necessarily improve our ability to test software”. Invariant detection (famously [Daikon](https://plse.cs.washington.edu/daikon/pubs/); in PBT see e.g. [Alonso 2022](https://doi.org/10.1145/3540250.3559080), [QuickSpec](http://www.cse.chalmers.se/~nicsma/papers/quickspec2.pdf), [Speculate](https://matela.com.br/speculate.pdf)) relies on code execution. Program slicing (e.g. [FUDGE](https://research.google/pubs/pub48314/), [FuzzGen](https://www.usenix.org/conference/usenixsecurity20/presentation/ispoglou), [WINNIE](https://www.ndss-symposium.org/wp-content/uploads/2021-334-paper.pdf)) requires downstream consumers of the code to test.

Ghostwriter inspects the function name, argument names and types, and docstrings. It can be used on buggy or incomplete code, runs in a few seconds, and produces a single semantically-meaningful test per function or group of functions. Rather than detecting regressions, these tests check semantic properties such as [encode/decode or save/load round-trips](https://zhd.dev/ghostwriter/?q=gzip.compress), for [commutative, associative, and distributive operations](https://zhd.dev/ghostwriter/?q=operator.mul), [equivalence between methods](https://zhd.dev/ghostwriter/?q=operator.add+numpy.add), [array shapes](https://zhd.dev/ghostwriter/?q=numpy.matmul), and idempotence. Where no property is detected, we simply check for ‘no error on valid input’ and allow the user to supply their own invariants.

Evaluations such as the [SBFT24](https://arxiv.org/abs/2401.15189) [competition](https://github.com/ThunderKey/python-tool-competition-2024) measure performance on a task which the Ghostwriter is not intended to perform. I’d love to see qualitative user studies, such as [PBT in Practice](https://harrisongoldste.in/papers/icse24-pbt-in-practice.pdf) for test generation, which could check whether the Ghostwriter is onto something or tilting at windmills. If you’re interested in similar questions, [drop me an email](mailto:zac%40zhd.dev?subject=Hypothesis%20Ghostwriter%20research)!

##### Observability[¶](#observability "Link to this heading")

Note

The [Tyche](https://github.com/tyche-pbt/tyche-extension) VSCode extension provides an in-editor UI for observability results generated by Hypothesis. If you want to _view_ observability results, rather than programmatically consume or display them, we recommend using Tyche.

Warning

This feature is experimental, and could have breaking changes or even be removed without notice. Try it out, let us know what you think, but don’t rely on it just yet!

###### Motivation[¶](#motivation "Link to this heading")

Understanding what your code is doing - for example, why your test failed - is often a frustrating exercise in adding some more instrumentation or logging (or `print()` calls) and running it again. The idea of [observability](https://en.wikipedia.org/wiki/Observability_(software)) is to let you answer questions you didn’t think of in advance. In slogan form,

> _Debugging should be a data analysis problem._

By default, Hypothesis only reports the minimal failing example… but sometimes you might want to know something about _all_ the examples. Printing them to the terminal by increasing [`Verbosity`](#hypothesis.Verbosity "hypothesis.Verbosity") might be nice, but isn’t always enough. This feature gives you an analysis-ready dataframe with useful columns and one row per test case, with columns from arguments to code coverage to pass/fail status.

This is deliberately a much lighter-weight and task-specific system than e.g. [OpenTelemetry](https://opentelemetry.io/). It’s also less detailed than time-travel debuggers such as [rr](https://rr-project.org/) or [pytrace](https://pytrace.com/), because there’s no good way to compare multiple traces from these tools and their Python support is relatively immature.

###### Configuration[¶](#configuration "Link to this heading")

If you set the `HYPOTHESIS_EXPERIMENTAL_OBSERVABILITY` environment variable, Hypothesis will log various observations to jsonlines files in the `.hypothesis/observed/` directory. You can load and explore these with e.g. [`pd.read_json(".hypothesis/observed/*_testcases.jsonl", lines=True)`](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.read_json.html#pandas.read_json "(in pandas v2.3.3)"), or by using the [sqlite-utils](https://pypi.org/project/sqlite-utils/) and [datasette](https://pypi.org/project/datasette/) libraries:

sqlite\-utils insert testcases.db testcases .hypothesis/observed/\*\_testcases.jsonl \--nl \--flatten
datasette serve testcases.db

If you are experiencing a significant slow-down, you can try setting `HYPOTHESIS_EXPERIMENTAL_OBSERVABILITY_NOCOVER` instead; this will disable coverage information collection. This should not be necessary on Python 3.12 or later, where coverage collection is very fast.

###### Collecting more information[¶](#collecting-more-information "Link to this heading")

If you want to record more information about your test cases than the arguments and outcome - for example, was `x` a binary tree? what was the difference between the expected and the actual value? how many queries did it take to find a solution? - Hypothesis makes this easy.

[`event()`](#hypothesis.event "hypothesis.event") accepts a string label, and optionally a string or int or float observation associated with it. All events are collected and summarized in [Test statistics](#statistics), as well as included on a per-test-case basis in our observations.

[`target()`](#hypothesis.target "hypothesis.target") is a special case of numeric-valued events: as well as recording them in observations, Hypothesis will try to maximize the targeted value. Knowing that, you can use this to guide the search for failing inputs.

###### Data Format[¶](#data-format "Link to this heading")

We dump observations in [json lines format](https://jsonlines.org/), with each line describing either a test case or an information message. The tables below are derived from [`this machine-readable JSON schema`](_downloads/6048e508a4f653f6c7e188c63a85e0e4/schema_observations.json), to provide both readable and verifiable specifications.

Note that we use [`json.dumps()`](https://docs.python.org/3/library/json.html#json.dumps "(in Python v3.14)") and can therefore emit non-standard JSON which includes infinities and NaN. This is valid in [JSON5](https://json5.org/), and supported by [some JSON parsers](https://evanhahn.com/pythons-nonstandard-json-encoding/) including Gson in Java, `JSON.parse()` in Ruby, and of course in Python.

###### Information message[¶](#information-message "Link to this heading")

Info, alert, and error messages correspond to a group of test cases or the overall run, and are intended for humans rather than machine analysis.

properties

*   **type**
    

A tag which labels this observation as general information to show the user. Hypothesis uses info messages to report statistics; alert or error messages can be provided by plugins.

enum

info, alert, error

*   **title**
    

The title of this message

type

_string_

*   **content**
    

The body of the message. Strings are presumed to be human-readable messages in markdown format; dictionaries may contain arbitrary information (as for test-case metadata).

type

_string_ / _object_

*   **property**
    

The name or representation of the test function we’re running. For Hypothesis, usually the Pytest nodeid.

type

_string_

*   **run\_start**
    

unix timestamp at which we started running this test function, so that later analysis can group test cases by run.

type

_number_

###### Test case[¶](#test-case "Link to this heading")

Describes the inputs to and result of running some test function on a particular input. The test might have passed, failed, or been abandoned part way through (e.g. because we failed a [`.filter()`](#hypothesis.strategies.SearchStrategy.filter "hypothesis.strategies.SearchStrategy.filter") condition).

properties

*   **type**
    

A tag which labels this observation as data about a specific test case.

const

test\_case

*   **status**
    

Whether the test passed, failed, or was aborted before completion (e.g. due to use of [`.filter()`](#hypothesis.strategies.SearchStrategy.filter "hypothesis.strategies.SearchStrategy.filter")). Note that if we gave\_up partway, values such as arguments and features may be incomplete.

enum

passed, failed, gave\_up

*   **status\_reason**
    

If non-empty, the reason for which the test failed or was abandoned. For Hypothesis, this is usually the exception type and location.

type

_string_

*   **representation**
    

The string representation of the input. In Hypothesis, this includes the property name and arguments (like `test_a(a=1)`), any interactive draws from [`data()`](#hypothesis.strategies.data "hypothesis.strategies.data"), and additionally some comments from [`Phase.explain`](#hypothesis.Phase.explain "hypothesis.Phase.explain") for failing examples.

type

_string_

*   **arguments**
    

A structured json-encoded representation of the input. Hypothesis provides a dictionary of argument names to json-ified values, including interactive draws from the [`data()`](#hypothesis.strategies.data "hypothesis.strategies.data") strategy. If ‘status’ is ‘gave\_up’, this may be absent or incomplete. In other libraries this can be any object.

type

_object_

*   **how\_generated**
    

How the input was generated, if known. In Hypothesis this might be an explicit example, generated during a particular phase with some backend, or by replaying the minimal failing example.

type

_string_ / _null_

*   **features**
    

Runtime observations which might help explain what this test case did. Hypothesis includes [`target()`](#hypothesis.target "hypothesis.target") scores, tags from [`event()`](#hypothesis.event "hypothesis.event"), and so on.

type

_object_

*   **coverage**
    

Mapping of filename to list of covered line numbers, if coverage information is available, or None if not. Hypothesis deliberately omits stdlib and site-packages code.

type

_object_ / _null_

additionalProperties

type

_array_

items

type

_integer_

minimum

1

uniqueItems

True

*   **timing**
    

The time in seconds taken by non-overlapping parts of this test case. Hypothesis reports `execute:test`, `overall:gc`, and `generate:{argname}` for each argument.

type

_object_

additionalProperties

type

_number_

minimum

0

*   **metadata**
    

Arbitrary metadata which might be of interest, but does not semantically fit in ‘features’. For example, Hypothesis includes the traceback for failing tests here.

type

_object_

*   **property**
    

The name or representation of the test function we’re running.

type

_string_

*   **run\_start**
    

unix timestamp at which we started running this test function, so that later analysis can group test cases by run.

type

_number_

###### Hypothesis metadata[¶](#hypothesis-metadata "Link to this heading")

While the observability format is agnostic to the property-based testing library which generated it, Hypothesis includes specific values in the `metadata` key for test cases. You may rely on these being present if and only if the observation was generated by Hypothesis.

properties

*   **traceback**
    

The traceback for failing tests, if and only if `status == "failed"`.

type

_string_ / _null_

*   **reproduction\_decorator**
    

The `@reproduce_failure` decorator string for failing tests, if and only if `status == "failed"`.

type

_string_ / _null_

*   **predicates**
    

The number of times each [`assume()`](#hypothesis.assume "hypothesis.assume") and [`@precondition`](#hypothesis.stateful.precondition "hypothesis.stateful.precondition") predicate was satisfied (`True`) and not satisfied (`False`).

type

_object_

additionalProperties

type

_object_

properties

*   **satisfied**
    

The number of times this predicate was satisfied (`True`).

type

_integer_

minimum

0

*   **unsatisfied**
    

The number of times this predicate was not satisfied (`False`).

type

_integer_

minimum

0

additionalProperties

False

*   **backend**
    

Backend-specific observations from [`observe_test_case()`](#hypothesis.internal.conjecture.providers.PrimitiveProvider.observe_test_case "hypothesis.internal.conjecture.providers.PrimitiveProvider.observe_test_case") and [`observe_information_messages()`](#hypothesis.internal.conjecture.providers.PrimitiveProvider.observe_information_messages "hypothesis.internal.conjecture.providers.PrimitiveProvider.observe_information_messages").

type

_object_

*   **sys.argv**
    

The result of `sys.argv`.

type

_array_

items

type

_string_

*   **os.getpid()**
    

The result of `os.getpid()`.

type

_integer_

*   **imported\_at**
    

The unix timestamp when Hypothesis was imported.

type

_number_

*   phase
    

The Hypothesis [`Phase`](#hypothesis.Phase "hypothesis.Phase") this test case was generated in.

type

_string_

*   **data\_status**
    

The internal status of the ConjectureData for this test case. The values are as follows: `Status.OVERRUN = 0`, `Status.INVALID = 1`, `Status.VALID = 2`, and `Status.INTERESTING = 3`.

type

_number_

enum

0, 1, 2, 3

*   **interesting\_origin**
    

The internal `InterestingOrigin` object for failing tests, if and only if `status == "failed"`. The `traceback` string value is derived from this object.

type

_string_ / _null_

###### Choices metadata[¶](#choices-metadata "Link to this heading")

These additional metadata elements are included in `metadata` (as e.g. `metadata["choice_nodes"]` or `metadata["choice_spans"]`), if and only if [`OBSERVABILITY_CHOICES`](#hypothesis.internal.observability.OBSERVABILITY_CHOICES "hypothesis.internal.observability.OBSERVABILITY_CHOICES") is set.

properties

*   **choice\_nodes**
    

Warning

EXPERIMENTAL AND UNSTABLE. This attribute may change format or disappear without warning.

The sequence of choices made during this test case. This includes the choice value, as well as its constraints and whether it was forced or not.

Only present if [`OBSERVABILITY_CHOICES`](#hypothesis.internal.observability.OBSERVABILITY_CHOICES "hypothesis.internal.observability.OBSERVABILITY_CHOICES") is `True`.

Note

The choice sequence is a relatively low-level implementation detail of Hypothesis, and is exposed in observability for users building tools or research on top of Hypothesis. See [`PrimitiveProvider`](#hypothesis.internal.conjecture.providers.PrimitiveProvider "hypothesis.internal.conjecture.providers.PrimitiveProvider") for more details about the choice sequence.

type

_array_ / _null_

items

type

_object_

properties

*   **type**
    

The type of choice made. Corresponds to a call to [`draw_integer()`](#hypothesis.internal.conjecture.providers.PrimitiveProvider.draw_integer "hypothesis.internal.conjecture.providers.PrimitiveProvider.draw_integer"), [`draw_float()`](#hypothesis.internal.conjecture.providers.PrimitiveProvider.draw_float "hypothesis.internal.conjecture.providers.PrimitiveProvider.draw_float"), [`draw_string()`](#hypothesis.internal.conjecture.providers.PrimitiveProvider.draw_string "hypothesis.internal.conjecture.providers.PrimitiveProvider.draw_string"), [`draw_bytes()`](#hypothesis.internal.conjecture.providers.PrimitiveProvider.draw_bytes "hypothesis.internal.conjecture.providers.PrimitiveProvider.draw_bytes"), or [`draw_boolean()`](#hypothesis.internal.conjecture.providers.PrimitiveProvider.draw_boolean "hypothesis.internal.conjecture.providers.PrimitiveProvider.draw_boolean").

type

_string_

enum

integer, float, string, bytes, boolean

*   **value**
    

The value of the choice. Corresponds to the value returned by a `PrimitiveProvider.draw_*` method.

`NaN` float values are returned as `["float", <float64_int_value>]`, to distinguish `NaN` floats with nonstandard bit patterns. Integers with `abs(value) >= 2**63` are returned as `["integer", str(value)]`, for compatibility with tools with integer size limitations. Bytes are returned as `["bytes", base64.b64encode(value)]`.

*   **constraints**
    

The constraints for this choice. Corresponds to the constraints passed to a `PrimitiveProvider.draw_*` method. `NaN` float values, integers with `abs(value) >= 2**63`, and byte values for constraints are transformed as for the `value` attribute.

type

_object_

*   **was\_forced**
    

Whether this choice was forced. As an implementation detail, Hypothesis occasionally requires that some choices take on a specific value, for instance to end generation of collection elements early for performance. These values are called “forced”, and have `was_forced = True`.

type

_boolean_

additionalProperties

False

*   **choice\_spans**
    

Warning

EXPERIMENTAL AND UNSTABLE. This attribute may change format or disappear without warning.

The semantically-meaningful spans of the choice sequence of this test case.

Each span has the format `[label, start, end, discarded]`, where:

*   `label` is an opaque integer-value string shared by all spans drawn from a particular strategy.
    
*   `start` and `end` are indices into the choice sequence for this span, such that `choices[start:end]` are the corresponding choices.
    
*   `discarded` is a boolean indicating whether this span was discarded (see [`span_end()`](#hypothesis.internal.conjecture.providers.PrimitiveProvider.span_end "hypothesis.internal.conjecture.providers.PrimitiveProvider.span_end")).
    

Only present if [`OBSERVABILITY_CHOICES`](#hypothesis.internal.observability.OBSERVABILITY_CHOICES "hypothesis.internal.observability.OBSERVABILITY_CHOICES") is `True`.

Note

Spans are a relatively low-level implementation detail of Hypothesis, and are exposed in observability for users building tools or research on top of Hypothesis. See [`PrimitiveProvider`](#hypothesis.internal.conjecture.providers.PrimitiveProvider "hypothesis.internal.conjecture.providers.PrimitiveProvider") (and particularly [`span_start()`](#hypothesis.internal.conjecture.providers.PrimitiveProvider.span_start "hypothesis.internal.conjecture.providers.PrimitiveProvider.span_start") and [`span_end()`](#hypothesis.internal.conjecture.providers.PrimitiveProvider.span_end "hypothesis.internal.conjecture.providers.PrimitiveProvider.span_end")) for more details about spans.

type

_array_

items

type

_array_

##### The Hypothesis pytest plugin[¶](#the-hypothesis-pytest-plugin "Link to this heading")

Hypothesis includes a tiny plugin to improve integration with [pytest](https://pypi.org/project/pytest/), which is activated by default (but does not affect other test runners). It aims to improve the integration between Hypothesis and Pytest by providing extra information and convenient access to config options.

*   `pytest --hypothesis-show-statistics` can be used to [display test and data generation statistics](#statistics).
    
*   `pytest --hypothesis-profile=<profile name>` can be used to load a settings profile (as in [`load_profile()`](#hypothesis.settings.load_profile "hypothesis.settings.load_profile")).
    
*   `pytest --hypothesis-verbosity=<level name>` can be used to override the current [`Verbosity`](#hypothesis.Verbosity "hypothesis.Verbosity") setting.
    
*   `pytest --hypothesis-seed=<an int>` can be used to reproduce a failure with a particular seed (as in [`@seed`](#hypothesis.seed "hypothesis.seed")).
    
*   `pytest --hypothesis-explain` can be used to temporarily enable [`Phase.explain`](#hypothesis.Phase.explain "hypothesis.Phase.explain").
    

Finally, all tests that are defined with Hypothesis automatically have `@pytest.mark.hypothesis` applied to them. See [here for information on working with markers](https://docs.pytest.org/en/stable/example/markers.html#mark-examples "(in pytest v9.0.1)").

Note

Pytest will load the plugin automatically if Hypothesis is installed. You don’t need to do anything at all to use it.

If this causes problems, you can avoid loading the plugin with the `-p no:hypothesispytest` option.

###### Test statistics[¶](#test-statistics "Link to this heading")

Note

While test statistics are only available under pytest, you can use the [observability](#observability) interface to view similar information about your tests.

You can see a number of statistics about executed tests by passing the command line argument `--hypothesis-show-statistics`. This will include some general statistics about the test:

For example if you ran the following with `--hypothesis-show-statistics`:

from hypothesis import given, strategies as st

@given(st.integers())
def test\_integers(i):
    pass

You would see:

\- during generate phase (0.06 seconds):
    - Typical runtimes: < 1ms, ~ 47% in data generation
    - 100 passing examples, 0 failing examples, 0 invalid examples
- Stopped because settings.max\_examples=100

The final “Stopped because” line tells you why Hypothesis stopped generating new examples. This is typically because we hit [`max_examples`](#hypothesis.settings.max_examples "hypothesis.settings.max_examples"), but occasionally because we exhausted the search space or because shrinking was taking a very long time. This can be useful for understanding the behaviour of your tests.

In some cases (such as filtered and recursive strategies) you will see events mentioned which describe some aspect of the data generation:

from hypothesis import given, strategies as st

@given(st.integers().filter(lambda x: x % 2 \== 0))
def test\_even\_integers(i):
    pass

You would see something like:

test\_even\_integers:

  - during generate phase (0.08 seconds):
      - Typical runtimes: < 1ms, ~ 57% in data generation
      - 100 passing examples, 0 failing examples, 12 invalid examples
      - Events:
        \* 51.79%, Retried draw from integers().filter(lambda x: x % 2 == 0) to satisfy filter
        \* 10.71%, Aborted test because unable to satisfy integers().filter(lambda x: x % 2 == 0)
  - Stopped because settings.max\_examples=100

##### hypothesis\[cli\][¶](#hypothesis-cli "Link to this heading")

Note

This feature requires the `hypothesis[cli]` [extra](#document-extras), via `pip install hypothesis[cli]`.

$ hypothesis --help
Usage: hypothesis \[OPTIONS\] COMMAND \[ARGS\]...

Options:
  --version   Show the version and exit.
  -h, --help  Show this message and exit.

Commands:
  codemod  \`hypothesis codemod\` refactors deprecated or inefficient code.
  fuzz     \[hypofuzz\] runs tests with an adaptive coverage-guided fuzzer.
  write    \`hypothesis write\` writes property-based tests for you!

This module requires the [click](https://pypi.org/project/click/) package, and provides Hypothesis’ command-line interface, for e.g. [‘ghostwriting’ tests](#ghostwriter) via the terminal. It’s also where [HypoFuzz](https://hypofuzz.com/) adds the **hypothesis fuzz** command ([learn more about that here](https://hypofuzz.com/docs/quickstart.html)).

##### hypothesis\[codemods\][¶](#hypothesis-codemods "Link to this heading")

Note

This feature requires the `hypothesis[codemods]` [extra](#document-extras), via `pip install hypothesis[codemods]`.

This module provides codemods based on the [LibCST](https://pypi.org/project/LibCST/) library, which can both detect _and automatically fix_ issues with code that uses Hypothesis, including upgrading from deprecated features to our recommended style.

You can run the codemods via our CLI:

$ hypothesis codemod --help
Usage: hypothesis codemod \[OPTIONS\] PATH...

  \`hypothesis codemod\` refactors deprecated or inefficient code.

  It adapts \`python -m libcst.tool\`, removing many features and config
  options which are rarely relevant for this purpose.  If you need more
  control, we encourage you to use the libcst CLI directly; if not this one
  is easier.

  PATH is the file(s) or directories of files to format in place, or "-" to
  read from stdin and write to stdout.

Options:
  -h, --help  Show this message and exit.

Alternatively you can use `python -m libcst.tool`, which offers more control at the cost of additional configuration (adding `'hypothesis.extra'` to the `modules` list in `.libcst.codemod.yaml`) and [some issues on Windows](https://github.com/Instagram/LibCST/issues/435).

hypothesis.extra.codemods.refactor(_code_)[¶](#hypothesis.extra.codemods.refactor "Link to this definition")

Update a source code string from deprecated to modern Hypothesis APIs.

This may not fix _all_ the deprecation warnings in your code, but we’re confident that it will be easier than doing it all by hand.

We recommend using the CLI, but if you want a Python function here it is.

##### hypothesis\[dpcontracts\][¶](#hypothesis-dpcontracts "Link to this heading")

Note

This feature requires the `hypothesis[dpcontracts]` [extra](#document-extras), via `pip install hypothesis[dpcontracts]`.

Tip

For new projects, we recommend using either [deal](https://pypi.org/project/deal/) or [icontract](https://pypi.org/project/icontract/) and [icontract-hypothesis](https://pypi.org/project/icontract-hypothesis/) over [dpcontracts](https://pypi.org/project/dpcontracts/). They’re generally more powerful tools for design-by-contract programming, and have substantially nicer Hypothesis integration too!

This module provides tools for working with the [dpcontracts](https://pypi.org/project/dpcontracts/) library, because [combining contracts and property-based testing works really well](https://hillelwayne.com/talks/beyond-unit-tests/).

It requires `dpcontracts >= 0.4`.

hypothesis.extra.dpcontracts.fulfill(_contract\_func_)[¶](#hypothesis.extra.dpcontracts.fulfill "Link to this definition")

Decorate `contract_func` to reject calls which violate preconditions, and retry them with different arguments.

This is a convenience function for testing internal code that uses [dpcontracts](https://pypi.org/project/dpcontracts/), to automatically filter out arguments that would be rejected by the public interface before triggering a contract error.

This can be used as `builds(fulfill(func), ...)` or in the body of the test e.g. `assert fulfill(func)(*args)`.

#### Hypothesis internals[¶](#hypothesis-internals "Link to this heading")

Warning

This page documents internal Hypothesis interfaces. Some are fairly stable, while others are still experimental. In either case, they are not subject to our standard [deprecation policy](#deprecation-policy), and we might make breaking changes in minor or patch releases.

This page is intended for people building tools, libraries, or research on top of Hypothesis. If that includes you, please get in touch! We’d love to hear what you’re doing, or explore more stable ways to support your use-case.

##### Alternative backends[¶](#alternative-backends "Link to this heading")

See also

See also the user-facing [Alternative backends for Hypothesis](#alternative-backends) documentation.

_class_ hypothesis.internal.conjecture.providers.PrimitiveProvider(_conjecturedata_, _/_)[¶](#hypothesis.internal.conjecture.providers.PrimitiveProvider "Link to this definition")

[`PrimitiveProvider`](#hypothesis.internal.conjecture.providers.PrimitiveProvider "hypothesis.internal.conjecture.providers.PrimitiveProvider") is the implementation interface of a [Hypothesis backend](#alternative-backends).

A [`PrimitiveProvider`](#hypothesis.internal.conjecture.providers.PrimitiveProvider "hypothesis.internal.conjecture.providers.PrimitiveProvider") is required to implement the following five `draw_*` methods:

*   [`draw_integer()`](#hypothesis.internal.conjecture.providers.PrimitiveProvider.draw_integer "hypothesis.internal.conjecture.providers.PrimitiveProvider.draw_integer")
    
*   [`draw_boolean()`](#hypothesis.internal.conjecture.providers.PrimitiveProvider.draw_boolean "hypothesis.internal.conjecture.providers.PrimitiveProvider.draw_boolean")
    
*   [`draw_float()`](#hypothesis.internal.conjecture.providers.PrimitiveProvider.draw_float "hypothesis.internal.conjecture.providers.PrimitiveProvider.draw_float")
    
*   [`draw_string()`](#hypothesis.internal.conjecture.providers.PrimitiveProvider.draw_string "hypothesis.internal.conjecture.providers.PrimitiveProvider.draw_string")
    
*   [`draw_bytes()`](#hypothesis.internal.conjecture.providers.PrimitiveProvider.draw_bytes "hypothesis.internal.conjecture.providers.PrimitiveProvider.draw_bytes")
    

Each strategy in Hypothesis generates values by drawing a series of choices from these five methods. By overriding them, a [`PrimitiveProvider`](#hypothesis.internal.conjecture.providers.PrimitiveProvider "hypothesis.internal.conjecture.providers.PrimitiveProvider") can control the distribution of inputs generated by Hypothesis.

For example, [hypothesis-crosshair](https://pypi.org/project/hypothesis-crosshair/) implements a [`PrimitiveProvider`](#hypothesis.internal.conjecture.providers.PrimitiveProvider "hypothesis.internal.conjecture.providers.PrimitiveProvider") which uses an SMT solver to generate inputs that uncover new branches.

Once you implement a [`PrimitiveProvider`](#hypothesis.internal.conjecture.providers.PrimitiveProvider "hypothesis.internal.conjecture.providers.PrimitiveProvider"), you can make it available for use through [`AVAILABLE_PROVIDERS`](#hypothesis.internal.conjecture.providers.AVAILABLE_PROVIDERS "hypothesis.internal.conjecture.providers.AVAILABLE_PROVIDERS").

lifetime _\= 'test\_function'_[¶](#hypothesis.internal.conjecture.providers.PrimitiveProvider.lifetime "Link to this definition")

The lifetime of a [`PrimitiveProvider`](#hypothesis.internal.conjecture.providers.PrimitiveProvider "hypothesis.internal.conjecture.providers.PrimitiveProvider") instance. Either `test_function` or `test_case`.

If `test_function` (the default), a single provider instance will be instantiated and used for the entirety of each test function (i.e., roughly one provider per [`@given`](#hypothesis.given "hypothesis.given") annotation). This can be useful for tracking state over the entirety of a test function.

If `test_case`, a new provider instance will be instantiated and used for each input Hypothesis generates.

The `conjecturedata` argument to `PrimitiveProvider.__init__` will be `None` for a lifetime of `test_function`, and an instance of `ConjectureData` for a lifetime of `test_case`.

Third-party providers likely want to set a lifetime of `test_function`.

avoid\_realization _\= False_[¶](#hypothesis.internal.conjecture.providers.PrimitiveProvider.avoid_realization "Link to this definition")

Solver-based backends such as `hypothesis-crosshair` use symbolic values which record operations performed on them in order to discover new paths. If `avoid_realization` is set to `True`, hypothesis will avoid interacting with symbolic choices returned by the provider in any way that would force the solver to narrow the range of possible values for that symbolic.

Setting this to `True` disables some hypothesis features and optimizations. Only set this to `True` if it is necessary for your backend.

add\_observability\_callback _\= False_[¶](#hypothesis.internal.conjecture.providers.PrimitiveProvider.add_observability_callback "Link to this definition")

will never be called by Hypothesis.

The opt-in behavior of observability is because enabling observability might increase runtime or memory usage.

_abstract_ draw\_boolean(_p\=0.5_)[¶](#hypothesis.internal.conjecture.providers.PrimitiveProvider.draw_boolean "Link to this definition")

Draw a boolean choice.

Parameters:

**p** ([_float_](https://docs.python.org/3/library/functions.html#float "(in Python v3.14)")) –

The probability of returning `True`. Between 0 and 1 inclusive.

Except for `0` and `1`, the value of `p` is a hint provided by Hypothesis, and may be ignored by the backend.

If `0`, the provider must return `False`. If `1`, the provider must return `True`.

_abstract_ draw\_integer(

_min\_value\=None_,

_max\_value\=None_,

_\*_,

_weights\=None_,

_shrink\_towards\=0_,

)[¶](#hypothesis.internal.conjecture.providers.PrimitiveProvider.draw_integer "Link to this definition")

Draw an integer choice.

Parameters:

*   **min\_value** ([_int_](https://docs.python.org/3/library/functions.html#int "(in Python v3.14)") _|_ _None_) – (Inclusive) lower bound on the integer value. If `None`, there is no lower bound.
    
*   **max\_value** ([_int_](https://docs.python.org/3/library/functions.html#int "(in Python v3.14)") _|_ _None_) – (Inclusive) upper bound on the integer value. If `None`, there is no upper bound.
    
*   **weights** ([_dict_](https://docs.python.org/3/library/stdtypes.html#dict "(in Python v3.14)")_\[_[_int_](https://docs.python.org/3/library/functions.html#int "(in Python v3.14)")_,_ [_float_](https://docs.python.org/3/library/functions.html#float "(in Python v3.14)")_\]_ _|_ _None_) – Maps keys in the range \[`min_value`, `max_value`\] to the probability of returning that key.
    
*   **shrink\_towards** ([_int_](https://docs.python.org/3/library/functions.html#int "(in Python v3.14)")) – The integer to shrink towards. This is not used during generation and can be ignored by backends.
    

_abstract_ draw\_float(

_\*_,

_min\_value\=\-inf_,

_max\_value\=inf_,

_allow\_nan\=True_,

_smallest\_nonzero\_magnitude_,

)[¶](#hypothesis.internal.conjecture.providers.PrimitiveProvider.draw_float "Link to this definition")

Draw a float choice.

Parameters:

*   **min\_value** ([_float_](https://docs.python.org/3/library/functions.html#float "(in Python v3.14)")) – (Inclusive) lower bound on the float value.
    
*   **max\_value** ([_float_](https://docs.python.org/3/library/functions.html#float "(in Python v3.14)")) – (Inclusive) upper bound on the float value.
    
*   **allow\_nan** ([_bool_](https://docs.python.org/3/library/functions.html#bool "(in Python v3.14)")) – If `False`, it is invalid to return `math.nan`.
    
*   **smallest\_nonzero\_magnitude** ([_float_](https://docs.python.org/3/library/functions.html#float "(in Python v3.14)")) – The smallest allowed nonzero magnitude. `draw_float` should not return a float `f` if `abs(f) < smallest_nonzero_magnitude`.
    

_abstract_ draw\_string(

_intervals_,

_\*_,

_min\_size\=0_,

_max\_size\=10000000000_,

)[¶](#hypothesis.internal.conjecture.providers.PrimitiveProvider.draw_string "Link to this definition")

Draw a string choice.

Parameters:

*   **intervals** ([_IntervalSet_](#hypothesis.internal.intervalsets.IntervalSet "hypothesis.internal.intervalsets.IntervalSet")) – The set of codepoints to sample from.
    
*   **min\_size** ([_int_](https://docs.python.org/3/library/functions.html#int "(in Python v3.14)")) – (Inclusive) lower bound on the string length.
    
*   **max\_size** ([_int_](https://docs.python.org/3/library/functions.html#int "(in Python v3.14)")) – (Inclusive) upper bound on the string length.
    

_abstract_ draw\_bytes(

_min\_size\=0_,

_max\_size\=10000000000_,

)[¶](#hypothesis.internal.conjecture.providers.PrimitiveProvider.draw_bytes "Link to this definition")

Draw a bytes choice.

Parameters:

*   **min\_size** ([_int_](https://docs.python.org/3/library/functions.html#int "(in Python v3.14)")) – (Inclusive) lower bound on the bytes length.
    
*   **max\_size** ([_int_](https://docs.python.org/3/library/functions.html#int "(in Python v3.14)")) – (Inclusive) upper bound on the bytes length.
    

per\_test\_case\_context\_manager()[¶](#hypothesis.internal.conjecture.providers.PrimitiveProvider.per_test_case_context_manager "Link to this definition")

Returns a context manager which will be entered each time Hypothesis starts generating and executing one test case, and exited when that test case finishes generating and executing, including if any exception is thrown.

In the lifecycle of a Hypothesis test, this is called before generating strategy values for each test case. This is just before any [custom executor](#custom-function-execution) is called.

Even if not returning a custom context manager, [`PrimitiveProvider`](#hypothesis.internal.conjecture.providers.PrimitiveProvider "hypothesis.internal.conjecture.providers.PrimitiveProvider") subclasses are welcome to override this method to know when Hypothesis starts and ends the execution of a single test case.

realize(_value_, _\*_, _for\_failure\=False_)[¶](#hypothesis.internal.conjecture.providers.PrimitiveProvider.realize "Link to this definition")

Called whenever hypothesis requires a concrete (non-symbolic) value from a potentially symbolic value. Hypothesis will not check that `value` is symbolic before calling `realize`, so you should handle the case where `value` is non-symbolic.

The returned value should be non-symbolic. If you cannot provide a value, raise [`BackendCannotProceed`](#hypothesis.errors.BackendCannotProceed "hypothesis.errors.BackendCannotProceed") with a value of `"discard_test_case"`.

If `for_failure` is `True`, the value is associated with a failing example. In this case, the backend should spend substantially more effort when attempting to realize the value, since it is important to avoid discarding failing examples. Backends may still raise [`BackendCannotProceed`](#hypothesis.errors.BackendCannotProceed "hypothesis.errors.BackendCannotProceed") when `for_failure` is `True`, if realization is truly impossible or if realization takes significantly longer than expected (say, 5 minutes).

replay\_choices(_choices_)[¶](#hypothesis.internal.conjecture.providers.PrimitiveProvider.replay_choices "Link to this definition")

Called when Hypothesis has discovered a choice sequence which the provider may wish to enqueue to replay under its own instrumentation when we next ask to generate a test case, rather than generating one from scratch.

This is used to e.g. warm-start [hypothesis-crosshair](https://pypi.org/project/hypothesis-crosshair/) with a corpus of high-code-coverage inputs discovered by [HypoFuzz](https://hypofuzz.com/).

observe\_test\_case()[¶](#hypothesis.internal.conjecture.providers.PrimitiveProvider.observe_test_case "Link to this definition")

Called at the end of the test case when [observability](#observability) is enabled.

The return value should be a non-symbolic json-encodable dictionary, and will be included in observations as `observation["metadata"]["backend"]`.

observe\_information\_messages(_\*_, _lifetime_)[¶](#hypothesis.internal.conjecture.providers.PrimitiveProvider.observe_information_messages "Link to this definition")

Called at the end of each test case and again at end of the test function.

Return an iterable of `{type: info/alert/error, title: str, content: str | dict}` dictionaries to be delivered as individual information messages. Hypothesis adds the `run_start` timestamp and `property` name for you.

on\_observation(_observation_)[¶](#hypothesis.internal.conjecture.providers.PrimitiveProvider.on_observation "Link to this definition")

Called at the end of each test case which uses this provider, with the same `observation["type"] == "test_case"` observation that is passed to other callbacks added via [`add_observability_callback`](#hypothesis.internal.observability.add_observability_callback "hypothesis.internal.observability.add_observability_callback"). This method is not called with `observation["type"] in {"info", "alert", "error"}` observations.

Important

For [`on_observation()`](#hypothesis.internal.conjecture.providers.PrimitiveProvider.on_observation "hypothesis.internal.conjecture.providers.PrimitiveProvider.on_observation") to be called by Hypothesis, [`add_observability_callback`](#hypothesis.internal.conjecture.providers.PrimitiveProvider.add_observability_callback "hypothesis.internal.conjecture.providers.PrimitiveProvider.add_observability_callback") must be set to `True`.

[`on_observation()`](#hypothesis.internal.conjecture.providers.PrimitiveProvider.on_observation "hypothesis.internal.conjecture.providers.PrimitiveProvider.on_observation") is explicitly opt-in, as enabling observability might increase runtime or memory usage.

Calls to this method are guaranteed to alternate with calls to [`per_test_case_context_manager()`](#hypothesis.internal.conjecture.providers.PrimitiveProvider.per_test_case_context_manager "hypothesis.internal.conjecture.providers.PrimitiveProvider.per_test_case_context_manager"). For example:

\# test function starts
per\_test\_case\_context\_manager()
on\_observation()
per\_test\_case\_context\_manager()
on\_observation()
...
\# test function ends

Note that [`on_observation()`](#hypothesis.internal.conjecture.providers.PrimitiveProvider.on_observation "hypothesis.internal.conjecture.providers.PrimitiveProvider.on_observation") will not be called for test cases which did not use this provider during generation, for example during [`Phase.reuse`](#hypothesis.Phase.reuse "hypothesis.Phase.reuse") or [`Phase.shrink`](#hypothesis.Phase.shrink "hypothesis.Phase.shrink"), or because Hypothesis switched to the standard Hypothesis backend after this backend raised too many [`BackendCannotProceed`](#hypothesis.errors.BackendCannotProceed "hypothesis.errors.BackendCannotProceed") exceptions.

span\_start(_label_, _/_)[¶](#hypothesis.internal.conjecture.providers.PrimitiveProvider.span_start "Link to this definition")

Marks the beginning of a semantically meaningful span of choices.

Spans are a depth-first tree structure. A span is opened by a call to [`span_start()`](#hypothesis.internal.conjecture.providers.PrimitiveProvider.span_start "hypothesis.internal.conjecture.providers.PrimitiveProvider.span_start"), and a call to [`span_end()`](#hypothesis.internal.conjecture.providers.PrimitiveProvider.span_end "hypothesis.internal.conjecture.providers.PrimitiveProvider.span_end") closes the most recently opened span. So the following sequence of calls:

span\_start(label\=1)
n1 \= draw\_integer()
span\_start(label\=2)
b1 \= draw\_boolean()
n2 \= draw\_integer()
span\_end()
f1 \= draw\_float()
span\_end()

produces the following two spans of choices:

1: \[n1, b1, n2, f1\]
2: \[b1, n2\]

Hypothesis uses spans to denote “semantically meaningful” sequences of choices. For instance, Hypothesis opens a span for the sequence of choices made while drawing from each strategy. Not every span corresponds to a strategy; the generation of e.g. each element in [`lists()`](#hypothesis.strategies.lists "hypothesis.strategies.lists") is also marked with a span, among others.

`label` is an opaque integer, which has no defined semantics. The only guarantee made by Hypothesis is that all spans with the same “meaning” will share the same `label`. So all spans from the same strategy will share the same label, as will e.g. the spans for [`lists()`](#hypothesis.strategies.lists "hypothesis.strategies.lists") elements.

Providers can track calls to [`span_start()`](#hypothesis.internal.conjecture.providers.PrimitiveProvider.span_start "hypothesis.internal.conjecture.providers.PrimitiveProvider.span_start") and [`span_end()`](#hypothesis.internal.conjecture.providers.PrimitiveProvider.span_end "hypothesis.internal.conjecture.providers.PrimitiveProvider.span_end") to learn something about the semantics of the test’s choice sequence. For instance, a provider could track the depth of the span tree, or the number of unique labels, which says something about the complexity of the choices being generated. Or a provider could track the span tree across test cases in order to determine what strategies are being used in what contexts.

It is possible for Hypothesis to start and immediately stop a span, without calling a `draw_*` method in between. These spans contain zero choices.

Hypothesis will always balance the number of calls to [`span_start()`](#hypothesis.internal.conjecture.providers.PrimitiveProvider.span_start "hypothesis.internal.conjecture.providers.PrimitiveProvider.span_start") and [`span_end()`](#hypothesis.internal.conjecture.providers.PrimitiveProvider.span_end "hypothesis.internal.conjecture.providers.PrimitiveProvider.span_end"). A call to [`span_start()`](#hypothesis.internal.conjecture.providers.PrimitiveProvider.span_start "hypothesis.internal.conjecture.providers.PrimitiveProvider.span_start") will always be followed by a call to [`span_end()`](#hypothesis.internal.conjecture.providers.PrimitiveProvider.span_end "hypothesis.internal.conjecture.providers.PrimitiveProvider.span_end") before the end of the test case.

[`span_start()`](#hypothesis.internal.conjecture.providers.PrimitiveProvider.span_start "hypothesis.internal.conjecture.providers.PrimitiveProvider.span_start") is called from `ConjectureData.start_span()` internally.

span\_end(_discard_, _/_)[¶](#hypothesis.internal.conjecture.providers.PrimitiveProvider.span_end "Link to this definition")

Marks the end of a semantically meaningful span of choices.

`discard` is `True` when the draw was filtered out or otherwise marked as unlikely to contribute to the input data as seen by the user’s test. Note however that side effects can make this determination unsound.

[`span_end()`](#hypothesis.internal.conjecture.providers.PrimitiveProvider.span_end "hypothesis.internal.conjecture.providers.PrimitiveProvider.span_end") is called from `ConjectureData.stop_span()` internally.

hypothesis.internal.conjecture.providers.AVAILABLE\_PROVIDERS[¶](#hypothesis.internal.conjecture.providers.AVAILABLE_PROVIDERS "Link to this definition")

Registered Hypothesis backends. This is a dictionary where keys are the name to be used in [`settings.backend`](#hypothesis.settings.backend "hypothesis.settings.backend"). The value of a key can be either:

*   A string corresponding to an importable absolute path of a [`PrimitiveProvider`](#hypothesis.internal.conjecture.providers.PrimitiveProvider "hypothesis.internal.conjecture.providers.PrimitiveProvider") subclass
    
*   A [`PrimitiveProvider`](#hypothesis.internal.conjecture.providers.PrimitiveProvider "hypothesis.internal.conjecture.providers.PrimitiveProvider") subclass (the class itself, not an instance of the class)
    

Hypothesis will instantiate the corresponding [`PrimitiveProvider`](#hypothesis.internal.conjecture.providers.PrimitiveProvider "hypothesis.internal.conjecture.providers.PrimitiveProvider") subclass when the backend is requested by a test’s [`settings.backend`](#hypothesis.settings.backend "hypothesis.settings.backend") value.

For example, the default Hypothesis backend is registered as:

from hypothesis.internal.conjecture.providers import AVAILABLE\_PROVIDERS

AVAILABLE\_PROVIDERS\["hypothesis"\] \= "hypothesis.internal.conjecture.providers.HypothesisProvider"
\# or
AVAILABLE\_PROVIDERS\["hypothesis"\] \= HypothesisProvider

And can be used with:

from hypothesis import given, settings, strategies as st

@given(st.integers())
@settings(backend\="hypothesis")
def f(n):
    pass

Though, as `backend="hypothesis"` is the default setting, the above would typically not have any effect.

For third-party backend authors, we strongly encourage ensuring that `import hypothesis` does not automatically import the expensive parts of your package, by:

*   setting a string path here, instead of a provider class
    
*   ensuring the registered hypothesis plugin path references a path which just sets AVAILABLE\_PROVIDERS and does not import your package
    

hypothesis.internal.conjecture.provider\_conformance.run\_conformance\_test(

_Provider_,

_\*_,

_context\_manager\_exceptions\=()_,

_settings\=None_,

_\_realize\_objects\=st.from\_type(object) | st.from\_type(type).flatmap(st.from\_type)_,

)[¶](#hypothesis.internal.conjecture.provider_conformance.run_conformance_test "Link to this definition")

Test that the given `Provider` class conforms to the [`PrimitiveProvider`](#hypothesis.internal.conjecture.providers.PrimitiveProvider "hypothesis.internal.conjecture.providers.PrimitiveProvider") interface.

For instance, this tests that `Provider` does not return out of bounds choices from any of the `draw_*` methods, or violate other invariants which Hypothesis depends on.

This function is intended to be called at test-time, not at runtime. It is provided by Hypothesis to make it easy for third-party backend authors to test their provider. Backend authors wishing to test their provider should include a test similar to the following in their test suite:

from hypothesis.internal.conjecture.provider\_conformance import run\_conformance\_test

def test\_conformance():
    run\_conformance\_test(MyProvider)

If your provider can raise control flow exceptions inside one of the five `draw_*` methods that are handled by your provider’s `per_test_case_context_manager`, pass a list of these exceptions types to `context_manager_exceptions`. Otherwise, `run_conformance_test` will treat those exceptions as fatal errors.

_class_ hypothesis.errors.BackendCannotProceed(_scope\='other'_, _/_)[¶](#hypothesis.errors.BackendCannotProceed "Link to this definition")

Raised by alternative backends when a [`PrimitiveProvider`](#hypothesis.internal.conjecture.providers.PrimitiveProvider "hypothesis.internal.conjecture.providers.PrimitiveProvider") cannot proceed. This is expected to occur inside one of the `.draw_*()` methods, or for symbolic execution perhaps in [`realize()`](#hypothesis.internal.conjecture.providers.PrimitiveProvider.realize "hypothesis.internal.conjecture.providers.PrimitiveProvider.realize").

The optional `scope` argument can enable smarter integration:

> verified:
> 
> Do not request further test cases from this backend. We _may_ generate more test cases with other backends; if one fails then Hypothesis will report unsound verification in the backend too.
> 
> exhausted:
> 
> Do not request further test cases from this backend; finish testing with test cases generated with the default backend. Common if e.g. native code blocks symbolic reasoning very early.
> 
> discard\_test\_case:
> 
> This particular test case could not be converted to concrete values; skip any further processing and continue with another test case from this backend.

_final class_ hypothesis.internal.intervalsets.IntervalSet(_intervals\=()_)[¶](#hypothesis.internal.intervalsets.IntervalSet "Link to this definition")

A compact and efficient representation of a set of `(a, b)` intervals. Can be treated like a set of integers, in that `n in intervals` will return `True` if `n` is contained in any of the `(a, b)` intervals, and `False` otherwise.

##### Observability[¶](#observability "Link to this heading")

hypothesis.internal.observability.add\_observability\_callback(_f_, _/_, _\*_, _all\_threads\=False_)[¶](#hypothesis.internal.observability.add_observability_callback "Link to this definition")

Adds `f` as a callback for [observability](#observability). `f` should accept one argument, which is an observation. Whenever Hypothesis produces a new observation, it calls each callback with that observation.

If Hypothesis tests are being run from multiple threads, callbacks are tracked per-thread. In other words, `add_observability_callback(f)` only adds `f` as an observability callback for observations produced on that thread.

If `all_threads=True` is passed, `f` will instead be registered as a callback for all threads. This means it will be called for observations generated by all threads, not just the thread which registered `f` as a callback. In this case, `f` will be passed two arguments: the first is the observation, and the second is the integer thread id from [`threading.get_ident()`](https://docs.python.org/3/library/threading.html#threading.get_ident "(in Python v3.14)") where that observation was generated.

We recommend against registering `f` as a callback for both `all_threads=True` and the default `all_threads=False`, due to unclear semantics with [`remove_observability_callback`](#hypothesis.internal.observability.remove_observability_callback "hypothesis.internal.observability.remove_observability_callback").

hypothesis.internal.observability.remove\_observability\_callback(_f_, _/_)[¶](#hypothesis.internal.observability.remove_observability_callback "Link to this definition")

Removes `f` from the [observability](#observability) callbacks.

If `f` is not in the list of observability callbacks, silently do nothing.

If running under multiple threads, `f` will only be removed from the callbacks for this thread.

hypothesis.internal.observability.with\_observability\_callback(_f_, _/_, _\*_, _all\_threads\=False_)[¶](#hypothesis.internal.observability.with_observability_callback "Link to this definition")

A simple context manager which calls [`add_observability_callback`](#hypothesis.internal.observability.add_observability_callback "hypothesis.internal.observability.add_observability_callback") on `f` when it enters and [`remove_observability_callback`](#hypothesis.internal.observability.remove_observability_callback "hypothesis.internal.observability.remove_observability_callback") on `f` when it exits.

hypothesis.internal.observability.observability\_enabled()[¶](#hypothesis.internal.observability.observability_enabled "Link to this definition")

Returns whether or not Hypothesis considers [observability](#observability) to be enabled. Observability is enabled if there is at least one observability callback present.

Callers might use this method to determine whether they should compute an expensive representation that is only used under observability, for instance by [alternative backends](#alternative-backends).

hypothesis.internal.observability.TESTCASE\_CALLBACKS _\= <hypothesis.internal.observability.\_TestcaseCallbacks object>_[¶](#hypothesis.internal.observability.TESTCASE_CALLBACKS "Link to this definition")

Warning

Deprecated in favor of [`add_observability_callback`](#hypothesis.internal.observability.add_observability_callback "hypothesis.internal.observability.add_observability_callback"), [`remove_observability_callback`](#hypothesis.internal.observability.remove_observability_callback "hypothesis.internal.observability.remove_observability_callback"), and [`observability_enabled`](#hypothesis.internal.observability.observability_enabled "hypothesis.internal.observability.observability_enabled").

[`TESTCASE_CALLBACKS`](#hypothesis.internal.observability.TESTCASE_CALLBACKS "hypothesis.internal.observability.TESTCASE_CALLBACKS") remains a thin compatibility shim which forwards `.append`, `.remove`, and `bool()` to those three methods. It is not an attempt to be fully compatible with the previous `TESTCASE_CALLBACKS = []`, so iteration or other usages will not work anymore. Please update to using the new methods instead.

[`TESTCASE_CALLBACKS`](#hypothesis.internal.observability.TESTCASE_CALLBACKS "hypothesis.internal.observability.TESTCASE_CALLBACKS") will eventually be removed.

hypothesis.internal.observability.OBSERVABILITY\_COLLECT\_COVERAGE _\= True_[¶](#hypothesis.internal.observability.OBSERVABILITY_COLLECT_COVERAGE "Link to this definition")

If `False`, do not collect coverage information when observability is enabled.

This is exposed both for performance (as coverage collection can be slow on Python 3.11 and earlier) and size (if you do not use coverage information, you may not want to store it in-memory).

hypothesis.internal.observability.OBSERVABILITY\_CHOICES _\= False_[¶](#hypothesis.internal.observability.OBSERVABILITY_CHOICES "Link to this definition")

If `True`, include the `metadata.choice_nodes` and `metadata.spans` keys in test case observations.

`False` by default. `metadata.choice_nodes` and `metadata.spans` can be a substantial amount of data, and so must be opted-in to, even when observability is enabled.

Warning

EXPERIMENTAL AND UNSTABLE. We are actively working towards a better interface for this as of June 2025, and this attribute may disappear or be renamed without notice.

##### Engine constants[¶](#engine-constants "Link to this heading")

We pick reasonable values for these constants, but if you must, you can monkeypatch them. (Hypothesis is not responsible for any performance degradation that may result).

hypothesis.internal.conjecture.engine.MAX\_SHRINKS _\= 500_[¶](#hypothesis.internal.conjecture.engine.MAX_SHRINKS "Link to this definition")

The maximum number of times the shrinker will reduce the complexity of a failing input before giving up. This avoids falling down a trap of exponential (or worse) complexity, where the shrinker appears to be making progress but will take a substantially long time to finish completely.

hypothesis.internal.conjecture.engine.MAX\_SHRINKING\_SECONDS _\= 300_[¶](#hypothesis.internal.conjecture.engine.MAX_SHRINKING_SECONDS "Link to this definition")

The maximum total time in seconds that the shrinker will try to shrink a failure for before giving up. This is across all shrinks for the same failure, so even if the shrinker successfully reduces the complexity of a single failure several times, it will stop when it hits [`MAX_SHRINKING_SECONDS`](#hypothesis.internal.conjecture.engine.MAX_SHRINKING_SECONDS "hypothesis.internal.conjecture.engine.MAX_SHRINKING_SECONDS") of total time taken.

hypothesis.internal.conjecture.engine.BUFFER\_SIZE _\= 8192_[¶](#hypothesis.internal.conjecture.engine.BUFFER_SIZE "Link to this definition")

The maximum amount of entropy a single test case can use before giving up while making random choices during input generation.

The “unit” of one [`BUFFER_SIZE`](#hypothesis.internal.conjecture.engine.BUFFER_SIZE "hypothesis.internal.conjecture.engine.BUFFER_SIZE") does not have any defined semantics, and you should not rely on it, except that a linear increase [`BUFFER_SIZE`](#hypothesis.internal.conjecture.engine.BUFFER_SIZE "hypothesis.internal.conjecture.engine.BUFFER_SIZE") will linearly increase the amount of entropy a test case can use during generation.

### Stateful tests[¶](#stateful-tests "Link to this heading")

Note

See also [How not to Die Hard with Hypothesis](https://hypothesis.works/articles/how-not-to-die-hard-with-hypothesis/) and [An Introduction to Rule-Based Stateful Testing](https://hypothesis.works/articles/rule-based-stateful-testing/).

With [`@given`](#hypothesis.given "hypothesis.given"), your tests are still something that you mostly write yourself, with Hypothesis providing some data. With Hypothesis’s _stateful testing_, Hypothesis instead tries to generate not just data but entire tests. You specify a number of primitive actions that can be combined together, and then Hypothesis will try to find sequences of those actions that result in a failure.

#### You may not need stateful tests[¶](#you-may-not-need-stateful-tests "Link to this heading")

The basic idea of stateful testing is to make Hypothesis choose actions as well as values for your test, and state machines are a great declarative way to do just that.

For simpler cases though, you might not need them at all - a standard test with [`@given`](#hypothesis.given "hypothesis.given") might be enough, since you can use [`data()`](#hypothesis.strategies.data "hypothesis.strategies.data") in branches or loops. In fact, that’s how the state machine explorer works internally. For more complex workloads though, where a higher level API comes into it’s own, keep reading!

#### Rule-based state machines[¶](#rule-based-state-machines "Link to this heading")

A state machine is very similar to a normal [`@given`](#hypothesis.given "hypothesis.given") based test in that it takes values drawn from strategies and passes them to a user defined test function, which may use assertions to check the system’s behavior. The key difference is that where [`@given`](#hypothesis.given "hypothesis.given") based tests must be independent, rules can be chained together - a single test run may involve multiple rule invocations, which may interact in various ways.

Rules can take normal strategies as arguments, but normal strategies, with the exception of [`runner()`](#hypothesis.strategies.runner "hypothesis.strategies.runner") and [`data()`](#hypothesis.strategies.data "hypothesis.strategies.data"), cannot take into account the current state of the machine. This is where bundles come in.

A rule can, in place of a normal strategy, take a [`Bundle`](#hypothesis.stateful.Bundle "hypothesis.stateful.Bundle"). A [`hypothesis.stateful.Bundle`](#hypothesis.stateful.Bundle "hypothesis.stateful.Bundle") is a named collection of generated values that can be reused by other operations in the test. They are populated with the results of rules, and may be used as arguments to rules, allowing data to flow from one rule to another, and rules to work on the results of previous computations or actions.

Specifically, a rule that specifies `target=a_bundle` will cause its return value to be added to that bundle. A rule that specifies `an_argument=a_bundle` as a strategy will draw a value from that bundle. A rule can also specify that an argument chooses a value from a bundle and removes that value by using [`consumes()`](#hypothesis.stateful.consumes "hypothesis.stateful.consumes") as in `an_argument=consumes(a_bundle)`.

Note

There is some overlap between what you can do with Bundles and what you can do with instance variables. Both represent state that rules can manipulate. If you do not need to draw values that depend on the machine’s state, you can simply use instance variables. If you do need to draw values that depend on the machine’s state, Bundles provide a fairly straightforward way to do this. If you need rules that draw values that depend on the machine’s state in some more complicated way, you will have to abandon bundles. You can use [`runner()`](#hypothesis.strategies.runner "hypothesis.strategies.runner") and [`.flatmap()`](#hypothesis.strategies.SearchStrategy.flatmap "hypothesis.strategies.SearchStrategy.flatmap") to access the instance from a rule: the strategy `runner().flatmap(lambda self: sampled_from(self.a_list))` will draw from the instance variable `a_list`. If you need something more complicated still, you can use [`data()`](#hypothesis.strategies.data "hypothesis.strategies.data") to draw data from the instance (or anywhere else) based on logic in the rule.

The following rule based state machine example is a simplified version of a test for Hypothesis’s example database implementation. An example database maps keys to sets of values, and in this test we compare one implementation of it to a simplified in memory model of its behaviour, which just stores the same values in a Python `dict`. The test then runs operations against both the real database and the in-memory representation of it and looks for discrepancies in their behaviour.

import shutil
import tempfile
from collections import defaultdict

import hypothesis.strategies as st
from hypothesis.database import DirectoryBasedExampleDatabase
from hypothesis.stateful import Bundle, RuleBasedStateMachine, rule

class DatabaseComparison(RuleBasedStateMachine):
    def \_\_init\_\_(self):
        super().\_\_init\_\_()
        self.tempd \= tempfile.mkdtemp()
        self.database \= DirectoryBasedExampleDatabase(self.tempd)
        self.model \= defaultdict(set)

    keys \= Bundle("keys")
    values \= Bundle("values")

    @rule(target\=keys, k\=st.binary())
    def add\_key(self, k):
        return k

    @rule(target\=values, v\=st.binary())
    def add\_value(self, v):
        return v

    @rule(k\=keys, v\=values)
    def save(self, k, v):
        self.model\[k\].add(v)
        self.database.save(k, v)

    @rule(k\=keys, v\=values)
    def delete(self, k, v):
        self.model\[k\].discard(v)
        self.database.delete(k, v)

    @rule(k\=keys)
    def values\_agree(self, k):
        assert set(self.database.fetch(k)) \== self.model\[k\]

    def teardown(self):
        shutil.rmtree(self.tempd)

TestDBComparison \= DatabaseComparison.TestCase

In this we declare two bundles - one for keys, and one for values. We have two trivial rules which just populate them with data (`k` and `v`), and three non-trivial rules: `save` saves a value under a key and `delete` removes a value from a key, in both cases also updating the model of what _should_ be in the database. `values_agree` then checks that the contents of the database agrees with the model for a particular key.

Note

While this could have been simplified by not using bundles, generating keys and values directly in the `save` and `delete` rules, using bundles encourages Hypothesis to choose the same keys and values for multiple operations. The bundle operations establish a “universe” of keys and values that are used in the rules.

We can now integrate this into our test suite by getting a unittest TestCase from it:

TestTrees \= DatabaseComparison.TestCase

\# Or just run with pytest's unittest support
if \_\_name\_\_ \== "\_\_main\_\_":
    unittest.main()

This test currently passes, but if we comment out the line where we call `self.model[k].discard(v)`, we would see the following output when run under pytest:

AssertionError: assert set() \== {b''}

\------------ Hypothesis \------------

state \= DatabaseComparison()
var1 \= state.add\_key(k\=b'')
var2 \= state.add\_value(v\=var1)
state.save(k\=var1, v\=var2)
state.delete(k\=var1, v\=var2)
state.values\_agree(k\=var1)
state.teardown()

Note how it’s printed out a very short program that will demonstrate the problem. The output from a rule based state machine should generally be pretty close to Python code - if you have custom `repr` implementations that don’t return valid Python then it might not be, but most of the time you should just be able to copy and paste the code into a test to reproduce it.

You can control the detailed behaviour with a settings object on the TestCase (this is a normal hypothesis settings object using the defaults at the time the TestCase class was first referenced). For example if you wanted to run fewer examples with larger programs you could change the settings to:

DatabaseComparison.TestCase.settings \= settings(
    max\_examples\=50, stateful\_step\_count\=100
)

Which doubles the number of steps each program runs and halves the number of test cases that will be run.

#### Rules[¶](#rules "Link to this heading")

As said earlier, rules are the most common feature used in RuleBasedStateMachine. They are defined by applying the [`rule()`](#hypothesis.stateful.rule "hypothesis.stateful.rule") decorator on a function. Note that RuleBasedStateMachine must have at least one rule defined and that a single function cannot be used to define multiple rules (this is to avoid having multiple rules doing the same things). Due to the stateful execution method, rules generally cannot take arguments from other sources such as fixtures or `pytest.mark.parametrize` - consider providing them via a strategy such as [`sampled_from()`](#hypothesis.strategies.sampled_from "hypothesis.strategies.sampled_from") instead.

#### Initializes[¶](#initializes "Link to this heading")

Initializes are a special case of rules, which are guaranteed to be run exactly once before any normal rule is called. Note if multiple initialize rules are defined, they will all be called but in any order, and that order will vary from run to run.

Initializes are typically useful to populate bundles:

import hypothesis.strategies as st
from hypothesis.stateful import Bundle, RuleBasedStateMachine, initialize, rule

name\_strategy \= st.text(min\_size\=1).filter(lambda x: "/" not in x)

class NumberModifier(RuleBasedStateMachine):
    folders \= Bundle("folders")
    files \= Bundle("files")

    @initialize(target\=folders)
    def init\_folders(self):
        return "/"

    @rule(target\=folders, parent\=folders, name\=name\_strategy)
    def create\_folder(self, parent, name):
        return f"{parent}/{name}"

    @rule(target\=files, parent\=folders, name\=name\_strategy)
    def create\_file(self, parent, name):
        return f"{parent}/{name}"

Initializes can also allow you to initialize the system under test in a way that depends on values chosen from a strategy. You could do this by putting an instance variable in the state machine that indicates whether the system under test has been initialized or not, and then using preconditions (below) to ensure that exactly one of the rules that initialize it get run before any rules that depend on it being initialized.

#### Preconditions[¶](#preconditions "Link to this heading")

While it’s possible to use [`assume()`](#hypothesis.assume "hypothesis.assume") in RuleBasedStateMachine rules, if you use it in only a few rules you can quickly run into a situation where few or none of your rules pass their assumptions. Thus, Hypothesis provides a [`precondition()`](#hypothesis.stateful.precondition "hypothesis.stateful.precondition") decorator to avoid this problem. The [`precondition()`](#hypothesis.stateful.precondition "hypothesis.stateful.precondition") decorator is used on `rule`\-decorated functions, and must be given a function that returns True or False based on the RuleBasedStateMachine instance.

from hypothesis.stateful import RuleBasedStateMachine, precondition, rule

class NumberModifier(RuleBasedStateMachine):
    num \= 0

    @rule()
    def add\_one(self):
        self.num += 1

    @precondition(lambda self: self.num != 0)
    @rule()
    def divide\_with\_one(self):
        self.num \= 1 / self.num

By using [`precondition()`](#hypothesis.stateful.precondition "hypothesis.stateful.precondition") here instead of [`assume()`](#hypothesis.assume "hypothesis.assume"), Hypothesis can filter the inapplicable rules before running them. This makes it much more likely that a useful sequence of steps will be generated.

Note that currently preconditions can’t access bundles; if you need to use preconditions, you should store relevant data on the instance instead.

#### Invariants[¶](#invariants "Link to this heading")

Often there are invariants that you want to ensure are met after every step in a process. It would be possible to add these as rules that are run, but they would be run zero or multiple times between other rules. Hypothesis provides a decorator that marks a function to be run after every step.

from hypothesis.stateful import RuleBasedStateMachine, invariant, rule

class NumberModifier(RuleBasedStateMachine):
    num \= 0

    @rule()
    def add\_two(self):
        self.num += 2
        if self.num \> 50:
            self.num += 1

    @invariant()
    def is\_even(self):
        assert self.num % 2 \== 0

NumberTest \= NumberModifier.TestCase

Invariants can also have [`precondition()`](#hypothesis.stateful.precondition "hypothesis.stateful.precondition")s applied to them, in which case they will only be run if the precondition function returns true.

Note that currently invariants can’t access bundles; if you need to use invariants, you should store relevant data on the instance instead.

#### More fine grained control[¶](#more-fine-grained-control "Link to this heading")

If you want to bypass the TestCase infrastructure you can invoke these manually. The stateful module exposes the function `run_state_machine_as_test`, which takes an arbitrary function returning a RuleBasedStateMachine and an optional settings parameter and does the same as the class based runTest provided.

### First-party extensions[¶](#first-party-extensions "Link to this heading")

Hypothesis has minimal dependencies, to maximise compatibility and make installing Hypothesis as easy as possible.

Our integrations with specific packages are therefore provided by `extra` modules that need their individual dependencies installed in order to work. You can install these dependencies using the setuptools extra feature as e.g. `pip install hypothesis[django]`. This will check installation of compatible versions.

You can also just install hypothesis into a project using them, ignore the version constraints, and hope for the best.

In general “Which version is Hypothesis compatible with?” is a hard question to answer and even harder to regularly test. Hypothesis is always tested against the latest compatible version and each package will note the expected compatibility range. If you run into a bug with any of these please specify the dependency version.

The following lists the available extras in Hypothesis and their documentation.

*   [hypothesis\[cli\]](#hypothesis-cli)
    
*   [hypothesis\[codemods\]](#codemods)
    
*   [hypothesis\[django\]](#hypothesis-django)
    
*   [hypothesis\[numpy\]](#hypothesis-numpy)
    
*   [hypothesis\[lark\]](#hypothesis-lark)
    
*   [hypothesis\[pytz\]](#hypothesis-pytz)
    
*   [hypothesis\[dateutil\]](#hypothesis-dateutil)
    
*   [hypothesis\[dpcontracts\]](#hypothesis-dpcontracts)
    

### Changelog[¶](#changelog "Link to this heading")

This is a record of all past Hypothesis releases and what went into them, in reverse chronological order. All previous releases are still available [on PyPI](https://pypi.org/project/hypothesis/).

### Hypothesis development[¶](#hypothesis-development "Link to this heading")

Hypothesis development is managed by [David R. MacIver](https://www.drmaciver.com) and [Zac Hatfield-Dodds](https://zhd.dev), respectively the first author and lead maintainer.

_However_, these roles don’t include unpaid feature development on Hypothesis. Our roles as leaders of the project are:

1.  Helping other people do feature development on Hypothesis
    
2.  Fixing bugs and other code health issues
    
3.  Improving documentation
    
4.  General release management work
    
5.  Planning the general roadmap of the project
    
6.  Doing sponsored development on tasks that are too large or in depth for other people to take on
    

So all new features must either be sponsored or implemented by someone else. That being said, the maintenance team takes an active role in shepherding pull requests and helping people write a new feature (see [CONTRIBUTING.rst](https://github.com/HypothesisWorks/hypothesis/blob/master/CONTRIBUTING.rst) for details and [these examples of how the process goes](https://github.com/HypothesisWorks/hypothesis/pulls?q=is%3Apr+is%3Amerged+mentored)). This isn’t “patches welcome”, it’s “we will help you write a patch”.

#### Release policy[¶](#release-policy "Link to this heading")

Hypothesis releases follow [semantic versioning](https://semver.org/).

We maintain backwards-compatibility wherever possible, and use deprecation warnings to mark features that have been superseded by a newer alternative. If you want to detect this, you can upgrade warnings to errors using the [`warnings`](https://docs.python.org/3/library/warnings.html#module-warnings "(in Python v3.14)") module.

We use a rapid release cycle to ensure users get features and bugfixes as soon as possible. Every change to the Hypothesis source is automatically built and published on PyPI as soon as it’s merged into master. [We wrote about this process here](https://hypothesis.works/articles/continuous-releases/).

#### Project roadmap[¶](#project-roadmap "Link to this heading")

Hypothesis does not have a long-term release plan. We respond to bug reports as they are made; new features are released as and when someone volunteers to write and maintain them.

### Compatibility[¶](#compatibility "Link to this heading")

Hypothesis generally does its level best to be compatible with everything you could need it to be compatible with. This document outlines our compatibility status and guarantees.

#### Hypothesis versions[¶](#hypothesis-versions "Link to this heading")

Backwards compatibility is better than backporting fixes, so we use [semantic versioning](#release-policy) and only support the most recent version of Hypothesis.

Documented APIs will not break except between major version bumps. All APIs mentioned in the Hypothesis documentation are public unless explicitly noted as provisional, in which case they may be changed in minor releases. Undocumented attributes, modules, and behaviour may include breaking changes in patch releases.

#### Deprecations[¶](#deprecations "Link to this heading")

Deprecated features will emit [`HypothesisDeprecationWarning`](#hypothesis.errors.HypothesisDeprecationWarning "hypothesis.errors.HypothesisDeprecationWarning") for at least six months, and then be removed in the following major release.

Note however that not all warnings are subject to this grace period; sometimes we strengthen validation by adding a warning, and these may become errors immediately at a major release.

We use custom exception and warning types, so you can see exactly where an error came from, or turn only our warnings into errors.

#### Python versions[¶](#python-versions "Link to this heading")

Hypothesis is supported and tested on CPython and PyPy 3.10+, i.e. all Python versions [that are still supported](https://devguide.python.org/versions/). 32-bit builds of CPython also work, though we only test them on Windows.

Hypothesis does not officially support anything except the latest patch release of each supported Python version. We will fix bugs in earlier patch releases if reported, but they’re not tested in CI and no guarantees are made.

#### Operating systems[¶](#operating-systems "Link to this heading")

In theory, Hypothesis should work anywhere that Python does. In practice, it is known to work and regularly tested on macOS, Windows, Linux, and [Emscripten](https://peps.python.org/pep-0776/).

If you experience issues running Hypothesis on other operating systems, we are happy to accept bug reports which either clearly point to the problem or contain reproducing instructions for a Hypothesis maintainer who does not have the ability to run that OS. It’s hard to fix something we can’t reproduce!

#### Testing frameworks[¶](#testing-frameworks "Link to this heading")

In general, Hypothesis goes to quite a lot of effort to return a function from [`@given`](#hypothesis.given "hypothesis.given") that behaves as closely to a normal test function as possible. This means that most things should work sensibly with most testing frameworks.

Maintainers of testing frameworks may be interested in our support for [custom function execution](#custom-function-execution), which may make some Hypothesis interactions possible to support.

##### pytest[¶](#pytest "Link to this heading")

The main interaction to be aware of between Hypothesis and [pytest](https://pypi.org/project/pytest/) is fixtures.

pytest fixtures are automatically passed to [`@given`](#hypothesis.given "hypothesis.given") tests, as usual. Note that [`@given`](#hypothesis.given "hypothesis.given") supplies parameters from the right, so tests which use a fixture should either be written with the fixture placed first, or with keyword arguments:

@given(st.integers())
def test\_use\_fixture(myfixture, n):
    pass

@given(n\=st.integers())
def test\_use\_fixture(n, myfixture):
    pass

However, function-scoped fixtures run only once for the entire test, not per-input. This can be surprising for fixtures which are expected to set up per-input state. To proactively warn about this, we raise [`HealthCheck.function_scoped_fixture`](#hypothesis.HealthCheck.function_scoped_fixture "hypothesis.HealthCheck.function_scoped_fixture") (unless suppressed with [`settings.suppress_health_check`](#hypothesis.settings.suppress_health_check "hypothesis.settings.suppress_health_check")).

Combining [`@given`](#hypothesis.given "hypothesis.given") and [pytest.mark.parametrize](https://docs.pytest.org/en/stable/reference/reference.html#pytest-mark-parametrize-ref "(in pytest v9.0.1)") is fully supported, again keeping in mind that [`@given`](#hypothesis.given "hypothesis.given") supplies parameters from the right:

@pytest.mark.parametrize("s", \["a", "b", "c"\])
@given(st.integers())
def test\_use\_parametrize(s, n):
    assert isinstance(s, str)
    assert isinstance(n, int)

##### unittest[¶](#unittest "Link to this heading")

[unittest](https://pypi.org/project/unittest/) works out of the box with Hypothesis.

The [`unittest.mock.patch()`](https://docs.python.org/3/library/unittest.mock.html#unittest.mock.patch "(in Python v3.14)") decorator works with [`@given`](#hypothesis.given "hypothesis.given"), but we recommend using it as a context manager within the test instead, to ensure that the mock is per-input, and to avoid poor interactions with Pytest fixtures.

[`unittest.TestCase.subTest()`](https://docs.python.org/3/library/unittest.html#unittest.TestCase.subTest "(in Python v3.14)") is a no-op under Hypothesis, because it interacts poorly with Hypothesis generating hundreds of inputs at a time.

##### Django[¶](#django "Link to this heading")

Integration with Django’s testing requires use of the [Django](#hypothesis-django) extra. The issue is that Django tests reset the database once per test, rather than once per input.

[pytest-django](https://pypi.org/project/pytest-django/) doesn’t yet implement Hypothesis compatibility. You can follow issue [pytest-django#912](https://github.com/pytest-dev/pytest-django/issues/912) for updates.

##### coverage.py[¶](#coverage-py "Link to this heading")

[coverage](https://pypi.org/project/coverage/) works out of the box with Hypothesis. Our own test suite has 100% branch coverage.

##### HypoFuzz[¶](#hypofuzz "Link to this heading")

[HypoFuzz](https://hypofuzz.com/) is built on top of Hypothesis and has native support for it. See also the `hypofuzz` [alternative backend](#alternative-backends).

#### Optional packages[¶](#optional-packages "Link to this heading")

The supported versions of optional packages, for strategies in `hypothesis.extra`, are listed in the documentation for that extra. Our general goal is to support all versions that are supported upstream.

#### Thread-Safety Policy[¶](#thread-safety-policy "Link to this heading")

As of [version 6.136.9](changelog.html#v6-136-9), Hypothesis is thread-safe. Each of the following is fully supported, and tested regularly in CI:

*   Running tests in multiple processes
    
*   Running separate tests in multiple threads
    
*   Running the same test in multiple threads
    

If you find a bug here, please report it. The main risks internally are global state, shared caches, and cached strategies.

##### Thread usage inside tests[¶](#thread-usage-inside-tests "Link to this heading")

Tests that spawn threads internally are supported by Hypothesis.

However, these as with any Hypothesis test, these tests must have deterministic test outcomes and data generation. For example, if timing changes in the threads change the sequence of dynamic draws from [`@composite`](#hypothesis.strategies.composite "hypothesis.strategies.composite") or [`data()`](#hypothesis.strategies.data "hypothesis.strategies.data"), Hypothesis may report the test as flaky. The solution here is to refactor data generation so it does not depend on test timings.

##### Cross-thread API calls[¶](#cross-thread-api-calls "Link to this heading")

In theory, Hypothesis supports cross-thread API calls, for instance spawning a thread inside of a test and using that to draw from [`@composite`](#hypothesis.strategies.composite "hypothesis.strategies.composite") or [`data()`](#hypothesis.strategies.data "hypothesis.strategies.data"), or to call [`event()`](#hypothesis.event "hypothesis.event"), [`target()`](#hypothesis.target "hypothesis.target"), or [`assume()`](#hypothesis.assume "hypothesis.assume").

However, we have not explicitly audited this behavior, and do not regularly test it in our CI. If you find a bug here, please report it. If our investigation determines that we cannot support cross-thread calls for the feature in question, we will update this page accordingly.

#### Type hints[¶](#type-hints "Link to this heading")

We ship type hints with Hypothesis itself. Though we always try to minimize breakage, we may make breaking changes to these between minor releases and do not commit to maintaining a fully stable interface for type hints.

We may also find more precise ways to describe the type of various interfaces, or change their type and runtime behaviour together in a way which is otherwise backwards-compatible.

There are known issues with inferring the type of examples generated by [`deferred()`](#hypothesis.strategies.deferred "hypothesis.strategies.deferred"), [`recursive()`](#hypothesis.strategies.recursive "hypothesis.strategies.recursive"), [`one_of()`](#hypothesis.strategies.one_of "hypothesis.strategies.one_of"), [`dictionaries()`](#hypothesis.strategies.dictionaries "hypothesis.strategies.dictionaries"), and [`fixed_dictionaries()`](#hypothesis.strategies.fixed_dictionaries "hypothesis.strategies.fixed_dictionaries"). We’re following proposed updates to Python’s typing standards, but unfortunately the long-standing interfaces of these strategies cannot (yet) be statically typechecked.

### Projects using Hypothesis[¶](#projects-using-hypothesis "Link to this heading")

Hypothesis is downloaded [over 4 million times each week](https://pypistats.org/packages/hypothesis), and was used by [more than 5% of Python users surveyed by the PSF in 2023](https://lp.jetbrains.com/python-developers-survey-2023/)!

The following notable open-source projects use Hypothesis to test their code: [pytorch](https://github.com/pytorch/pytorch), [jax](https://github.com/jax-ml/jax), [PyPy](https://github.com/pypy/pypy), [numpy](https://github.com/numpy/numpy), [pandas](https://github.com/pandas-dev/pandas), [attrs](https://github.com/python-attrs/attrs), [chardet](https://github.com/chardet/chardet), [bidict](https://github.com/jab/bidict), [xarray](https://github.com/pydata/xarray), [array-api-tests](https://github.com/data-apis/array-api-tests), [pandera](https://github.com/unionai-oss/pandera), [ivy](https://github.com/ivy-llc/ivy), [zenml](https://github.com/zenml-io/zenml), [mercurial](https://www.mercurial-scm.org/), [qutebrowser](https://github.com/qutebrowser/qutebrowser), [dry-python/returns](https://github.com/dry-python/returns), [argon2\_cffi](https://github.com/hynek/argon2-cffi), [axelrod](https://github.com/Axelrod-Python/Axelrod), [hyper-h2](https://github.com/python-hyper/h2), [MDAnalysis](https://github.com/MDAnalysis/mdanalysis), [napari](https://github.com/napari/napari), [natsort](https://github.com/SethMMorton/natsort), [vdirsyncer](https://github.com/pimutils/vdirsyncer), and [pyrsistent](https://github.com/tobgu/pyrsistent). You can find [thousands more projects tested by Hypothesis on GitHub](https://github.com/HypothesisWorks/hypothesis/network/dependents).

There are also dozens of [first-party](#document-extras) and [third-party extensions](#document-extensions) integrating Hypothesis with a wide variety of libraries and data formats.

#### Research papers about Hypothesis[¶](#research-papers-about-hypothesis "Link to this heading")

Looking to read more about Hypothesis and property-based testing? Hypothesis has been the subject of a number of research papers:

1.  [Hypothesis: A new approach to property-based testing](https://doi.org/10.21105/joss.01891) (2019)\*
    
2.  [Test-Case Reduction via Test-Case Generation: Insights from the Hypothesis Reducer](https://doi.org/10.4230/LIPIcs.ECOOP.2020.13) (2020)\*
    
3.  [Deriving semantics-aware fuzzers from web API schemas](https://dl.acm.org/doi/10.1145/3510454.3528637) (2022)\*
    
4.  [Tyche: Making Sense of PBT Effectiveness](https://dl.acm.org/doi/10.1145/3654777.3676407) (2024)\*
    
5.  [An Empirical Evaluation of Property-Based Testing in Python](https://dl.acm.org/doi/10.1145/3764068) (2025)
    
6.  [Agentic Property-Based Testing: Finding Bugs Across the Python Ecosystem](https://doi.org/10.48550/arXiv.2510.09907) (2025)\*
    

\* _Author list includes one or more Hypothesis maintainers_

### Third-party extensions[¶](#third-party-extensions "Link to this heading")

There are a number of open-source community libraries that extend Hypothesis. This page lists some of them; you can find more by searching PyPI [by keyword](https://pypi.org/search/?q=hypothesis) or [by framework classifier](https://pypi.org/search/?c=Framework+%3A%3A+Hypothesis).

If there’s something missing which you think should be here, let us know!

Note

Being listed on this page does not imply that the Hypothesis maintainers endorse a package.

#### External strategies[¶](#external-strategies "Link to this heading")

Some packages provide strategies directly:

*   [hypothesis-fspaths](https://pypi.org/project/hypothesis-fspaths/) - strategy to generate filesystem paths.
    
*   [hypothesis-geojson](https://pypi.org/project/hypothesis-geojson/) - strategy to generate [GeoJson](https://geojson.org/).
    
*   [hypothesis-geometry](https://pypi.org/project/hypothesis-geometry/) - strategies to generate geometric objects.
    
*   [hs-dbus-signature](https://pypi.org/project/hs-dbus-signature/) - strategy to generate arbitrary [D-Bus signatures](https://www.freedesktop.org/wiki/Software/dbus/).
    
*   [hypothesis-sqlalchemy](https://pypi.org/project/hypothesis-sqlalchemy/) - strategies to generate [SQLAlchemy](https://pypi.org/project/SQLAlchemy/) objects.
    
*   [hypothesis-ros](https://pypi.org/project/hypothesis-ros/) - strategies to generate messages and parameters for the [Robot Operating System](https://www.ros.org/).
    
*   [hypothesis-csv](https://pypi.org/project/hypothesis-csv/) - strategy to generate CSV files.
    
*   [hypothesis-networkx](https://pypi.org/project/hypothesis-networkx/) - strategy to generate [networkx](https://pypi.org/project/networkx/) graphs.
    
*   [hypothesis-bio](https://pypi.org/project/hypothesis-bio/) - strategies for bioinformatics data, such as DNA, codons, FASTA, and FASTQ formats.
    
*   [hypothesis-rdkit](https://pypi.org/project/hypothesis-rdkit/) - strategies to generate RDKit molecules and representations such as SMILES and mol blocks
    
*   [hypothesmith](https://pypi.org/project/hypothesmith/) - strategy to generate syntatically-valid Python code.
    
*   [hypothesis-torch](https://pypi.org/project/hypothesis-torch/) - strategy to generate various [Pytorch](https://pytorch.org/) structures (including tensors and modules).
    

Others provide a function to infer a strategy from some other schema:

*   [hypothesis-jsonschema](https://pypi.org/project/hypothesis-jsonschema/) - infer strategies from [JSON schemas](https://json-schema.org/).
    
*   [lollipop-hypothesis](https://pypi.org/project/lollipop-hypothesis/) - infer strategies from [lollipop](https://pypi.org/project/lollipop/) schemas.
    
*   [hypothesis-drf](https://pypi.org/project/hypothesis-drf/) - infer strategies from a [djangorestframework](https://pypi.org/project/djangorestframework/) serialiser.
    
*   [hypothesis-graphql](https://pypi.org/project/hypothesis-graphql/) - infer strategies from [GraphQL schemas](https://graphql.org/).
    
*   [hypothesis-mongoengine](https://pypi.org/project/hypothesis-mongoengine/) - infer strategies from a [mongoengine](https://pypi.org/project/mongoengine/) model.
    
*   [hypothesis-pb](https://pypi.org/project/hypothesis-pb/) - infer strategies from [Protocol Buffer](https://protobuf.dev/) schemas.
    

Or some other custom integration, such as a [“hypothesis” entry point](#entry-points):

*   [deal](https://pypi.org/project/deal/) is a design-by-contract library with built-in Hypothesis support.
    
*   [icontract-hypothesis](https://pypi.org/project/icontract-hypothesis/) infers strategies from [icontract](https://pypi.org/project/icontract/) code contracts.
    
*   [pandera](https://pypi.org/project/pandera/) schemas all have a `.strategy()` method, which returns a strategy for matching [`DataFrame`](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html#pandas.DataFrame "(in pandas v2.3.3)")s.
    
*   [Pydantic](https://pypi.org/project/pydantic/) automatically registers constrained types - so [`builds()`](#hypothesis.strategies.builds "hypothesis.strategies.builds") and [`from_type()`](#hypothesis.strategies.from_type "hypothesis.strategies.from_type") “just work” regardless of the underlying implementation.
    

#### Other cool things[¶](#other-cool-things "Link to this heading")

[Tyche](https://marketplace.visualstudio.com/items?itemName=HarrisonGoldstein.tyche) ([source](https://github.com/tyche-pbt)) is a VSCode extension which provides live insights into your property-based tests, including the distribution of generated inputs and the resulting code coverage. You can [read the research paper here](https://harrisongoldste.in/papers/uist23.pdf).

[schemathesis](https://pypi.org/project/schemathesis/) is a tool for testing web applications built with [Open API / Swagger specifications](https://swagger.io/). It reads the schema and generates test cases which will ensure that the application is compliant with its schema. The application under test could be written in any language, the only thing you need is a valid API schema in a supported format. Includes CLI and convenient [pytest](https://pypi.org/project/pytest/) integration. Powered by Hypothesis and [hypothesis-jsonschema](https://pypi.org/project/hypothesis-jsonschema/), inspired by the earlier [swagger-conformance](https://pypi.org/project/swagger-conformance/) library.

[Trio](https://trio.readthedocs.io/) is an async framework with “an obsessive focus on usability and correctness”, so naturally it works with Hypothesis! [pytest-trio](https://pypi.org/project/pytest-trio/) includes [a custom hook](#custom-function-execution) that allows `@given(...)` to work with Trio-style async test functions, and [hypothesis-trio](https://pypi.org/project/hypothesis-trio/) includes stateful testing extensions to support concurrent programs.

[pymtl3](https://pypi.org/project/pymtl3/) is “an open-source Python-based hardware generation, simulation, and verification framework with multi-level hardware modeling support”, which ships with Hypothesis integrations to check that all of those levels are equivalent, from function-level to register-transfer level and even to hardware.

[battle-tested](https://pypi.org/project/battle-tested/) is a fuzzing tool that will show you how your code can fail - by trying all kinds of inputs and reporting whatever happens.

[pytest-subtesthack](https://pypi.org/project/pytest-subtesthack/) functions as a workaround for [issue #377](https://github.com/HypothesisWorks/hypothesis/issues/377).

[returns](https://pypi.org/project/returns/) uses Hypothesis to verify that Higher Kinded Types correctly implement functor, applicative, monad, and other laws; allowing a declarative approach to be combined with traditional pythonic code.

[icontract-hypothesis](https://pypi.org/project/icontract-hypothesis/) includes a [ghostwriter](#ghostwriter) for test files and IDE integrations such as [icontract-hypothesis-vim](https://github.com/mristin/icontract-hypothesis-vim), [icontract-hypothesis-pycharm](https://github.com/mristin/icontract-hypothesis-pycharm), and [icontract-hypothesis-vscode](https://github.com/mristin/icontract-hypothesis-vscode) - you can run a quick ‘smoke test’ with only a few keystrokes for any type-annotated function, even if it doesn’t have any contracts!

#### Writing an extension[¶](#writing-an-extension "Link to this heading")

Note

See [CONTRIBUTING.rst](https://github.com/HypothesisWorks/hypothesis/blob/master/CONTRIBUTING.rst) for more information.

New strategies can be added to Hypothesis, or published as an external package on PyPI - either is fine for most strategies. If in doubt, ask!

It’s generally much easier to get things working outside, because there’s more freedom to experiment and fewer requirements in stability and API style. We’re happy to review and help with external packages as well as pull requests!

If you’re thinking about writing an extension, please name it `hypothesis-{something}` - a standard prefix makes the community more visible and searching for extensions easier. And make sure you use the `Framework :: Hypothesis` trove classifier!

On the other hand, being inside gets you access to some deeper implementation features (if you need them) and better long-term guarantees about maintenance. We particularly encourage pull requests for new composable primitives that make implementing other strategies easier, or for widely used types in the standard library. Strategies for other things are also welcome; anything with external dependencies just goes in `hypothesis.extra`.

Tools such as assertion helpers may also need to check whether the current test is using Hypothesis. For that, see [`currently_in_test_context()`](#hypothesis.currently_in_test_context "hypothesis.currently_in_test_context").

#### Hypothesis integration via entry points[¶](#hypothesis-integration-via-entry-points "Link to this heading")

If you would like to ship Hypothesis strategies for a custom type - either as part of the upstream library, or as a third-party extension, there’s a catch: [`from_type()`](#hypothesis.strategies.from_type "hypothesis.strategies.from_type") only works after the corresponding call to [`register_type_strategy()`](#hypothesis.strategies.register_type_strategy "hypothesis.strategies.register_type_strategy"), and you’ll have the same problem with [`register_random()`](#hypothesis.register_random "hypothesis.register_random"). This means that either

*   you have to try importing Hypothesis to register the strategy when _your_ library is imported, though that’s only useful at test time, or
    
*   the user has to call a ‘register the strategies’ helper that you provide before running their tests
    

[Entry points](https://setuptools.pypa.io/en/latest/userguide/entry_point.html) are Python’s standard way of automating the latter: when you register a `"hypothesis"` entry point in your `pyproject.toml`, we’ll import and run it automatically when _hypothesis_ is imported. Nothing happens unless Hypothesis is already in use, and it’s totally seamless for downstream users!

Let’s look at an example. You start by adding a function somewhere in your package that does all the Hypothesis-related setup work:

\# mymodule.py

class MyCustomType:
    def \_\_init\_\_(self, x: int):
        assert x \>= 0, f"got {x}, but only positive numbers are allowed"
        self.x \= x

def \_hypothesis\_setup\_hook():
    import hypothesis.strategies as st

    st.register\_type\_strategy(MyCustomType, st.integers(min\_value\=0))

and then declare this as your `"hypothesis"` entry point:

\# pyproject.toml

\# You can list a module to import by dotted name
\[project.entry-points.hypothesis\]
\_ \= "mymodule.a\_submodule"

\# Or name a specific function, and Hypothesis will call it for you
\[project.entry-points.hypothesis\]
\_ \= "mymodule:\_hypothesis\_setup\_hook"

And that’s all it takes!

HYPOTHESIS\_NO\_PLUGINS[¶](#envvar-HYPOTHESIS_NO_PLUGINS "Link to this definition")

If set, disables automatic loading of all hypothesis plugins. This is probably only useful for our own self-tests, but documented in case it might help narrow down any particularly weird bugs in complex environments.

##### Interaction with [pytest-cov](https://pypi.org/project/pytest-cov/)[¶](#interaction-with-pytest-cov "Link to this heading")

Because pytest does not load plugins from entrypoints in any particular order, using the Hypothesis entrypoint may import your module before [pytest-cov](https://pypi.org/project/pytest-cov/) starts. [This is a known issue](https://github.com/pytest-dev/pytest/issues/935), but there are workarounds.

You can use **coverage run pytest ...** instead of **pytest --cov ...**, opting out of the pytest plugin entirely. Alternatively, you can ensure that Hypothesis is loaded after coverage measurement is started by disabling the entrypoint, and loading our pytest plugin from your `conftest.py` instead:

echo "pytest\_plugins = \['hypothesis.extra.pytestplugin'\]\\n" \> tests/conftest.py
pytest \-p "no:hypothesispytest" ...

Another alternative, which we in fact use in our CI self-tests because it works well also with parallel tests, is to automatically start coverage early for all new processes if an environment variable is set. This automatic starting is set up by the PyPi package [coverage\_enable\_subprocess](https://pypi.org/project/coverage_enable_subprocess/).

This means all configuration must be done in `.coveragerc`, and not on the command line:

\[run\]
parallel \= True
source \= ...

Then, set the relevant environment variable and run normally:

python -m pip install coverage\_enable\_subprocess
export COVERAGE\_PROCESS\_START=$PATH/.coveragerc
pytest \[-n auto\] ...
coverage combine
coverage report

#### Alternative backends for Hypothesis[¶](#alternative-backends-for-hypothesis "Link to this heading")

See also

See also the [Alternative backends interface](#alternative-backends-internals) for details on implementing your own alternative backend.

Hypothesis supports alternative backends, which tells Hypothesis how to generate primitive types. This enables powerful generation techniques which are compatible with all parts of Hypothesis, including the database and shrinking.

Hypothesis includes the following backends:

hypothesis

The default backend.

hypothesis-urandom

The same as the default backend, but uses `/dev/urandom` as its source of randomness, instead of the standard PRNG in [`random.Random`](https://docs.python.org/3/library/random.html#random.Random "(in Python v3.14)"). The only reason to use this backend over the default `backend="hypothesis"` is if you are also using [Antithesis](https://antithesis.com/), in which case this allows Antithesis mutation of `/dev/urandom` to control the values generated by Hypothesis.

`/dev/urandom` is not available on Windows, so we emit a warning and fall back to the hypothesis backend there.

hypofuzz

Generates inputs using coverage-guided fuzzing. See [HypoFuzz](https://hypofuzz.com/) for details.

Requires `pip install hypofuzz`.

crosshair

Generates inputs using SMT solvers like z3, which is particularly effective at satisfying difficult checks in your code, like `if` or `==` statements.

Requires `pip install hypothesis[crosshair]`.

You can change the backend for a test with the [`settings.backend`](#hypothesis.settings.backend "hypothesis.settings.backend") setting. For instance, after `pip install hypothesis[crosshair]`, you can use [crosshair](https://pypi.org/project/crosshair-tool/) to generate inputs with SMT via the [hypothesis-crosshair](https://pypi.org/project/hypothesis-crosshair/) backend:

from hypothesis import given, settings, strategies as st

@settings(backend\="crosshair")  \# pip install hypothesis\[crosshair\]
@given(st.integers())
def test\_needs\_solver(x):
    assert x != 123456789

Failures found by alternative backends are saved to the database and shrink just like normally generated inputs, and in general interact with every feature of Hypothesis as you would expect.

### Packaging guidelines[¶](#packaging-guidelines "Link to this heading")

Downstream packagers often want to package Hypothesis. Here are some guidelines.

The primary guideline is this: If you are not prepared to keep up with the Hypothesis release schedule, don’t. You will be doing your users a disservice.

Hypothesis has a very frequent release schedule. We often release new versions multiple times a week.

If you _are_ prepared to keep up with this schedule, you might find the rest of this document useful.

#### Release tarballs[¶](#release-tarballs "Link to this heading")

These are available from [the GitHub releases page](https://github.com/HypothesisWorks/hypothesis/releases). The tarballs on PyPI are intended for installation from a Python tool such as [pip](https://pypi.org/project/pip/) and should not be considered complete releases. Requests to include additional files in them will not be granted. Their absence is not a bug.

#### Dependencies[¶](#dependencies "Link to this heading")

##### Python versions[¶](#python-versions "Link to this heading")

Hypothesis is designed to work with a range of Python versions - we support [all versions of CPython with upstream support](https://devguide.python.org/#status-of-python-branches). We also support the latest versions of PyPy for Python 3.

##### Other Python libraries[¶](#other-python-libraries "Link to this heading")

Hypothesis has _mandatory_ dependencies on the following libraries:

*   [sortedcontainers](https://pypi.org/project/sortedcontainers/)
    

Hypothesis has _optional_ dependencies on the following libraries:

\[project.optional\-dependencies\]
cli \= \["click>=7.0", "black>=20.8b0", "rich>=9.0.0"\]
codemods \= \["libcst>=0.3.16"\]
ghostwriter \= \["black>=20.8b0"\]
pytz \= \["pytz>=2014.1"\]
dateutil \= \["python-dateutil>=1.4"\]
lark \= \["lark>=0.10.1"\]  \# probably still works with old \`lark-parser\` too
numpy \= \["numpy>=1.21.6"\]  \# oldest with wheels for non-EOL Python (for now)
pandas \= \["pandas>=1.1"\]
pytest \= \["pytest>=4.6"\]
dpcontracts \= \["dpcontracts>=0.4"\]
redis \= \["redis>=3.0.0"\]
crosshair \= \["hypothesis-crosshair>=0.0.26", "crosshair-tool>=0.0.98"\]
\# zoneinfo is an odd one: every dependency is platform-conditional.
zoneinfo \= \["tzdata>=2025.2; sys\_platform == 'win32' or sys\_platform == 'emscripten'"\]
\# We only support Django versions with upstream support - see
\# https://www.djangoproject.com/download/#supported-versions
\# We also leave the choice of timezone library to the user, since it
\# might be zoneinfo or pytz depending on version and configuration.
django \= \["django>=4.2"\]
watchdog \= \["watchdog>=4.0.0"\]

The way this works when installing Hypothesis normally is that these features become available if the relevant library is installed.

Specifically for [pytest](https://pypi.org/project/pytest/), our plugin supports versions of pytest which have been out of upstream support for some time. Hypothesis tests can still be executed by even older versions of pytest - you just won’t have the plugin to provide automatic marks, helpful usage warnings, and per-test statistics.

#### Testing Hypothesis[¶](#testing-hypothesis "Link to this heading")

If you want to test Hypothesis as part of your packaging you will probably not want to use the mechanisms Hypothesis itself uses for running its tests, because it has a lot of logic for installing and testing against different versions of Python.

The tests must be run with fairly recent tooling; check the [tree/master/requirements/](https://github.com/HypothesisWorks/hypothesis/tree/master/requirements/) directory for details.

The organisation of the tests is described in the [hypothesis-python/tests/README.rst](https://github.com/HypothesisWorks/hypothesis/blob/master/hypothesis-python/tests/README.rst).

#### Examples[¶](#examples "Link to this heading")

*   [arch linux](https://archlinux.org/packages/extra/any/python-hypothesis/)
    
*   [fedora](https://src.fedoraproject.org/rpms/python-hypothesis)
    
*   [gentoo](https://packages.gentoo.org/packages/dev-python/hypothesis)
    

### Community[¶](#community "Link to this heading")

The Hypothesis community is full of excellent people who can answer your questions and help you out. Please do join us:

*   You can post a question on Stack Overflow using the [python-hypothesis](https://stackoverflow.com/questions/tagged/python-hypothesis) tag.
    
*   We also have [a mailing list](https://groups.google.com/forum/#!forum/hypothesis-users). Feel free to use it to ask for help, provide feedback, or discuss anything remotely Hypothesis related at all.
    

Note that the [Hypothesis code of conduct](https://github.com/HypothesisWorks/hypothesis/blob/master/CODE_OF_CONDUCT.rst) applies in all Hypothesis community spaces!

If you would like to cite Hypothesis, please consider [our suggested citation](https://github.com/HypothesisWorks/hypothesis/blob/master/CITATION.cff).

If you like repo badges, we suggest the following badge, which you can add with Markdown or reStructuredText respectively:

![https://img.shields.io/badge/hypothesis-tested-brightgreen.svg](https://img.shields.io/badge/hypothesis-tested-brightgreen.svg)

\[!\[Tested with Hypothesis\](https://img.shields.io/badge/hypothesis-tested-brightgreen.svg)\](https://hypothesis.readthedocs.io/)

.. image:: https://img.shields.io/badge/hypothesis-tested-brightgreen.svg
   :alt: Tested with Hypothesis
   :target: https://hypothesis.readthedocs.io

Finally, we have a beautiful logo which appears online, and often on stickers:

[![The Hypothesis logo, a dragonfly with rainbow wings](_images/dragonfly-rainbow.svg)](_images/dragonfly-rainbow.svg)

As well as being beautiful, dragonflies actively hunt down bugs for a living! You can find the images and a usage guide in the [brand](https://github.com/HypothesisWorks/hypothesis/blob/master/brand) directory on GitHub, or find us at conferences where we often have stickers and sometimes other swag.

Copyright © 2013-2025, the Hypothesis team

Made with [Sphinx](https://www.sphinx-doc.org/) and [@pradyunsg](https://pradyunsg.me)'s [Furo](https://github.com/pradyunsg/furo)

On this page

*   [Quickstart](#document-quickstart)
*   [Tutorial](#document-tutorial/index)
*   [How-to guides](#document-how-to/index)
*   [Explanations](#document-explanation/index)
*   [API Reference](#document-reference/index)
*   [Stateful tests](#document-stateful)
*   [Extras](#document-extras)
*   [Changelog](#document-changelog)

