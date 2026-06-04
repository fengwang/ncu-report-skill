Review the current diff against the session contract.

Use independent review axes:
- Correctness: logic errors, edge cases, exceptions, spec adherence.
- Security/safety: injection, authz/authn, secrets, unsafe file/process/network behavior.
- Tests: missing regression tests, tautological tests, weak assertions, hidden untested branches.
- Architecture: coupling, ownership boundaries, naming, module responsibilities.
- Performance: complexity, resource leaks, hot paths, unnecessary IO.

Each finding must include:
- severity
- file:line or exact evidence
- violated contract clause or invariant
- impact
- smallest safe fix
- confidence

Return only actionable findings. Do not include style nits unless they block maintainability.
Deduplicate overlap.
Do not drop a Critical/High issue just because only one reviewer found it, if evidence is concrete.

