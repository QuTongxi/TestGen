# Adding notes

When a test fails, Hypothesis will normally print output that looks like this:

```
Falsifying example: test_a_thing(x=1, y="foo")
```

Sometimes you want to add some additional information to a failure, such as the output of some intermediate step in your test. The `note()` function lets you do this:

```python
>>> from hypothesis import given, note, strategies as st
>>> @given(st.lists(st.integers()), st.randoms())
... def test_shuffle_is_noop(ls, r):
...     ls2 = list(ls)
...     r.shuffle(ls2)
...     note(f"Shuffle: {ls2!r}")
...     assert ls == ls2
...
>>> try:
...     test_shuffle_is_noop()
... except AssertionError:
...     print("ls != ls2")
...
Falsifying example: test_shuffle_is_noop(ls=[0, 1], r=RandomWithSeed(1))
Shuffle: [1, 0]
ls != ls2
```

`note()` is like a print statement that gets attached to the falsifying example reported by Hypothesis. It’s also reported by observability, and shown for all examples (if `settings.verbosity` is set to `Verbosity.verbose` or higher).

`event()` is a similar function which tells Hypothesis to count the number of test cases which reported each distinct value you pass, for inclusion in test statistics and observability reports.