/* Octave adapter for the shared local Infinity research runtime. */
(function (global) {
  "use strict";

  const CATALOG_KEY = "octave.research.records.v1";
  const BASE_URL = String(global.INFINITY_AI_BASE_URL || "http://127.0.0.1:11435").replace(/\/$/, "");

  function normalize(value) {
    return String(value == null ? "" : value).normalize("NFKC").toLowerCase().replace(/\s+/g, " ").trim();
  }

  function stable(value) {
    if (Array.isArray(value)) return value.map(stable);
    if (value && typeof value === "object") {
      return Object.keys(value).sort().reduce((result, key) => {
        result[key] = stable(value[key]);
        return result;
      }, {});
    }
    return value;
  }

  async function sha256(value) {
    const encoded = new TextEncoder().encode(JSON.stringify(stable(value)));
    const digest = await global.crypto.subtle.digest("SHA-256", encoded);
    return Array.from(new Uint8Array(digest), byte => byte.toString(16).padStart(2, "0")).join("");
  }

  function timeoutSignal(ms) {
    if (global.AbortSignal && typeof global.AbortSignal.timeout === "function") return global.AbortSignal.timeout(ms);
    const controller = new AbortController();
    global.setTimeout(() => controller.abort(), ms);
    return controller.signal;
  }

  async function post(path, payload) {
    const response = await global.fetch(BASE_URL + path, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
      signal: timeoutSignal(1800),
    });
    if (!response.ok) throw new Error("Infinity AI " + response.status);
    return response.json();
  }

  async function reason(record) {
    try {
      const result = await post("/v1/reason", {
        input: "Write a concise synthesis and next research step from the supplied source records. Keep model prose INFERRED. Do not claim full-text review or external verification beyond the supplied URLs.",
        context: record,
      });
      if (result.schema !== "infinity/reason-result/v1" || result.role !== "REASONER" ||
          result.evidenceState !== "INFERRED" || typeof result.output !== "string") {
        throw new Error("invalid REASONER evidence contract");
      }
      return { status: "READY", output: result.output, model: result.model || "local", evidenceLevel: "INFERRED" };
    } catch (error) {
      return { status: "OFFLINE_FALLBACK", output: null, model: null, evidenceLevel: "INFERRED", error: error.message };
    }
  }

  async function proposeAction(lane, source, targetQuery) {
    const names = {
      GREEN: "token.engineer", BLUE: "token.import", YELLOW: "research.expand_token",
      ORANGE: "research.expand_token", RED: "token.route", PURPLE: "research.expand_token",
    };
    try {
      const result = await post("/v1/tools", {
        input: lane + " action from " + source + " toward " + targetQuery,
        tools: [{ name: names[lane], description: "Propose the selected Octave color action" }],
        context: { lane, source, targetQuery },
      });
      if (result.executed !== false || !result.proposal) throw new Error("TOOL_ROUTER executed or returned no proposal");
      return { status: "READY", proposal: result.proposal, executed: false, requiresApplicationValidation: true };
    } catch (error) {
      return { status: "OFFLINE_FALLBACK", proposal: { name: names[lane], arguments: { source, targetQuery } }, executed: false, requiresApplicationValidation: true, error: error.message };
    }
  }

  function catalog() {
    try {
      const value = JSON.parse(global.localStorage.getItem(CATALOG_KEY) || "[]");
      return Array.isArray(value) ? value : [];
    } catch (_) {
      return [];
    }
  }

  async function buildRecord(input) {
    const sourceSet = (input.sources || []).map(source => normalize(source.url)).filter(Boolean).sort();
    const article = {
      query: normalize(input.query), project: input.projectBody,
      discovery: input.discoveryBody, sources: sourceSet,
    };
    const novelty = {
      schema: "infinity/research-novelty/v1",
      queryHash: await sha256(normalize(input.query)),
      sourceSetHash: sourceSet.length ? await sha256(sourceSet) : null,
      articleHash: await sha256(article),
      tokenLineageHash: await sha256((input.tokenLineage || []).map(normalize)),
      userPathHash: await sha256((input.userPath || []).map(normalize)),
      status: "UNIQUE", duplicateOf: null, matchedOn: null,
    };
    const previous = catalog();
    const fields = ["queryHash", "sourceSetHash", "articleHash"];
    const duplicate = previous.find(item => fields.some(field => novelty[field] && item.novelty[field] === novelty[field]));
    if (duplicate) {
      novelty.status = "DUPLICATE";
      novelty.duplicateOf = duplicate.recordId;
      novelty.matchedOn = fields.find(field => novelty[field] && duplicate.novelty[field] === novelty[field]);
    }
    const record = {
      schema: "infinity/research-record/v1",
      recordId: "octave-" + novelty.articleHash.slice(0, 16),
      streamType: "PROJECT_RESEARCH",
      evidenceLevel: "INFERRED",
      query: input.query,
      projectBody: input.projectBody,
      discovery: { body: input.discoveryBody, evidenceLevel: "INFERRED", relationshipStatus: "EXPLORATORY_LINK" },
      sources: (input.sources || []).map(source => ({
        title: source.title, url: source.url, provider: source.src,
        evidenceLevel: source.url ? "EXTERNALLY_VERIFIED" : "OBSERVED",
        fullTextReviewed: false,
      })),
      novelty,
    };
    record.runtime = await reason(record);
    try {
      previous.unshift(record);
      global.localStorage.setItem(CATALOG_KEY, JSON.stringify(previous.slice(0, 500)));
    } catch (_) {
      // The record remains usable/exportable when storage is disabled.
    }
    return record;
  }

  global.OctaveResearchRuntime = { buildRecord, proposeAction, sha256 };
})(window);
