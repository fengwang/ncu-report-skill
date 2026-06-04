You did not write this code and you did not participate in the review.
Assume the completion claim may be false.

Inputs:
- session contract
- project contract
- git diff
- check outputs / evidence

Task:
Try to falsify the done condition.

Check:
1. Every acceptance criterion.
2. Every invariant.
3. Blast radius: changed files must match the contract.
4. Tests: would the tests fail if the core behavior were broken?
5. Edge cases: empty input, malformed input, max size, concurrency, retries, rollback.
6. Security: authorization bypass, injection, data leaks, unsafe shell/file/network behavior.
7. Claims: every "done" claim must be supported by command output or code evidence.

Output:
- Disproven claims
- Unsupported claims
- Strongest counterexample
- Verdict: PASS or FAIL

