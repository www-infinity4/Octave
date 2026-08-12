const assert = require("node:assert/strict");
const crypto = require("node:crypto").webcrypto;
const values = new Map();
global.window = global;
global.crypto = crypto;
global.localStorage = {
  getItem: key => values.has(key) ? values.get(key) : null,
  setItem: (key, value) => values.set(key, value),
};
global.fetch = async (url) => {
  if (String(url).endsWith("/v1/reason")) return { ok: true, json: async () => ({
    schema: "infinity/reason-result/v1", role: "REASONER", model: "fake-gemma",
    output: "Local synthesis", evidenceState: "INFERRED",
  }) };
  return { ok: true, json: async () => ({
    proposal: { name: "token.engineer", arguments: {} }, executed: false,
    requiresApplicationValidation: true,
  }) };
};
require("./research-runtime.js");

(async () => {
  const input = {
    query: "Hydrogen portal", projectBody: "Sourced project draft",
    discoveryBody: "Explore electron logic", tokenLineage: ["ICT-A", "ICT-B"],
    userPath: ["hydrogen", "electron"],
    sources: [{ src: "Wikidata", title: "Hydrogen", url: "https://www.wikidata.org/wiki/Q556" }],
  };
  const first = await OctaveResearchRuntime.buildRecord(input);
  assert.equal(first.evidenceLevel, "INFERRED");
  assert.equal(first.runtime.evidenceLevel, "INFERRED");
  assert.equal(first.runtime.model, "fake-gemma");
  assert.equal(first.sources[0].evidenceLevel, "EXTERNALLY_VERIFIED");
  for (const field of ["queryHash", "sourceSetHash", "articleHash", "tokenLineageHash", "userPathHash"]) {
    assert.match(first.novelty[field], /^[a-f0-9]{64}$/);
  }
  const repeated = await OctaveResearchRuntime.buildRecord(input);
  assert.equal(repeated.novelty.status, "DUPLICATE");
  assert.equal(repeated.novelty.duplicateOf, first.recordId);
  const action = await OctaveResearchRuntime.proposeAction("GREEN", "A", "B");
  assert.equal(action.proposal.name, "token.engineer");
  assert.equal(action.executed, false);
  console.log("Octave shared research runtime: PASS");
})().catch(error => { console.error(error); process.exitCode = 1; });
