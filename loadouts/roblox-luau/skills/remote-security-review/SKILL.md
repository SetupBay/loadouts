---
name: remote-security-review
description: Audit a Roblox game's RemoteEvents and RemoteFunctions for exploitable client trust. Use before publishing, after adding remotes, or when players report exploits like infinite money or teleporting.
---

# Remote security review

## 1. Inventory
- Find every remote: search for `RemoteEvent`, `RemoteFunction`, `UnreliableRemoteEvent` instances in the Rojo project files
  (`*.model.json`, `*.project.json`, `.rbxmx`) and in code (`Instance.new("RemoteEvent")`).
- Find every handler: `OnServerEvent`, `OnServerInvoke`, and on the client `FireServer`/`InvokeServer` calls.
- Build a table: remote name → server handler file → client call sites → arguments sent.

## 2. Review each handler
For each remote, answer:
1. **What does the client claim?** List each argument. Would an exploiter gain anything by changing it?
2. **Types checked?** Every argument `typeof`-checked, strings length-limited, numbers bounded and NaN-rejected, Instances checked
   to be the expected class and in an expected place.
3. **Authority:** does the server compute the outcome, or trust a client value (amount, damage, price, position, target)?
4. **Permission/state:** does it check ownership, cost, distance (`(char.HumanoidRootPart.Position - target.Position).Magnitude`),
   cooldown, round state?
5. **Rate limiting:** can it be spammed? What happens if it is fired 1,000 times a second?
6. **Errors:** can bad input throw and break the handler for everyone, or leave state half-updated?
7. **RemoteFunctions:** never `InvokeClient`. `OnServerInvoke` returns quickly and never yields on client data.

## 3. Also check
- Server-only modules are not in `ReplicatedStorage` (secrets, admin lists, prices that should be hidden).
- No `loadstring`, no `require` of asset IDs you do not control.
- Admin commands check a server-side list of `UserId`s (not names, which can change).
- Clients are not given network ownership of things that matter (e.g. other players' parts, shop NPCs).

## 4. Report
```
Remote review — <place> — <n> remotes
[Critical] AddCoins (src/server/Economy.server.luau:42) — trusts `amount` from the client. Any exploiter can grant themselves unlimited coins.
  Fix: remove the remote; award coins on the server when the qualifying event happens.
[High] Attack — no distance check or cooldown. Fix: check range ≤ weapon reach and a per-player cooldown.
[OK] RequestRespawn — no arguments, cooldown present.
```
Order by severity. Offer to write the fixes, one remote at a time.
