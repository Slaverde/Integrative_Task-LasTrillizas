# Stage 2 - Sorting by profile

Implementation: `sort_for_profile` and `sort_by_vocabulary` in
`src/normalization/sorting.py`. Tests: `tests/test_normalization_sorting.py`.

After the transducers, `normalize` returns the canonical tokens in the order in
which the candidate wrote them. Before the automata of stage 3 read them, the
tokens are put in a fixed order given by the profile. The result then does not
depend on how the resume was written: `Git, NodeJS, JS, Postgres, React.js` and
`JS, React.js, NodeJS, Postgres, Git` give the same sequence.

## 1. The rule

`sort_for_profile(tokens, profile)` sorts by a pair of numbers:

1. **Category rank.** The position of the token's category in
   `PROFILE_ORDER[profile]`. A category that the profile does not list gets a
   rank after all the listed ones.
2. **Vocabulary position.** The position of the token in `vocabulary.TOKENS`.
   It breaks the ties inside a category (`JAVASCRIPT` before `TYPESCRIPT`
   before `PYTHON`) and fixes the order of the tokens outside the profile.

Both numbers depend only on the token and the profile, so the output is the
same for every permutation of the input. A string that is not a token of the
vocabulary raises `ValueError`; `normalize` never produces one.

The same function serves the four profiles. The only thing that changes is the
data, `PROFILE_ORDER`:

| Profile | Category order |
|---|---|
| `FULL_STACK_DEVELOPER` | LANGUAGE -> FRONTEND -> BACKEND -> DATABASE -> VERSION_CONTROL -> CONCEPT |
| `MACHINE_LEARNING_ENGINEER` | LANGUAGE -> DATA_LIBRARY -> ML_LIBRARY -> CONCEPT -> DATABASE -> VERSION_CONTROL |
| `BACKEND_DEVELOPER` (provisional) | LANGUAGE -> BACKEND -> DATABASE -> CONCEPT -> TOOL -> VERSION_CONTROL |
| `DATA_SCIENTIST` (provisional) | LANGUAGE -> DATA_LIBRARY -> ML_LIBRARY -> DATABASE -> TOOL -> VERSION_CONTROL |

The two provisional profiles take their order from `vocabulary.py`; when the
professor's requirements change it, update this table.

`sort_by_vocabulary(tokens)` is the profile-free version (only rule 2). The
pipeline uses it to list the skills of a candidate once in the DSL, because the
DSL has one skills section for all profiles.

## 2. Examples

The assignment's example, `Git, NodeJS, JS, Postgres, React.js`, normalized and
shuffled (`GIT, NODE_JS, JAVASCRIPT, POSTGRESQL, REACT`):

| Profile | Sorted sequence |
|---|---|
| `FULL_STACK_DEVELOPER` | JAVASCRIPT, REACT, NODE_JS, POSTGRESQL, GIT |
| `MACHINE_LEARNING_ENGINEER` | JAVASCRIPT, POSTGRESQL, GIT, REACT, NODE_JS |
| `BACKEND_DEVELOPER` | JAVASCRIPT, NODE_JS, POSTGRESQL, GIT, REACT |
| `DATA_SCIENTIST` | JAVASCRIPT, POSTGRESQL, GIT, REACT, NODE_JS |

For Full Stack this is `JAVASCRIPT, REACT, NODE_JS, POSTGRESQL, GIT`, the
sequence that the assignment shows. The machine-learning and data profiles
list neither `FRONTEND` nor `BACKEND`, so `REACT` and `NODE_JS` go to the end;
the backend profile lists `BACKEND` but not `FRONTEND`.

A machine-learning resume, `Git, SQL, TensorFlow, NumPy, scikit-learn, Pandas,
Python`:

| Profile | Sorted sequence |
|---|---|
| `FULL_STACK_DEVELOPER` | PYTHON, SQL, GIT, PANDAS, NUMPY, SCIKIT_LEARN, TENSORFLOW |
| `MACHINE_LEARNING_ENGINEER` | PYTHON, PANDAS, NUMPY, SCIKIT_LEARN, TENSORFLOW, SQL, GIT |
| `BACKEND_DEVELOPER` | PYTHON, SQL, GIT, PANDAS, NUMPY, SCIKIT_LEARN, TENSORFLOW |
| `DATA_SCIENTIST` | PYTHON, PANDAS, NUMPY, SCIKIT_LEARN, TENSORFLOW, SQL, GIT |

Tokens of categories that a profile does not list go last
(`DOCKER, PYTORCH, KERAS, JAVA, TENSORFLOW, GIT`):

| Profile | Sorted sequence |
|---|---|
| `FULL_STACK_DEVELOPER` | JAVA, GIT, TENSORFLOW, PYTORCH, KERAS, DOCKER |
| `MACHINE_LEARNING_ENGINEER` | JAVA, TENSORFLOW, PYTORCH, KERAS, GIT, DOCKER |
| `BACKEND_DEVELOPER` | JAVA, DOCKER, GIT, TENSORFLOW, PYTORCH, KERAS |
| `DATA_SCIENTIST` | JAVA, TENSORFLOW, PYTORCH, KERAS, DOCKER, GIT |

## 3. Why the tokens outside the profile go last

The other option was to remove them, but then the output would not be "the same
tokens in a new order", and the contract of `docs/contracts.md` would change.
Putting them last keeps every token and has one consequence for stage 3: an
automaton reads first the categories that its profile asks for, in order, and
then a tail of tokens it does not care about. The tail only needs loops in the
accepting states.

Tokens of the *same* category as a required one (`PYTHON` when Full Stack asks
for `JAVASCRIPT` or `TYPESCRIPT`) are not removed either. They stay inside the
category, in vocabulary order, and the automaton has to tolerate them.

## 4. Why sorting is not a transducer

Stage 2 normalizes with finite-state transducers, but this step is ordinary
code. The reason is a limit of the model, and it is worth knowing for the
presentation.

**In general, a finite-state transducer cannot sort.** Take the alphabet
`{a, b}` and the function that moves every `a` before every `b`; its value on
`b^n a^n` is `a^n b^n`. A transducer that reads `b^n` has written nothing
yet, because it does not know how many `a` will come. After the `a`'s it has
to write `n` letters `b`, so it must remember `n`. A machine with `k` states
cannot tell `k + 1` different values of `n` apart (pumping argument), so no
finite machine does it. Sorting needs memory that grows with the input.

**For our input it is possible, but not reasonable.** After `normalize` a token
appears at most once, and there are only 39 tokens. A function with a finite
domain is always rational, so a transducer exists: its state would be the set
of tokens read so far and, at the end marker, it would write them in order. It
would need one state per subset, 2^39 = 549,755,813,888 states, for each of the four
profiles. The sort in `sorting.py` does the same job with a pair of numbers
and one call to `sorted`.

So the pipeline uses transducers where the problem is local (rewrite a
spelling into a token, without memory beyond the characters read) and code
where it needs to compare and reorder the whole sequence.

## 5. Properties checked by the tests

| Property | Test |
|---|---|
| The assignment's example gives `JAVASCRIPT, REACT, NODE_JS, POSTGRESQL, GIT` | `test_example_of_the_assignment` |
| The output is a permutation of the input (nothing is lost or invented) | `test_every_profile_goes_through_the_same_function` |
| Categories appear in the order of the profile | `test_every_profile_goes_through_the_same_function` |
| The result does not depend on the input order (all permutations of 6 tokens, 4 profiles) | `test_the_result_does_not_depend_on_the_input_order` |
| Sorting twice changes nothing | `test_sorting_twice_changes_nothing` |
| Tokens outside the profile go last, in vocabulary order | `test_tokens_of_a_category_outside_the_profile_go_last_in_vocabulary_order` |
| Ties inside a category follow the vocabulary | `test_ties_inside_a_category_follow_the_vocabulary` |
| A string that is not a token is an error | `test_unknown_tokens_are_an_error` |
